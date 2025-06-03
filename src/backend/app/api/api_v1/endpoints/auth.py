"""
Authentication and user management API routes
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    SecurityManager, 
    security, 
    verify_refresh_token,
    get_current_user_token
)
from app.core.deps import get_current_user, get_current_active_user
from app.models.user import User
from app.schemas.auth import (
    Token, 
    TokenData, 
    UserLogin, 
    UserRegister, 
    PasswordReset,
    PasswordChange
)
from app.schemas.user import UserCreate, UserInDB, UserResponse
from app.services.user_service import UserService


router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, message = SecurityManager.validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Create user
    user_service = UserService(db)
    user_create = UserCreate(
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    user = user_service.create_user(user_create)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login user and return JWT tokens
    """
    # Authenticate user
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not SecurityManager.verify_password(
        user_credentials.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = SecurityManager.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = SecurityManager.create_refresh_token(subject=user.id)
    
    # Update last login
    user_service = UserService(db)
    user_service.update_last_login(user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    # Extract refresh token
    refresh_token = get_current_user_token(credentials)
    
    # Verify refresh token
    user_id = verify_refresh_token(refresh_token)
    
    # Check if user still exists and is active
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = SecurityManager.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    new_refresh_token = SecurityManager.create_refresh_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Logout user (client should discard tokens)
    """
    # In a production system, you might want to maintain a blacklist
    # of revoked tokens. For now, we rely on client-side token removal.
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get current user information
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user information
    """
    user_service = UserService(db)
    
    # Update user (excluding password)
    update_data = user_update.model_dump(exclude={"password"})
    updated_user = user_service.update_user(current_user.id, update_data)
    
    return UserResponse.model_validate(updated_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change user password
    """
    # Verify current password
    user = db.query(User).filter(User.id == current_user.id).first()
    if not SecurityManager.verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    is_valid, message = SecurityManager.validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Update password
    user_service = UserService(db)
    user_service.change_password(current_user.id, password_data.new_password)
    
    return {"message": "Password changed successfully"}


@router.post("/request-password-reset")
async def request_password_reset(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request password reset (generates reset token)
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = SecurityManager.generate_password_reset_token()
    
    user_service = UserService(db)
    user_service.set_password_reset_token(user.id, reset_token)
    
    # In a real application, send email with reset link
    # For demo purposes, we'll return the token (remove in production)
    return {
        "message": "Password reset token generated",
        "reset_token": reset_token  # Remove in production
    }


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset password using reset token
    """
    # Find user with reset token
    user = db.query(User).filter(
        User.password_reset_token == reset_data.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Validate new password
    is_valid, message = SecurityManager.validate_password_strength(reset_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Reset password
    user_service = UserService(db)
    user_service.reset_password(user.id, reset_data.new_password)
    
    return {"message": "Password reset successfully"}


@router.get("/token/verify")
async def verify_token(
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Verify if current token is valid
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email
    }

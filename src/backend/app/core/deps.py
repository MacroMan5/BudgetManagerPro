"""
Authentication dependencies for FastAPI endpoints
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import security, verify_access_token, get_current_user_token
from app.models.user import User
from app.schemas.user import UserInDB


async def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """
    Dependency to get current authenticated user
    """
    # Extract token from credentials
    token = get_current_user_token(credentials)
    
    # Verify token and get user ID
    user_id = verify_access_token(token)
    
    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserInDB.model_validate(user)


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Dependency to get current active user (additional check)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Dependency to get current superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_permissions(*required_permissions: str):
    """
    Decorator factory for permission-based access control
    Usage: @require_permissions("accounts:read", "transactions:write")
    """
    def permission_dependency(
        current_user: UserInDB = Depends(get_current_user)
    ) -> UserInDB:
        # Check if user has required permissions
        user_permissions = getattr(current_user, 'permissions', [])
        
        missing_permissions = [
            perm for perm in required_permissions 
            if perm not in user_permissions
        ]
        
        if missing_permissions and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing_permissions)}"
            )
        
        return current_user
    
    return permission_dependency


class RoleChecker:
    """
    Role-based access control checker
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if current_user.role not in self.allowed_roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        return current_user


# Common role checkers
require_admin = RoleChecker(["admin"])
require_user_or_admin = RoleChecker(["user", "admin"])


def get_optional_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserInDB]:
    """
    Optional user dependency - returns None if no valid authentication
    Useful for endpoints that work for both authenticated and anonymous users
    """
    if not credentials:
        return None
    
    try:
        token = get_current_user_token(credentials)
        user_id = verify_access_token(token)
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if user and user.is_active:
            return UserInDB.model_validate(user)
    except:
        pass  # Silent fail for optional authentication
    
    return None


def check_account_access(account_id: int):
    """
    Dependency factory to check if user has access to specific account
    """
    def account_access_checker(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> UserInDB:
        from app.models.account import Account
        
        # Check if account belongs to user
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == current_user.id
        ).first()
        
        if not account and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account"
            )
        
        return current_user
    
    return account_access_checker


def check_transaction_access(transaction_id: int):
    """
    Dependency factory to check if user has access to specific transaction
    """
    def transaction_access_checker(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> UserInDB:
        from app.models.transaction import Transaction
        from app.models.account import Account
        
        # Check if transaction belongs to user's account
        transaction = db.query(Transaction).join(Account).filter(
            Transaction.id == transaction_id,
            Account.user_id == current_user.id
        ).first()
        
        if not transaction and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this transaction"
            )
        
        return current_user
    
    return transaction_access_checker

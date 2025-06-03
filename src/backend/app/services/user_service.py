"""
User service for business logic operations
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import SecurityManager
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """User business logic service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user"""
        # Hash password
        password_hash = SecurityManager.get_password_hash(user_create.password)
        
        # Create user instance
        db_user = User(
            email=user_create.email,
            password_hash=password_hash,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, user_update: Dict[str, Any]) -> User:
        """Update user information"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        for field, value in user_update.items():
            if hasattr(db_user, field) and value is not None:
                setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def change_password(self, user_id: int, new_password: str) -> User:
        """Change user password"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        password_hash = SecurityManager.get_password_hash(new_password)
        db_user.password_hash = password_hash
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def set_password_reset_token(self, user_id: int, reset_token: str) -> User:
        """Set password reset token for user"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.password_reset_token = reset_token
        db_user.password_reset_expires = datetime.utcnow().replace(
            hour=datetime.utcnow().hour + 1  # Token expires in 1 hour
        )
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def reset_password(self, user_id: int, new_password: str) -> User:
        """Reset user password and clear reset token"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        password_hash = SecurityManager.get_password_hash(new_password)
        db_user.password_hash = password_hash
        
        # Clear reset token
        db_user.password_reset_token = None
        db_user.password_reset_expires = None
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_last_login(self, user_id: int) -> User:
        """Update user's last login timestamp"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.last_login = datetime.utcnow()
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def deactivate_user(self, user_id: int) -> User:
        """Deactivate user account"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def activate_user(self, user_id: int) -> User:
        """Activate user account"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.is_active = True
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

"""
Models package - Import all models here to ensure SQLAlchemy sees them during table creation
"""

# Import all models to register them with SQLAlchemy
from app.models.user import User
from app.models.account import Account, AccountType

# Export all models and enums
__all__ = [
    "User",
    "Account", 
    "AccountType",
]

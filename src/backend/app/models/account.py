"""
Account model for database operations
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class AccountType(str, Enum):
    """Account type enumeration"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    MORTGAGE = "mortgage"
    LINE_OF_CREDIT = "line_of_credit"


class Account(Base):
    """Account model"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    bank_name = Column(String(255), nullable=True)
    account_number = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
      # Relationships
    user = relationship("User", back_populates="accounts")    # TODO: Implement Transaction model
    # transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    # TODO: Implement Balance model  
    # balances = relationship("Balance", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', type='{self.account_type.value}', user_id={self.user_id})>"
    
    @property
    def display_name(self) -> str:
        """Get account's display name with bank info if available"""
        if self.bank_name:
            return f"{self.name} ({self.bank_name})"
        return self.name
    
    @property
    def masked_account_number(self) -> str:
        """Get masked account number for security"""
        if not self.account_number:
            return ""
        if len(self.account_number) <= 4:
            return self.account_number
        return f"****{self.account_number[-4:]}"

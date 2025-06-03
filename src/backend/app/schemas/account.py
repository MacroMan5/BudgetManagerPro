"""
Account schemas for API requests and responses
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.account import AccountType


class AccountBase(BaseModel):
    """Base account schema"""
    name: str = Field(..., min_length=1, max_length=255)
    account_type: AccountType
    bank_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class AccountCreate(AccountBase):
    """Account creation schema"""
    pass


class AccountUpdate(BaseModel):
    """Account update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    account_type: Optional[AccountType] = None
    bank_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AccountInDB(AccountBase):
    """Account schema with database fields"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountResponse(AccountBase):
    """Account response schema (safe fields only)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    masked_account_number: str
    display_name: str
    
    class Config:
        from_attributes = True


class AccountSummary(BaseModel):
    """Account summary schema for lists"""
    id: int
    name: str
    account_type: AccountType
    bank_name: Optional[str] = None
    is_active: bool
    masked_account_number: str
    display_name: str
    
    class Config:
        from_attributes = True


class AccountStats(BaseModel):
    """Account statistics schema"""
    id: int
    name: str
    account_type: AccountType
    current_balance: Optional[float] = None
    transaction_count: int = 0
    last_transaction_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

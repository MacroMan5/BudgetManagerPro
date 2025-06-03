"""
Account service for business logic operations
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.account import Account, AccountType
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountStats


class AccountService:
    """Account business logic service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_account(self, account_data: AccountCreate, user_id: int) -> Account:
        """Create a new account for user"""
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check for duplicate account name for this user
        existing_account = self.db.query(Account).filter(
            Account.user_id == user_id,
            Account.name == account_data.name,
            Account.is_active == True
        ).first()
        
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account with name '{account_data.name}' already exists"
            )
        
        # Create new account
        db_account = Account(
            user_id=user_id,
            name=account_data.name,
            account_type=account_data.account_type,
            bank_name=account_data.bank_name,
            account_number=account_data.account_number,
            description=account_data.description
        )
        
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        
        return db_account
    
    def get_account(self, account_id: int, user_id: int) -> Optional[Account]:
        """Get account by ID for specific user"""
        return self.db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == user_id
        ).first()
    
    def get_accounts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        account_type: Optional[AccountType] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Account]:
        """Get all accounts for user with optional filtering"""
        query = self.db.query(Account).filter(Account.user_id == user_id)
        
        # Apply filters
        if account_type:
            query = query.filter(Account.account_type == account_type)
        
        if is_active is not None:
            query = query.filter(Account.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Account.name.ilike(search_term)) |
                (Account.bank_name.ilike(search_term)) |
                (Account.description.ilike(search_term))
            )
        
        return query.order_by(Account.name).offset(skip).limit(limit).all()
    
    def get_accounts_count(
        self,
        user_id: int,
        account_type: Optional[AccountType] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """Get total count of accounts for user with optional filtering"""
        query = self.db.query(Account).filter(Account.user_id == user_id)
        
        # Apply same filters as get_accounts
        if account_type:
            query = query.filter(Account.account_type == account_type)
        
        if is_active is not None:
            query = query.filter(Account.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Account.name.ilike(search_term)) |
                (Account.bank_name.ilike(search_term)) |
                (Account.description.ilike(search_term))
            )
        
        return query.count()
    
    def update_account(
        self,
        account_id: int,
        account_data: AccountUpdate,
        user_id: int
    ) -> Optional[Account]:
        """Update account"""
        account = self.get_account(account_id, user_id)
        if not account:
            return None
        
        # Check for duplicate name if name is being changed
        if account_data.name and account_data.name != account.name:
            existing_account = self.db.query(Account).filter(
                Account.user_id == user_id,
                Account.name == account_data.name,
                Account.is_active == True,
                Account.id != account_id
            ).first()
            
            if existing_account:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Account with name '{account_data.name}' already exists"
                )
        
        # Update fields
        update_data = account_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)
        
        account.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def delete_account(self, account_id: int, user_id: int) -> bool:
        """Soft delete account (set is_active to False)"""
        account = self.get_account(account_id, user_id)
        if not account:
            return False
        
        # Check if account has transactions
        # This should be implemented when Transaction model is ready
        # For now, we'll just soft delete
        
        account.is_active = False
        account.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def hard_delete_account(self, account_id: int, user_id: int) -> bool:
        """Permanently delete account and all related data"""
        account = self.get_account(account_id, user_id)
        if not account:
            return False
        
        # This will cascade delete all related transactions and balances
        self.db.delete(account)
        self.db.commit()
        
        return True
    
    def get_account_stats(self, user_id: int) -> List[AccountStats]:
        """Get statistics for all user accounts"""
        # This will be fully implemented when Transaction model is ready
        accounts = self.get_accounts(user_id, is_active=True)
        
        stats = []
        for account in accounts:
            stat = AccountStats(
                id=account.id,
                name=account.name,
                account_type=account.account_type,
                current_balance=0.0,  # Will be calculated from transactions
                transaction_count=0,  # Will be calculated from transactions
                last_transaction_date=None  # Will be calculated from transactions
            )
            stats.append(stat)
        
        return stats
    
    def get_account_types(self) -> Dict[str, str]:
        """Get all available account types"""
        return {
            AccountType.CHECKING: "Checking Account",
            AccountType.SAVINGS: "Savings Account", 
            AccountType.CREDIT_CARD: "Credit Card",
            AccountType.MORTGAGE: "Mortgage",
            AccountType.LINE_OF_CREDIT: "Line of Credit"
        }

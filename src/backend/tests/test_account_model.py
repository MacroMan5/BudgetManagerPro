"""
Test cases for Account model
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.account import Account, AccountType
from app.models.user import User


class TestAccountModel:
    """Test Account model functionality"""
    
    def test_create_account(self, db_session: Session, test_user: User):
        """Test account creation"""
        account = Account(
            user_id=test_user.id,
            name="Test Checking",
            account_type=AccountType.CHECKING,
            bank_name="Test Bank",
            account_number="1234567890",
            description="Test checking account"
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        assert account.id is not None
        assert account.user_id == test_user.id
        assert account.name == "Test Checking"
        assert account.account_type == AccountType.CHECKING
        assert account.bank_name == "Test Bank"
        assert account.account_number == "1234567890"
        assert account.description == "Test checking account"
        assert account.is_active is True
        assert account.created_at is not None
        assert account.updated_at is not None
    
    def test_account_default_values(self, db_session: Session, test_user: User):
        """Test account default values"""
        account = Account(
            user_id=test_user.id,
            name="Minimal Account",
            account_type=AccountType.SAVINGS
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        assert account.is_active is True
        assert account.bank_name is None
        assert account.account_number is None
        assert account.description is None
        assert account.created_at is not None
        assert account.updated_at is not None
    
    def test_account_type_enum(self, db_session: Session, test_user: User):
        """Test all account types"""
        account_types = [
            AccountType.CHECKING,
            AccountType.SAVINGS, 
            AccountType.CREDIT_CARD,
            AccountType.MORTGAGE,
            AccountType.LINE_OF_CREDIT
        ]
        
        for account_type in account_types:
            account = Account(
                user_id=test_user.id,
                name=f"Test {account_type.value}",
                account_type=account_type
            )
            
            db_session.add(account)
            db_session.commit()
            db_session.refresh(account)
            
            assert account.account_type == account_type
            
    def test_display_name_property(self, db_session: Session, test_user: User):
        """Test display_name property"""
        # Account with bank name
        account_with_bank = Account(
            user_id=test_user.id,
            name="My Checking",
            account_type=AccountType.CHECKING,
            bank_name="Test Bank"
        )
        
        db_session.add(account_with_bank)
        db_session.commit()
        
        assert account_with_bank.display_name == "My Checking (Test Bank)"
        
        # Account without bank name
        account_without_bank = Account(
            user_id=test_user.id,
            name="My Savings",
            account_type=AccountType.SAVINGS
        )
        
        db_session.add(account_without_bank)
        db_session.commit()
        
        assert account_without_bank.display_name == "My Savings"
    
    def test_masked_account_number_property(self, db_session: Session, test_user: User):
        """Test masked_account_number property"""
        # Long account number
        account_long = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING,
            account_number="1234567890123456"
        )
        
        assert account_long.masked_account_number == "****3456"
        
        # Short account number
        account_short = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING,
            account_number="123"
        )
        
        assert account_short.masked_account_number == "123"
        
        # No account number
        account_no_number = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING,
            account_number=None
        )
        
        assert account_no_number.masked_account_number == ""
        
        # Empty account number
        account_empty = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING,
            account_number=""
        )
        
        assert account_empty.masked_account_number == ""
    
    def test_account_repr(self, db_session: Session, test_user: User):
        """Test account string representation"""
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        expected_repr = f"<Account(id={account.id}, name='Test Account', type='checking', user_id={test_user.id})>"
        assert repr(account) == expected_repr
    
    def test_account_user_relationship(self, db_session: Session, test_user: User):
        """Test relationship with User model"""
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        # Test relationship from account to user
        assert account.user == test_user
        assert account.user.id == test_user.id
        
        # Test relationship from user to accounts
        db_session.refresh(test_user)
        assert account in test_user.accounts
    
    def test_account_cascade_delete(self, db_session: Session, test_user: User):
        """Test that accounts are deleted when user is deleted"""
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING
        )
        
        db_session.add(account)
        db_session.commit()
        
        account_id = account.id
        
        # Delete user should cascade to accounts
        db_session.delete(test_user)
        db_session.commit()
        
        # Account should no longer exist
        deleted_account = db_session.query(Account).filter(Account.id == account_id).first()
        assert deleted_account is None

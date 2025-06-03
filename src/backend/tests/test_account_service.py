"""
Test cases for Account service
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.account import Account, AccountType
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate
from app.services.account_service import AccountService


class TestAccountService:
    """Test Account service functionality"""
    
    def test_create_account_success(self, db_session: Session, test_user: User):
        """Test successful account creation"""
        service = AccountService(db_session)
        
        account_data = AccountCreate(
            name="Test Checking",
            account_type=AccountType.CHECKING,
            bank_name="Test Bank",
            account_number="1234567890",
            description="Test checking account"
        )
        
        account = service.create_account(account_data, test_user.id)
        
        assert account.id is not None
        assert account.user_id == test_user.id
        assert account.name == "Test Checking"
        assert account.account_type == AccountType.CHECKING
        assert account.bank_name == "Test Bank"
        assert account.account_number == "1234567890"
        assert account.description == "Test checking account"
        assert account.is_active is True
    
    def test_create_account_user_not_found(self, db_session: Session):
        """Test account creation with non-existent user"""
        service = AccountService(db_session)
        
        account_data = AccountCreate(
            name="Test Account",
            account_type=AccountType.CHECKING
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_account(account_data, 99999)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)
    
    def test_create_duplicate_account_name(self, db_session: Session, test_user: User):
        """Test creating account with duplicate name"""
        service = AccountService(db_session)
        
        # Create first account
        account_data = AccountCreate(
            name="Duplicate Name",
            account_type=AccountType.CHECKING
        )
        
        service.create_account(account_data, test_user.id)
        
        # Try to create account with same name
        with pytest.raises(HTTPException) as exc_info:
            service.create_account(account_data, test_user.id)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail)
    
    def test_get_account_success(self, db_session: Session, test_user: User):
        """Test getting account by ID"""
        service = AccountService(db_session)
        
        # Create account
        account_data = AccountCreate(
            name="Test Account",
            account_type=AccountType.SAVINGS
        )
        
        created_account = service.create_account(account_data, test_user.id)
        
        # Get account
        retrieved_account = service.get_account(created_account.id, test_user.id)
        
        assert retrieved_account is not None
        assert retrieved_account.id == created_account.id
        assert retrieved_account.name == "Test Account"
    
    def test_get_account_not_found(self, db_session: Session, test_user: User):
        """Test getting non-existent account"""
        service = AccountService(db_session)
        
        account = service.get_account(99999, test_user.id)
        assert account is None
    
    def test_get_account_wrong_user(self, db_session: Session, test_user: User, test_superuser: User):
        """Test getting account from different user"""
        service = AccountService(db_session)
        
        # Create account for test_user
        account_data = AccountCreate(
            name="Test Account",
            account_type=AccountType.CHECKING
        )
        
        created_account = service.create_account(account_data, test_user.id)
        
        # Try to get account as different user
        retrieved_account = service.get_account(created_account.id, test_superuser.id)
        assert retrieved_account is None
    
    def test_get_accounts_all(self, db_session: Session, test_user: User):
        """Test getting all accounts for user"""
        service = AccountService(db_session)
        
        # Create multiple accounts
        accounts_data = [
            AccountCreate(name="Account 1", account_type=AccountType.CHECKING),
            AccountCreate(name="Account 2", account_type=AccountType.SAVINGS),
            AccountCreate(name="Account 3", account_type=AccountType.CREDIT_CARD),
        ]
        
        for account_data in accounts_data:
            service.create_account(account_data, test_user.id)
        
        # Get all accounts
        accounts = service.get_accounts(test_user.id)
        
        assert len(accounts) == 3
        account_names = [acc.name for acc in accounts]
        assert "Account 1" in account_names
        assert "Account 2" in account_names
        assert "Account 3" in account_names
    
    def test_get_accounts_with_pagination(self, db_session: Session, test_user: User):
        """Test getting accounts with pagination"""
        service = AccountService(db_session)
        
        # Create multiple accounts
        for i in range(5):
            account_data = AccountCreate(
                name=f"Account {i+1}",
                account_type=AccountType.CHECKING
            )
            service.create_account(account_data, test_user.id)
        
        # Test pagination
        first_page = service.get_accounts(test_user.id, skip=0, limit=2)
        assert len(first_page) == 2
        
        second_page = service.get_accounts(test_user.id, skip=2, limit=2)
        assert len(second_page) == 2
        
        third_page = service.get_accounts(test_user.id, skip=4, limit=2)
        assert len(third_page) == 1
    
    def test_get_accounts_filter_by_type(self, db_session: Session, test_user: User):
        """Test filtering accounts by type"""
        service = AccountService(db_session)
        
        # Create accounts of different types
        accounts_data = [
            AccountCreate(name="Checking 1", account_type=AccountType.CHECKING),
            AccountCreate(name="Checking 2", account_type=AccountType.CHECKING),
            AccountCreate(name="Savings 1", account_type=AccountType.SAVINGS),
        ]
        
        for account_data in accounts_data:
            service.create_account(account_data, test_user.id)
        
        # Filter by checking accounts
        checking_accounts = service.get_accounts(test_user.id, account_type=AccountType.CHECKING)
        assert len(checking_accounts) == 2
        
        # Filter by savings accounts
        savings_accounts = service.get_accounts(test_user.id, account_type=AccountType.SAVINGS)
        assert len(savings_accounts) == 1
    
    def test_get_accounts_filter_by_active_status(self, db_session: Session, test_user: User):
        """Test filtering accounts by active status"""
        service = AccountService(db_session)
        
        # Create accounts
        account_data1 = AccountCreate(name="Active Account", account_type=AccountType.CHECKING)
        account_data2 = AccountCreate(name="Inactive Account", account_type=AccountType.SAVINGS)
        
        account1 = service.create_account(account_data1, test_user.id)
        account2 = service.create_account(account_data2, test_user.id)
        
        # Deactivate second account
        service.delete_account(account2.id, test_user.id)
        
        # Filter by active accounts
        active_accounts = service.get_accounts(test_user.id, is_active=True)
        assert len(active_accounts) == 1
        assert active_accounts[0].name == "Active Account"
        
        # Filter by inactive accounts
        inactive_accounts = service.get_accounts(test_user.id, is_active=False)
        assert len(inactive_accounts) == 1
        assert inactive_accounts[0].name == "Inactive Account"
    
    def test_get_accounts_search(self, db_session: Session, test_user: User):
        """Test searching accounts"""
        service = AccountService(db_session)
        
        # Create accounts
        accounts_data = [
            AccountCreate(name="My Checking", account_type=AccountType.CHECKING, bank_name="Test Bank"),
            AccountCreate(name="Emergency Fund", account_type=AccountType.SAVINGS, bank_name="Other Bank"),
            AccountCreate(name="Credit Card", account_type=AccountType.CREDIT_CARD, description="Main card"),
        ]
        
        for account_data in accounts_data:
            service.create_account(account_data, test_user.id)
        
        # Search by name
        results = service.get_accounts(test_user.id, search="checking")
        assert len(results) == 1
        assert results[0].name == "My Checking"
        
        # Search by bank name
        results = service.get_accounts(test_user.id, search="Test Bank")
        assert len(results) == 1
        assert results[0].name == "My Checking"
        
        # Search by description
        results = service.get_accounts(test_user.id, search="Main")
        assert len(results) == 1
        assert results[0].name == "Credit Card"
    
    def test_get_accounts_count(self, db_session: Session, test_user: User):
        """Test getting account count"""
        service = AccountService(db_session)
        
        # Initially no accounts
        count = service.get_accounts_count(test_user.id)
        assert count == 0
        
        # Create accounts
        for i in range(3):
            account_data = AccountCreate(
                name=f"Account {i+1}",
                account_type=AccountType.CHECKING
            )
            service.create_account(account_data, test_user.id)
        
        # Check count
        count = service.get_accounts_count(test_user.id)
        assert count == 3
        
        # Test count with filters
        count_checking = service.get_accounts_count(test_user.id, account_type=AccountType.CHECKING)
        assert count_checking == 3
        
        count_savings = service.get_accounts_count(test_user.id, account_type=AccountType.SAVINGS)
        assert count_savings == 0
    
    def test_update_account_success(self, db_session: Session, test_user: User):
        """Test successful account update"""
        service = AccountService(db_session)
        
        # Create account
        account_data = AccountCreate(
            name="Original Name",
            account_type=AccountType.CHECKING,
            bank_name="Original Bank"
        )
        
        account = service.create_account(account_data, test_user.id)
        
        # Update account
        update_data = AccountUpdate(
            name="Updated Name",
            bank_name="Updated Bank",
            description="Updated description"
        )
        
        updated_account = service.update_account(account.id, update_data, test_user.id)
        
        assert updated_account is not None
        assert updated_account.name == "Updated Name"
        assert updated_account.bank_name == "Updated Bank"
        assert updated_account.description == "Updated description"
        assert updated_account.account_type == AccountType.CHECKING  # Unchanged
    
    def test_update_account_not_found(self, db_session: Session, test_user: User):
        """Test updating non-existent account"""
        service = AccountService(db_session)
        
        update_data = AccountUpdate(name="New Name")
        
        result = service.update_account(99999, update_data, test_user.id)
        assert result is None
    
    def test_update_account_duplicate_name(self, db_session: Session, test_user: User):
        """Test updating account with duplicate name"""
        service = AccountService(db_session)
        
        # Create two accounts
        account_data1 = AccountCreate(name="Account 1", account_type=AccountType.CHECKING)
        account_data2 = AccountCreate(name="Account 2", account_type=AccountType.SAVINGS)
        
        account1 = service.create_account(account_data1, test_user.id)
        account2 = service.create_account(account_data2, test_user.id)
        
        # Try to update account2 to have same name as account1
        update_data = AccountUpdate(name="Account 1")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_account(account2.id, update_data, test_user.id)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail)
    
    def test_delete_account_soft(self, db_session: Session, test_user: User):
        """Test soft delete account"""
        service = AccountService(db_session)
        
        # Create account
        account_data = AccountCreate(name="Test Account", account_type=AccountType.CHECKING)
        account = service.create_account(account_data, test_user.id)
        
        # Soft delete account
        result = service.delete_account(account.id, test_user.id)
        assert result is True
        
        # Account should still exist but be inactive
        db_session.refresh(account)
        assert account.is_active is False
    
    def test_delete_account_not_found(self, db_session: Session, test_user: User):
        """Test deleting non-existent account"""
        service = AccountService(db_session)
        
        result = service.delete_account(99999, test_user.id)
        assert result is False
    
    def test_hard_delete_account(self, db_session: Session, test_user: User):
        """Test hard delete account"""
        service = AccountService(db_session)
        
        # Create account
        account_data = AccountCreate(name="Test Account", account_type=AccountType.CHECKING)
        account = service.create_account(account_data, test_user.id)
        account_id = account.id
        
        # Hard delete account
        result = service.hard_delete_account(account_id, test_user.id)
        assert result is True
        
        # Account should no longer exist
        deleted_account = db_session.query(Account).filter(Account.id == account_id).first()
        assert deleted_account is None
    
    def test_get_account_stats(self, db_session: Session, test_user: User):
        """Test getting account statistics"""
        service = AccountService(db_session)
        
        # Create accounts
        account_data1 = AccountCreate(name="Checking", account_type=AccountType.CHECKING)
        account_data2 = AccountCreate(name="Savings", account_type=AccountType.SAVINGS)
        
        account1 = service.create_account(account_data1, test_user.id)
        account2 = service.create_account(account_data2, test_user.id)
        
        # Get stats
        stats = service.get_account_stats(test_user.id)
        
        assert len(stats) == 2
        assert stats[0].name in ["Checking", "Savings"]
        assert stats[1].name in ["Checking", "Savings"]
        
        # Check stats structure
        for stat in stats:
            assert stat.id is not None
            assert stat.account_type in [AccountType.CHECKING, AccountType.SAVINGS]
            assert stat.current_balance == 0.0  # Default value
            assert stat.transaction_count == 0  # Default value
            assert stat.last_transaction_date is None  # Default value
    
    def test_get_account_types(self, db_session: Session):
        """Test getting available account types"""
        service = AccountService(db_session)
        
        account_types = service.get_account_types()
        
        assert len(account_types) == 5
        assert AccountType.CHECKING in account_types
        assert AccountType.SAVINGS in account_types
        assert AccountType.CREDIT_CARD in account_types
        assert AccountType.MORTGAGE in account_types
        assert AccountType.LINE_OF_CREDIT in account_types
        
        # Check descriptions
        assert account_types[AccountType.CHECKING] == "Checking Account"
        assert account_types[AccountType.SAVINGS] == "Savings Account"

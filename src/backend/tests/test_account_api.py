"""
Test cases for Account API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.account import Account, AccountType
from app.models.user import User


class TestAccountAPI:
    """Test Account API endpoints"""
    
    def test_create_account_success(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test successful account creation via API"""
        account_data = {
            "name": "Test Checking Account",
            "account_type": "checking",
            "bank_name": "Test Bank",
            "account_number": "1234567890",
            "description": "My primary checking account"
        }
        
        response = client.post(
            "/api/v1/accounts/",
            json=account_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Test Checking Account"
        assert data["account_type"] == "checking"
        assert data["bank_name"] == "Test Bank"
        assert data["description"] == "My primary checking account"
        assert data["is_active"] is True
        assert data["masked_account_number"] == "****7890"
        assert data["display_name"] == "Test Checking Account (Test Bank)"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_account_unauthorized(self, client: TestClient):
        """Test account creation without authentication"""
        account_data = {
            "name": "Test Account",
            "account_type": "checking"
        }
        
        response = client.post("/api/v1/accounts/", json=account_data)
        assert response.status_code == 401
    
    def test_create_account_invalid_data(self, client: TestClient, auth_headers: dict):
        """Test account creation with invalid data"""
        # Missing required fields
        response = client.post(
            "/api/v1/accounts/",
            json={"name": "Test"},
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # Invalid account type
        response = client.post(
            "/api/v1/accounts/",
            json={
                "name": "Test Account",
                "account_type": "invalid_type"
            },
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # Name too long
        response = client.post(
            "/api/v1/accounts/",
            json={
                "name": "x" * 256,  # Too long
                "account_type": "checking"
            },
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_get_accounts_empty(self, client: TestClient, auth_headers: dict):
        """Test getting accounts when none exist"""
        response = client.get("/api/v1/accounts/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_get_accounts_list(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test getting list of accounts"""
        # Create test accounts
        accounts = [
            Account(
                user_id=test_user.id,
                name="Checking Account",
                account_type=AccountType.CHECKING,
                bank_name="Test Bank"
            ),
            Account(
                user_id=test_user.id,
                name="Savings Account",
                account_type=AccountType.SAVINGS,
                bank_name="Other Bank"
            )
        ]
        
        for account in accounts:
            db_session.add(account)
        db_session.commit()
        
        response = client.get("/api/v1/accounts/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        account_names = [acc["name"] for acc in data]
        assert "Checking Account" in account_names
        assert "Savings Account" in account_names
    
    def test_get_accounts_pagination(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test account pagination"""
        # Create multiple accounts
        for i in range(5):
            account = Account(
                user_id=test_user.id,
                name=f"Account {i+1}",
                account_type=AccountType.CHECKING
            )
            db_session.add(account)
        db_session.commit()
        
        # Test first page
        response = client.get("/api/v1/accounts/?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Test second page
        response = client.get("/api/v1/accounts/?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Test third page
        response = client.get("/api/v1/accounts/?skip=4&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_accounts_filter_by_type(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test filtering accounts by type"""
        # Create accounts of different types
        accounts = [
            Account(user_id=test_user.id, name="Checking 1", account_type=AccountType.CHECKING),
            Account(user_id=test_user.id, name="Checking 2", account_type=AccountType.CHECKING),
            Account(user_id=test_user.id, name="Savings 1", account_type=AccountType.SAVINGS),
        ]
        
        for account in accounts:
            db_session.add(account)
        db_session.commit()
        
        # Filter by checking accounts
        response = client.get("/api/v1/accounts/?account_type=checking", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Filter by savings accounts
        response = client.get("/api/v1/accounts/?account_type=savings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_accounts_search(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test searching accounts"""
        # Create test accounts
        accounts = [
            Account(
                user_id=test_user.id,
                name="My Checking",
                account_type=AccountType.CHECKING,
                bank_name="Test Bank"
            ),
            Account(
                user_id=test_user.id,
                name="Emergency Fund",
                account_type=AccountType.SAVINGS,
                description="Emergency savings"
            )
        ]
        
        for account in accounts:
            db_session.add(account)
        db_session.commit()
        
        # Search by name
        response = client.get("/api/v1/accounts/?search=checking", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Checking"
        
        # Search by bank name
        response = client.get("/api/v1/accounts/?search=Test Bank", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Checking"
        
        # Search by description
        response = client.get("/api/v1/accounts/?search=Emergency", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Emergency Fund"
    
    def test_get_account_by_id_success(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test getting specific account by ID"""
        # Create test account
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING,
            bank_name="Test Bank",
            account_number="1234567890"
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        response = client.get(f"/api/v1/accounts/{account.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == account.id
        assert data["name"] == "Test Account"
        assert data["account_type"] == "checking"
        assert data["bank_name"] == "Test Bank"
        assert data["masked_account_number"] == "****7890"
        assert data["display_name"] == "Test Account (Test Bank)"
    
    def test_get_account_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent account"""
        response = client.get("/api/v1/accounts/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_account_wrong_user(self, client: TestClient, auth_headers: dict, superuser_headers: dict, test_user: User, db_session: Session):
        """Test getting account belonging to different user"""
        # Create account for test_user
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        # Try to access as superuser (different user)
        response = client.get(f"/api/v1/accounts/{account.id}", headers=superuser_headers)
        assert response.status_code == 404
    
    def test_update_account_success(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test successful account update"""
        # Create test account
        account = Account(
            user_id=test_user.id,
            name="Original Name",
            account_type=AccountType.CHECKING,
            bank_name="Original Bank"
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        # Update account
        update_data = {
            "name": "Updated Name",
            "bank_name": "Updated Bank",
            "description": "Updated description"
        }
        
        response = client.put(
            f"/api/v1/accounts/{account.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Name"
        assert data["bank_name"] == "Updated Bank"
        assert data["description"] == "Updated description"
        assert data["account_type"] == "checking"  # Unchanged
    
    def test_update_account_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating non-existent account"""
        update_data = {"name": "New Name"}
        
        response = client.put(
            "/api/v1/accounts/99999",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_delete_account_success(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test successful account deletion (soft delete)"""
        # Create test account
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        response = client.delete(f"/api/v1/accounts/{account.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Account deactivated successfully"
        
        # Verify account is deactivated
        db_session.refresh(account)
        assert account.is_active is False
    
    def test_delete_account_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting non-existent account"""
        response = client.delete("/api/v1/accounts/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_activate_account_success(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test activating deactivated account"""
        # Create and deactivate test account
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type=AccountType.CHECKING,
            is_active=False
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        response = client.patch(f"/api/v1/accounts/{account.id}/activate", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Account activated successfully"
        
        # Verify account is activated
        db_session.refresh(account)
        assert account.is_active is True
    
    def test_get_account_count(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test getting account count"""
        # Initially no accounts
        response = client.get("/api/v1/accounts/count", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        
        # Create some accounts
        for i in range(3):
            account = Account(
                user_id=test_user.id,
                name=f"Account {i+1}",
                account_type=AccountType.CHECKING
            )
            db_session.add(account)
        db_session.commit()
        
        # Check count
        response = client.get("/api/v1/accounts/count", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
    
    def test_get_account_stats(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test getting account statistics"""
        # Create test accounts
        accounts = [
            Account(user_id=test_user.id, name="Checking", account_type=AccountType.CHECKING),
            Account(user_id=test_user.id, name="Savings", account_type=AccountType.SAVINGS),
        ]
        
        for account in accounts:
            db_session.add(account)
        db_session.commit()
        
        response = client.get("/api/v1/accounts/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        
        for stat in data:
            assert "id" in stat
            assert "name" in stat
            assert "account_type" in stat
            assert "current_balance" in stat
            assert "transaction_count" in stat
            assert stat["current_balance"] == 0.0  # Default value
            assert stat["transaction_count"] == 0  # Default value
    
    def test_get_account_types(self, client: TestClient, auth_headers: dict):
        """Test getting available account types"""
        response = client.get("/api/v1/accounts/types", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        expected_types = ["checking", "savings", "credit_card", "mortgage", "line_of_credit"]
        assert len(data) == len(expected_types)
        
        for account_type in expected_types:
            assert account_type in data
            assert isinstance(data[account_type], str)  # Has description
    
    def test_user_isolation(self, client: TestClient, auth_headers: dict, superuser_headers: dict, test_user: User, test_superuser: User, db_session: Session):
        """Test that users can only access their own accounts"""
        # Create accounts for both users
        user_account = Account(
            user_id=test_user.id,
            name="User Account",
            account_type=AccountType.CHECKING
        )
        
        superuser_account = Account(
            user_id=test_superuser.id,
            name="Superuser Account",
            account_type=AccountType.SAVINGS
        )
        
        db_session.add(user_account)
        db_session.add(superuser_account)
        db_session.commit()
        
        # Test user can only see their account
        response = client.get("/api/v1/accounts/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "User Account"
        
        # Test superuser can only see their account
        response = client.get("/api/v1/accounts/", headers=superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Superuser Account"

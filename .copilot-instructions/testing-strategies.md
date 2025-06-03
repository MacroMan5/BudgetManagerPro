# Testing Context and Guidelines - BudgetManager Pro

## Project Overview
BudgetManager Pro is a secure multi-user personal finance web application with comprehensive testing strategies ensuring high code quality and reliability.

## Testing Architecture

### Testing Stack
- **Framework**: Pytest with asyncio support
- **Test Database**: SQLite in-memory for isolation
- **API Testing**: FastAPI TestClient with dependency injection
- **Coverage**: Aim for >95% test coverage
- **Test Types**: Unit, Integration, API, and End-to-End tests

### Current Test Structure
```
src/backend/tests/
├── conftest.py              # Test configuration and shared fixtures
├── test_auth.py            # Authentication endpoint tests
├── test_account_api.py     # Account API endpoint tests
├── test_account_service.py # Account service layer tests  
├── test_account_model.py   # Account model/database tests
├── test_user_model.py      # User model tests
├── test_user_service.py    # User service tests
└── test_transaction_*.py   # Transaction-related tests (to be added)
```

## Testing Patterns and Best Practices

### 1. Test Fixtures and Dependency Injection
```python
# Use dependency_overrides for clean test isolation
@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
```

### 2. User Authentication in Tests
```python
# Create authenticated test client
@pytest.fixture
def authenticated_client(test_db):
    # Create test user
    user_data = {"email": "test@example.com", "password": "TestPass123!"}
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login and get token
    response = client.post("/api/v1/auth/login", data=user_data)
    token = response.json()["access_token"]
    
    # Return client with authorization header
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
```

### 3. Database Isolation Patterns
```python
# Ensure unique data per test to prevent UNIQUE constraint failures
@pytest.fixture
def unique_user_data():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test-{unique_id}@example.com",
        "password": "TestPass123!",
        "full_name": f"Test User {unique_id}"
    }
```

### 4. API Testing Best Practices
```python
class TestAccountAPI:
    def test_create_account_success(self, authenticated_client, unique_account_data):
        """Test successful account creation"""
        response = authenticated_client.post("/api/v1/accounts/", json=unique_account_data)
        
        assert response.status_code == 201
        account = response.json()
        assert account["name"] == unique_account_data["name"]
        assert account["account_type"] == unique_account_data["account_type"]
        assert account["is_active"] is True
        assert "id" in account
        assert "created_at" in account
    
    def test_create_account_duplicate_name(self, authenticated_client, unique_account_data):
        """Test creating account with duplicate name fails"""
        # Create first account
        authenticated_client.post("/api/v1/accounts/", json=unique_account_data)
        
        # Try to create duplicate
        response = authenticated_client.post("/api/v1/accounts/", json=unique_account_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
```

### 5. Service Layer Testing
```python
class TestAccountService:
    def test_create_account(self, db_session, test_user):
        """Test account creation through service layer"""
        service = AccountService(db_session)
        account_data = AccountCreateSchema(
            name="Test Checking",
            account_type="checking",
            initial_balance=1000.00
        )
        
        account = service.create_account(account_data, test_user.id)
        
        assert account.name == "Test Checking"
        assert account.user_id == test_user.id
        assert account.balance == 1000.00
        assert account.is_active is True
```

### 6. Model/Database Testing
```python
class TestAccountModel:
    def test_account_creation(self, db_session, test_user):
        """Test Account model creation and validation"""
        account = Account(
            name="Test Account",
            account_type="savings",
            balance=500.00,
            user_id=test_user.id
        )
        
        db_session.add(account)
        db_session.commit()
        
        assert account.id is not None
        assert account.created_at is not None
        assert account.is_active is True
```

## Test Data Management

### 1. Factory Pattern for Test Data
```python
class AccountFactory:
    @staticmethod
    def create_account_data(name=None, account_type="checking"):
        unique_id = str(uuid.uuid4())[:8]
        return {
            "name": name or f"Test Account {unique_id}",
            "account_type": account_type,
            "initial_balance": 1000.00,
            "description": f"Test account created at {datetime.now()}"
        }
```

### 2. Realistic Test Data
```python
SAMPLE_TRANSACTIONS = [
    {"description": "Grocery Store", "amount": -85.50, "category": "Food"},
    {"description": "Salary Deposit", "amount": 3500.00, "category": "Income"},
    {"description": "Gas Station", "amount": -42.30, "category": "Transportation"}
]
```

## Error Testing Strategies

### 1. Authentication Errors
```python
def test_unauthorized_access(self, client):
    """Test endpoints require authentication"""
    response = client.get("/api/v1/accounts/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_invalid_token(self, client):
    """Test invalid JWT token handling"""
    client.headers.update({"Authorization": "Bearer invalid_token"})
    response = client.get("/api/v1/accounts/")
    assert response.status_code == 401
```

### 2. Validation Errors
```python
def test_invalid_account_data(self, authenticated_client):
    """Test account creation with invalid data"""
    invalid_data = {
        "name": "",  # Empty name
        "account_type": "invalid_type",  # Invalid type
        "initial_balance": -100  # Negative balance
    }
    
    response = authenticated_client.post("/api/v1/accounts/", json=invalid_data)
    assert response.status_code == 422
    
    errors = response.json()["detail"]
    assert any("name" in str(error) for error in errors)
    assert any("account_type" in str(error) for error in errors)
```

### 3. Business Logic Errors
```python
def test_insufficient_funds_transfer(self, authenticated_client):
    """Test transfer with insufficient funds"""
    # Create account with low balance
    account_data = {"name": "Low Balance", "initial_balance": 10.00}
    account_response = authenticated_client.post("/api/v1/accounts/", json=account_data)
    account_id = account_response.json()["id"]
    
    # Try to transfer more than balance
    transfer_data = {
        "to_account_id": "other_account_id",
        "amount": 100.00,
        "description": "Large transfer"
    }
    
    response = authenticated_client.post(f"/api/v1/accounts/{account_id}/transfer", json=transfer_data)
    assert response.status_code == 400
    assert "insufficient funds" in response.json()["detail"].lower()
```

## Test Performance and Optimization

### 1. Database Test Optimization
- Use in-memory SQLite for speed
- Rollback transactions instead of recreating tables
- Batch test data creation
- Use connection pooling for concurrent tests

### 2. Async Test Handling
```python
@pytest.mark.asyncio
async def test_async_endpoint(authenticated_client):
    """Test asynchronous operations"""
    response = await authenticated_client.get("/api/v1/accounts/summary")
    assert response.status_code == 200
```

## Test Organization Guidelines

### 1. Test Naming Convention
- `test_{functionality}_{expected_outcome}`
- Example: `test_create_account_success`, `test_login_invalid_credentials`

### 2. Test Categories
- **Unit Tests**: Individual functions/methods
- **Integration Tests**: Component interactions
- **API Tests**: Full HTTP request/response cycle
- **End-to-End Tests**: Complete user workflows

### 3. Test Documentation
```python
def test_complex_scenario(self):
    """
    Test Description: Verify account balance calculation after multiple transactions
    
    Scenario:
    1. Create account with initial balance
    2. Add multiple income transactions
    3. Add multiple expense transactions
    4. Verify final balance matches expected calculation
    
    Expected: Final balance = initial + income - expenses
    """
```

## Continuous Testing

### 1. Pre-commit Testing
- Run fast unit tests before each commit
- Ensure code formatting and linting pass
- Validate critical functionality

### 2. CI/CD Pipeline Testing
- Full test suite on pull requests
- Performance regression testing
- Security vulnerability scanning
- Code coverage reporting

### 3. Test Monitoring
- Track test execution time
- Monitor flaky test patterns
- Maintain test success rate >95%

## Current Test Status

**Latest Test Results**: 61/62 tests passing (98.4% success rate)

### Test Coverage by Component
- Account API: 20/20 tests ✅
- Account Service: 20/20 tests ✅ 
- Account Model: 8/8 tests ✅
- Authentication: 13/14 tests ✅ (1 minor status code issue)

### Known Issues
1. **Weak Password Test**: Expected 400 status code but receiving 422
   - **Fix**: Update test expectation or API response code
   - **Priority**: Low (cosmetic issue)

## Best Practices Summary

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Clarity**: Test names and assertions should clearly indicate purpose
3. **Coverage**: Aim for both positive and negative test scenarios
4. **Performance**: Keep tests fast and focused
5. **Maintenance**: Regularly review and update tests as features evolve
6. **Documentation**: Document complex test scenarios and edge cases

This testing framework ensures BudgetManager Pro maintains high quality and reliability as it evolves and scales.

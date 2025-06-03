# BudgetManager Pro - API Backend Context & Instructions

## Project Overview
BudgetManager Pro is a secure, multi-user budget management application with a FastAPI backend that provides RESTful APIs for personal finance management, CSV transaction imports, and account reconciliation.

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI 0.104+
- **Python Version**: 3.12+
- **Authentication**: JWT tokens with OAuth2
- **Validation**: Pydantic v2 models
- **Database**: SQLAlchemy ORM with SQLite
- **Testing**: Pytest with async support
- **Location**: `src/backend/`

### API Structure

#### Main Application (`app/main.py`)
```python
from fastapi import FastAPI
from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="BudgetManager Pro API",
    version="1.0.0",
    description="Personal finance and budget management API"
)

app.include_router(api_router, prefix="/api/v1")
```

#### API Versioning Structure
```
app/api/
├── __init__.py
├── api_v1/
│   ├── __init__.py
│   ├── api.py              # Main router aggregation
│   └── endpoints/          # Individual endpoint modules
│       ├── auth.py         # Authentication endpoints
│       ├── users.py        # User management
│       └── accounts.py     # Account management
└── v1/
    └── endpoints/
        ├── accounts.py     # Account CRUD operations
        ├── transactions.py # Transaction management
        ├── categories.py   # Category management
        ├── budgets.py      # Budget management
        └── csv_import.py   # CSV import functionality
```

### Core API Endpoints

#### Authentication API (`/api/v1/auth/`)
```python
POST /register          # User registration
POST /login            # User login (returns JWT)
POST /refresh          # Refresh JWT token
POST /logout           # Logout user
GET  /me               # Get current user profile
PUT  /me               # Update user profile
POST /change-password  # Change user password
```

#### Account Management API (`/api/v1/accounts/`)
```python
GET    /               # List user accounts (with pagination/filtering)
POST   /               # Create new account
GET    /{id}           # Get specific account
PUT    /{id}           # Update account
DELETE /{id}           # Soft delete account
PATCH  /{id}/activate  # Reactivate account
GET    /types          # Get available account types
GET    /stats          # Get account statistics
GET    /count          # Get total account count
```

#### Transaction Management API (`/api/v1/transactions/`)
```python
GET    /                    # List transactions (paginated, filtered)
POST   /                    # Create manual transaction
GET    /{id}                # Get specific transaction
PUT    /{id}                # Update transaction
DELETE /{id}                # Delete transaction
POST   /bulk               # Bulk transaction operations
GET    /stats              # Transaction statistics
POST   /categorize         # Auto-categorize transactions
GET    /duplicates         # Find potential duplicates
```

#### CSV Import API (`/api/v1/csv/`)
```python
POST   /upload/{account_id}     # Upload CSV file for import
GET    /institutions           # List supported institutions
POST   /institutions           # Add custom institution mapping
GET    /preview/{upload_id}     # Preview import before confirmation
POST   /confirm/{upload_id}     # Confirm and execute import
GET    /history                # Import history
```

### Security & Authentication

#### JWT Authentication Flow
```python
# Authentication dependency
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # Verify JWT token
    # Get user from database
    # Enforce user isolation
    return user
```

#### User Isolation Enforcement
```python
# Every API endpoint MUST enforce user isolation
@router.get("/accounts/")
def get_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only return accounts belonging to current_user
    return account_service.get_accounts(db, user_id=current_user.id)
```

#### Security Headers
```python
# Applied to all API responses
{
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY", 
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000",
    "Content-Security-Policy": "default-src 'self'"
}
```

### Request/Response Models

#### Pydantic Schemas (`app/schemas/`)
```python
# Account schemas
class AccountBase(BaseModel):
    name: str
    account_type: AccountType
    bank_name: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(AccountBase):
    name: Optional[str] = None
    account_type: Optional[AccountType] = None

class AccountResponse(AccountBase):
    id: int
    user_id: int
    balance: Decimal
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### API Response Patterns
```python
# Success response
{
    "data": {...},
    "message": "Operation successful",
    "success": true
}

# Error response
{
    "detail": "Error description",
    "error_code": "VALIDATION_ERROR",
    "timestamp": "2024-01-01T12:00:00Z"
}

# Paginated response
{
    "items": [...],
    "total": 150,
    "page": 1,
    "size": 50,
    "pages": 3
}
```

### Service Layer Pattern

#### Account Service (`app/services/account_service.py`)
```python
class AccountService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_account(self, account_data: AccountCreate, user_id: int) -> Account:
        # Validate user can create account
        # Create account with user isolation
        # Return created account
        pass
    
    def get_accounts(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        account_type: Optional[AccountType] = None
    ) -> List[Account]:
        # Get user accounts with filtering and pagination
        # Enforce user isolation
        pass
```

### Error Handling

#### Custom Exception Classes
```python
class BudgetManagerException(Exception):
    """Base exception for BudgetManager Pro"""
    pass

class AccountNotFoundException(BudgetManagerException):
    """Account not found or access denied"""
    pass

class InsufficientPermissionsException(BudgetManagerException):
    """User lacks required permissions"""
    pass
```

#### Global Exception Handler
```python
@app.exception_handler(BudgetManagerException)
async def budget_manager_exception_handler(request: Request, exc: BudgetManagerException):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "error_code": exc.__class__.__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### CSV Import Processing

#### Institution Mapping System
```python
class InstitutionMapper:
    """Maps CSV columns to standard transaction fields"""
    
    def __init__(self, institution_config: dict):
        self.config = institution_config
    
    def map_transaction(self, csv_row: dict) -> TransactionData:
        # Map institution-specific CSV format to standard fields
        # Handle date format variations
        # Parse amount with proper sign handling
        # Extract description and categorization hints
        pass
```

#### Duplicate Detection
```python
def generate_transaction_hash(transaction_data: dict) -> str:
    """Generate hash for duplicate detection"""
    # Combine date, amount, and partial description
    # Create reproducible hash signature
    # Handle slight variations in description
    pass
```

### API Development Guidelines

#### Security Requirements
1. **Always validate user ownership** before any operation
2. **Use dependency injection** for authentication
3. **Sanitize all inputs** with Pydantic validation
4. **Log security events** (failed auth, access attempts)
5. **Rate limit** authentication endpoints

#### Performance Guidelines
1. **Use async/await** for I/O operations
2. **Implement pagination** for list endpoints
3. **Add response caching** where appropriate
4. **Optimize database queries** with proper indexing
5. **Use background tasks** for heavy operations

#### Code Quality Standards
1. **Type hints** for all function parameters and returns
2. **Comprehensive docstrings** for all public methods
3. **Input validation** with Pydantic models
4. **Error handling** with proper HTTP status codes
5. **Unit testing** with minimum 80% coverage

### Testing Strategy

#### Test Structure
```python
# API endpoint tests
def test_create_account_success(client, auth_headers):
    # Test successful account creation
    pass

def test_create_account_unauthorized(client):
    # Test authentication requirement
    pass

def test_get_accounts_user_isolation(client, auth_headers):
    # Test user cannot see other users' accounts
    pass
```

#### Test Data Management
```python
# Test fixtures with user isolation
@pytest.fixture
def test_user(db_session):
    # Create isolated test user
    pass

@pytest.fixture
def auth_headers(test_user):
    # Generate JWT token for test user
    pass
```

### Monitoring & Logging

#### Request Logging
```python
# Log all API requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    return response
```

#### Health Checks
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Configuration Management

#### Environment-based Settings
```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./budget_manager.db"
    
    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_VERSION: str = "v1"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
```

## Key Files to Focus On
- `src/backend/app/main.py` - FastAPI application setup
- `src/backend/app/api/` - All API endpoints and routing
- `src/backend/app/core/` - Core functionality (auth, config, deps)
- `src/backend/app/services/` - Business logic layer
- `src/backend/app/schemas/` - Request/response models
- `tests/test_*_api.py` - API endpoint tests
- `src/backend/requirements.txt` - Python dependencies

# BudgetManager Pro - Database Context & Instructions

## Project Overview
BudgetManager Pro is a secure, multi-user personal finance and budget management web application. Users must authenticate to access their accounts and can only view/modify their own financial data.

## Database Architecture

### Technology Stack
- **Database**: SQLite (local, multi-user support)
- **ORM**: SQLAlchemy with Alembic migrations
- **Connection**: Async SQLAlchemy sessions
- **Location**: `src/backend/app/models/` and `src/backend/app/core/database.py`

### Core Database Models

#### User Model (`app/models/user.py`)
```python
class User(Base):
    id: Primary key
    email: Unique email address
    password_hash: Bcrypt hashed password
    first_name, last_name: User identification
    is_active: Account status
    is_superuser: Admin privileges
    created_at, updated_at: Timestamps
    last_login: Login tracking
```

#### Account Model (`app/models/account.py`)
```python
class Account(Base):
    id: Primary key
    user_id: Foreign key to User (strict isolation)
    name: Account display name
    account_type: Enum (checking, savings, credit_card, etc.)
    bank_name: Financial institution
    account_number: Encrypted account identifier
    balance: Current balance
    is_active: Active status
    description: Optional notes
    created_at, updated_at: Timestamps
```

#### Transaction Model (`app/models/transaction.py`)
```python
class Transaction(Base):
    id: Primary key
    account_id: Foreign key to Account
    date: Transaction date
    amount: Transaction amount (positive/negative)
    description: Transaction description
    category_id: Foreign key to Category
    subcategory_id: Optional subcategory
    is_duplicate: Duplicate detection flag
    csv_source: Source institution mapping
    hash_signature: Duplicate detection hash
    created_at, updated_at: Timestamps
```

#### Category Model (`app/models/category.py`)
```python
class Category(Base):
    id: Primary key
    user_id: Foreign key to User
    name: Category name
    description: Optional description
    color: UI color code
    is_default: System vs user category
    parent_id: Self-referential for subcategories
```

#### Budget Model (`app/models/budget.py`)
```python
class Budget(Base):
    id: Primary key
    user_id: Foreign key to User
    category_id: Foreign key to Category
    name: Budget name
    amount: Budget limit
    period: Enum (monthly, yearly, etc.)
    start_date, end_date: Budget period
    is_active: Active status
```

### Database Security & Isolation

#### Row-Level Security
- Every model (except User) has `user_id` foreign key
- All queries MUST filter by current user's ID
- Service layer enforces user isolation
- No cross-user data access allowed

#### Data Encryption
- Account numbers are encrypted at rest
- Passwords use bcrypt hashing
- Sensitive fields use application-level encryption

### CSV Import & Institution Mapping

#### CSV Configuration (`app/models/csv_config.py`)
```python
class CSVConfig(Base):
    id: Primary key
    user_id: Foreign key to User
    institution_name: Bank/institution identifier
    column_mappings: JSON field mapping CSV columns
    date_format: Institution-specific date format
    amount_column: Amount field identifier
    description_column: Description field
    is_active: Configuration status
```

#### Supported Institutions
- Configurable column mappings per institution
- Flexible date format parsing
- Automatic duplicate detection
- Transaction categorization suggestions

### Database Operations

#### Connection Management
```python
# Database session dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### User Isolation Pattern
```python
# All database queries MUST follow this pattern
def get_user_accounts(db: Session, user_id: int):
    return db.query(Account).filter(Account.user_id == user_id).all()
```

#### Transaction Patterns
- Use database transactions for multi-table operations
- Implement proper rollback on errors
- Async operations where beneficial
- Connection pooling for performance

### Key Development Guidelines

#### Security First
1. **Never skip user_id filtering** in queries
2. **Validate user ownership** before any operation
3. **Use parameterized queries** to prevent SQL injection
4. **Hash passwords** with bcrypt minimum cost 12
5. **Encrypt sensitive data** before storage

#### Performance Considerations
1. **Index user_id columns** for fast filtering
2. **Use pagination** for large result sets
3. **Implement query optimization** for complex reports
4. **Cache frequent queries** appropriately
5. **Monitor query performance** in production

#### Data Integrity
1. **Use foreign key constraints** to maintain relationships
2. **Implement proper cascading** for deletions
3. **Add database-level constraints** where possible
4. **Use transactions** for multi-step operations
5. **Validate data** at both API and database level

### Common Database Operations

#### Account Management
```python
# Create account (with user isolation)
def create_account(db: Session, account_data: AccountCreate, user_id: int):
    db_account = Account(**account_data.dict(), user_id=user_id)
    db.add(db_account)
    db.commit()
    return db_account

# Get user accounts with filtering
def get_accounts(db: Session, user_id: int, account_type: Optional[AccountType] = None):
    query = db.query(Account).filter(Account.user_id == user_id)
    if account_type:
        query = query.filter(Account.account_type == account_type)
    return query.all()
```

#### Transaction Import
```python
# Import CSV transactions with duplicate detection
def import_transactions(db: Session, csv_data: List[dict], user_id: int, account_id: int):
    for row in csv_data:
        # Generate hash for duplicate detection
        hash_sig = generate_transaction_hash(row)
        
        # Check for existing transaction
        existing = db.query(Transaction).filter(
            Transaction.account_id == account_id,
            Transaction.hash_signature == hash_sig
        ).first()
        
        if not existing:
            transaction = Transaction(
                account_id=account_id,
                hash_signature=hash_sig,
                **parse_csv_row(row)
            )
            db.add(transaction)
    
    db.commit()
```

### Migration Strategy
- Use Alembic for schema changes
- Maintain backwards compatibility
- Test migrations on copy of production data
- Document migration dependencies

### Testing Database Code
- Use test database isolation
- Reset test data between tests
- Test user isolation thoroughly
- Mock external dependencies

### Monitoring & Maintenance
- Log slow queries for optimization
- Monitor database growth and performance
- Regular backup strategy
- Index usage analysis

## Files to Focus On
- `src/backend/app/core/database.py` - Database configuration
- `src/backend/app/models/*.py` - All database models
- `src/backend/app/services/*.py` - Database service layer
- `tests/test_*_model.py` - Model tests
- `tests/test_*_service.py` - Service layer tests

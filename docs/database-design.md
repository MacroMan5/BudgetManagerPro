# BudgetManager Pro Database Design

## Database Specifications

**Database Type:** SQL (Relational)  
**Specific Database:** SQLite (Development), PostgreSQL (Production Migration Path)  
**Data Volume:** Small to Medium (1-100 users, ~10K-1M transactions)  
**Query Patterns:** Read-heavy with periodic bulk writes (CSV imports)  

## Entity Relationship Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Users    │    │  Accounts   │    │Transactions │
│             │    │             │    │             │
│ id (PK)     │◄───┤ user_id (FK)│◄───┤ account_id  │
│ username    │    │ id (PK)     │    │ id (PK)     │
│ email       │    │ name        │    │ date        │
│ password    │    │ type        │    │ amount      │
│ created_at  │    │ bank        │    │ description │
│             │    │ created_at  │    │ category_id │
└─────────────┘    └─────────────┘    │ created_at  │
                                      └─────────────┘
                                             │
┌─────────────┐    ┌─────────────┐          │
│ Categories  │    │  Balances   │          │
│             │    │             │          │
│ id (PK)     │◄───┤ category_id │◄─────────┘
│ user_id (FK)│    │ id (PK)     │
│ name        │    │ account_id  │
│ parent_id   │    │ month       │
│ type        │    │ opening     │
│ created_at  │    │ closing     │
└─────────────┘    │ created_at  │
                   └─────────────┘

┌─────────────┐    ┌─────────────┐
│CSV_Mappings │    │   Recurring │
│             │    │ Transactions│
│ id (PK)     │    │             │
│ user_id (FK)│    │ id (PK)     │
│ bank_name   │    │ user_id (FK)│
│ column_map  │    │ pattern     │
│ created_at  │    │ category_id │
└─────────────┘    │ amount      │
                   │ description │
                   │ frequency   │
                   │ created_at  │
                   └─────────────┘
```

## Table Specifications

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Accounts Table
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- 'checking', 'savings', 'credit_card', 'mortgage', 'line_of_credit'
    bank_name VARCHAR(255),
    account_number VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER NULL,
    category_type VARCHAR(20) NOT NULL, -- 'income', 'expense'
    color VARCHAR(7), -- Hex color code
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    description TEXT NOT NULL,
    category_id INTEGER NULL,
    transaction_type VARCHAR(20) NOT NULL, -- 'debit', 'credit'
    reference_number VARCHAR(100),
    is_reconciled BOOLEAN DEFAULT FALSE,
    is_transfer BOOLEAN DEFAULT FALSE,
    transfer_account_id INTEGER NULL,
    import_batch_id VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (transfer_account_id) REFERENCES accounts(id) ON DELETE SET NULL
);
```

### Balances Table
```sql
CREATE TABLE balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    month DATE NOT NULL, -- First day of the month
    opening_balance DECIMAL(15,2) NOT NULL,
    closing_balance DECIMAL(15,2) NOT NULL,
    calculated_balance DECIMAL(15,2), -- Auto-calculated from transactions
    is_reconciled BOOLEAN DEFAULT FALSE,
    reconciliation_difference DECIMAL(15,2) DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    UNIQUE(account_id, month)
);
```

### CSV_Mappings Table
```sql
CREATE TABLE csv_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bank_name VARCHAR(255) NOT NULL,
    mapping_name VARCHAR(255) NOT NULL,
    column_mappings JSON NOT NULL, -- JSON object with column mappings
    date_format VARCHAR(50) DEFAULT '%Y-%m-%d',
    amount_columns JSON, -- For banks with separate debit/credit columns
    description_columns JSON, -- Multiple description fields
    skip_rows INTEGER DEFAULT 0,
    has_header BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Recurring_Transactions Table
```sql
CREATE TABLE recurring_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pattern_name VARCHAR(255) NOT NULL,
    description_pattern VARCHAR(500) NOT NULL, -- Regex or contains pattern
    amount_range_min DECIMAL(15,2),
    amount_range_max DECIMAL(15,2),
    category_id INTEGER NOT NULL,
    frequency VARCHAR(20), -- 'monthly', 'weekly', 'biweekly'
    auto_categorize BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
```

## Indexes Strategy

### Primary Indexes
- All primary keys are automatically indexed
- Unique constraints on username, email

### Performance Indexes
```sql
-- User data isolation
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_categories_user_id ON categories(user_id);

-- Date-based queries
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_account_date ON transactions(account_id, date);
CREATE INDEX idx_balances_account_month ON balances(account_id, month);

-- Search and filtering
CREATE INDEX idx_transactions_description ON transactions(description);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);

-- Import optimization
CREATE INDEX idx_transactions_import_batch ON transactions(import_batch_id);
CREATE INDEX idx_transactions_reference ON transactions(reference_number);
```

## Data Constraints

### Business Rules
1. **User Data Isolation**: All user-owned entities must reference user_id
2. **Account Balancing**: Sum of transactions must equal balance differences
3. **Category Hierarchy**: Parent categories must belong to same user
4. **Transaction Integrity**: Transfers must reference valid accounts
5. **Date Consistency**: Transaction dates must be reasonable (not future)

### Validation Rules
```sql
-- Amount precision: 2 decimal places, max 13 digits
CHECK (amount >= -999999999999.99 AND amount <= 999999999999.99)

-- Valid account types
CHECK (account_type IN ('checking', 'savings', 'credit_card', 'mortgage', 'line_of_credit'))

-- Valid category types
CHECK (category_type IN ('income', 'expense'))

-- Valid transaction types
CHECK (transaction_type IN ('debit', 'credit'))
```

## Migration Strategy

### Development to Production Migration
1. **SQLite to PostgreSQL**: Use Alembic for schema migrations
2. **Data Migration**: Export/import scripts with data validation
3. **Index Recreation**: Rebuild indexes for PostgreSQL optimization

### Schema Versioning
- Use Alembic migration files
- Semantic versioning for database schema
- Rollback procedures for each migration

## Backup Strategy

### SQLite Backup
```bash
# Daily backup
sqlite3 budget_manager.db ".backup backup_$(date +%Y%m%d).db"

# Compressed backup
sqlite3 budget_manager.db ".dump" | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Retention Policy
- Daily backups: Keep 30 days
- Weekly backups: Keep 12 weeks
- Monthly backups: Keep 12 months

## Data Seeding

### Default Categories
```sql
-- Default Income Categories
INSERT INTO categories (user_id, name, category_type) VALUES
(1, 'Salary', 'income'),
(1, 'Freelance', 'income'),
(1, 'Investment Income', 'income');

-- Default Expense Categories
INSERT INTO categories (user_id, name, category_type) VALUES
(1, 'Housing', 'expense'),
(1, 'Transportation', 'expense'),
(1, 'Food & Dining', 'expense'),
(1, 'Utilities', 'expense'),
(1, 'Healthcare', 'expense');
```

### Sample CSV Mappings
```sql
INSERT INTO csv_mappings (user_id, bank_name, mapping_name, column_mappings) VALUES
(1, 'Bank of Montreal', 'BMO Checking', '{"date": 0, "description": 1, "amount": 2, "balance": 3}'),
(1, 'TD Canada Trust', 'TD Checking', '{"date": 0, "description": 2, "debit": 3, "credit": 4}');
```

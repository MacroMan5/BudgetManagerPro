# BudgetManager Pro - Data Flow Diagram

## Primary Data Flows

### 1. User Authentication Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │  React App  │    │ FastAPI     │    │  Database   │
│             │    │             │    │ Auth API    │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ 1. Login Form    │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 2. POST /auth    │                  │
       │                  ├─────────────────►│                  │
       │                  │                  │ 3. Validate User │
       │                  │                  ├─────────────────►│
       │                  │                  │ 4. User Data     │
       │                  │                  │◄─────────────────┤
       │                  │ 5. JWT Token     │                  │
       │                  │◄─────────────────┤                  │
       │ 6. Set Token     │                  │                  │
       │◄─────────────────┤                  │                  │
       │                  │                  │                  │
```

### 2. CSV Transaction Import Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │  React App  │    │ FastAPI     │    │  Database   │
│             │    │             │    │ Import API  │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ 1. Select CSV    │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 2. Upload File   │                  │
       │                  ├─────────────────►│                  │
       │                  │                  │ 3. Parse CSV     │
       │                  │                  │ 4. Map Columns   │
       │                  │                  │ 5. Validate Data │
       │                  │                  │ 6. Check Duplicates
       │                  │                  ├─────────────────►│
       │                  │                  │ 7. Existing Data │
       │                  │                  │◄─────────────────┤
       │                  │                  │ 8. Insert New    │
       │                  │                  ├─────────────────►│
       │                  │ 9. Import Result │                  │
       │                  │◄─────────────────┤                  │
       │ 10. Show Summary │                  │                  │
       │◄─────────────────┤                  │                  │
```

### 3. Transaction Categorization Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │  React App  │    │ FastAPI     │    │  Database   │
│             │    │             │    │Category API │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ 1. Load Trans.   │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 2. GET /transactions
       │                  ├─────────────────►│                  │
       │                  │                  │ 3. Query Trans.  │
       │                  │                  ├─────────────────►│
       │                  │                  │ 4. Transaction   │
       │                  │                  │    Data          │
       │                  │                  │◄─────────────────┤
       │                  │ 5. Trans. List   │                  │
       │                  │◄─────────────────┤                  │
       │ 6. Select Cat.   │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 7. PUT /transactions/{id}
       │                  ├─────────────────►│                  │
       │                  │                  │ 8. Update Cat.   │
       │                  │                  ├─────────────────►│
       │                  │ 9. Success       │                  │
       │                  │◄─────────────────┤                  │
       │ 10. Refresh UI   │                  │                  │
       │◄─────────────────┤                  │                  │
```

### 4. Monthly Balance Reconciliation Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │  React App  │    │ FastAPI     │    │  Database   │
│             │    │             │    │Balance API  │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ 1. Enter Balances│                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 2. POST /balances│                  │
       │                  ├─────────────────►│                  │
       │                  │                  │ 3. Store Balance │
       │                  │                  ├─────────────────►│
       │                  │                  │ 4. Calculate     │
       │                  │                  │    Transactions  │
       │                  │                  ├─────────────────►│
       │                  │                  │ 5. Trans. Sum    │
       │                  │                  │◄─────────────────┤
       │                  │                  │ 6. Reconcile     │
       │                  │                  │    (Open+Trans   │
       │                  │                  │     vs Close)    │
       │                  │ 7. Reconciliation│                  │
       │                  │    Report        │                  │
       │                  │◄─────────────────┤                  │
       │ 8. Show Results  │                  │                  │
       │◄─────────────────┤                  │                  │
```

### 5. Recurring Transaction Processing Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Scheduler │    │  React App  │    │ FastAPI     │    │  Database   │
│  (Future)   │    │             │    │Recurring API│    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ 1. Monthly Trigger│                 │                  │
       ├─────────────────►│                  │                  │
       │                  │ 2. Process       │                  │
       │                  │    Recurring     │                  │
       │                  ├─────────────────►│                  │
       │                  │                  │ 3. Get Recurring │
       │                  │                  │    Rules         │
       │                  │                  ├─────────────────►│
       │                  │                  │ 4. Rules Data    │
       │                  │                  │◄─────────────────┤
       │                  │                  │ 5. Match Import  │
       │                  │                  │    Transactions  │
       │                  │                  ├─────────────────►│
       │                  │                  │ 6. Auto-categorize
       │                  │                  ├─────────────────►│
       │                  │ 7. Processing    │                  │
       │                  │    Report        │                  │
       │                  │◄─────────────────┤                  │
```

## Data Flow Security Considerations

### 1. Authentication Headers
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
X-Request-ID: <unique-request-id>
```

### 2. Input Validation Flow
```
User Input → Frontend Validation → API Schema Validation → Database Constraints
```

### 3. Error Handling Flow
```
Database Error → Service Layer → API Response → Frontend Error Handler → User Notification
```

### 4. Audit Trail Flow
```
User Action → API Middleware → Audit Logger → Database Log → Monitoring Dashboard
```

## Performance Optimization Points

### 1. Database Query Optimization
- Index on `user_id`, `account_id`, `date` columns
- Monthly transaction queries with date range filters
- Category hierarchy queries with recursive CTEs

### 2. Caching Strategy
- User session caching (Redis)
- Category tree caching
- Monthly summary caching

### 3. Async Processing
- Large CSV file processing
- Monthly reconciliation calculations
- Report generation

### 4. Pagination Implementation
- Transaction list pagination (50 items per page)
- Account history pagination
- Search result pagination

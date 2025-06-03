# BudgetManager Pro API Specification

## API Overview

**Base URL:** `http://localhost:8000/api/v1`  
**API Type:** REST  
**Authentication:** JWT Bearer Tokens  
**Data Format:** JSON  
**Versioning Strategy:** URL Path Versioning  

## Core Entities

### 1. Users
- User registration, authentication, and profile management
- Multi-tenant data isolation

### 2. Accounts
- Bank accounts, credit cards, mortgages, lines of credit
- Account metadata and balance tracking

### 3. Transactions
- Financial transactions with categorization
- CSV import functionality with duplicate detection

### 4. Categories
- Hierarchical income and expense categories
- User-defined categorization system

### 5. Balances
- Monthly opening and closing balances
- Reconciliation calculations

### 6. CSV Mappings
- Bank-specific column mapping configurations
- Template management for different financial institutions

## API Endpoints Summary

### Authentication Endpoints
```
POST   /auth/register          # User registration
POST   /auth/login             # User login
POST   /auth/refresh           # Token refresh
POST   /auth/logout            # User logout
```

### User Management
```
GET    /users/me               # Get current user profile
PUT    /users/me               # Update user profile
DELETE /users/me               # Delete user account
```

### Account Management
```
GET    /accounts               # List user accounts
POST   /accounts               # Create new account
GET    /accounts/{id}          # Get account details
PUT    /accounts/{id}          # Update account
DELETE /accounts/{id}          # Delete account
```

### Transaction Management
```
GET    /transactions           # List transactions (paginated)
POST   /transactions           # Create transaction
GET    /transactions/{id}      # Get transaction details
PUT    /transactions/{id}      # Update transaction
DELETE /transactions/{id}      # Delete transaction
POST   /transactions/import    # Import CSV transactions
POST   /transactions/categorize # Bulk categorize transactions
```

### Category Management
```
GET    /categories             # List categories (tree structure)
POST   /categories             # Create category
GET    /categories/{id}        # Get category details
PUT    /categories/{id}        # Update category
DELETE /categories/{id}        # Delete category
```

### Balance Management
```
GET    /balances               # List account balances by month
POST   /balances               # Create/update monthly balance
GET    /balances/{account_id}/{month} # Get specific balance
PUT    /balances/{id}          # Update balance
POST   /balances/reconcile     # Reconcile monthly balances
```

### CSV Mapping Management
```
GET    /csv-mappings           # List user's CSV mappings
POST   /csv-mappings           # Create CSV mapping
GET    /csv-mappings/{id}      # Get mapping details
PUT    /csv-mappings/{id}      # Update mapping
DELETE /csv-mappings/{id}      # Delete mapping
```

### Reporting Endpoints
```
GET    /reports/monthly/{year}/{month}    # Monthly financial report
GET    /reports/yearly/{year}             # Yearly financial report
GET    /reports/account/{id}              # Account-specific report
GET    /reports/category/{id}             # Category spending analysis
```

## HTTP Status Codes

### Success Codes
- `200 OK` - Successful GET, PUT requests
- `201 Created` - Successful POST requests
- `204 No Content` - Successful DELETE requests

### Client Error Codes
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate entry)
- `422 Unprocessable Entity` - Validation errors

### Server Error Codes
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

## Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "timestamp": "2025-06-02T21:30:00Z",
    "request_id": "req_123456789"
  }
}
```

## Authentication

### JWT Token Structure
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1640995200,
  "iat": 1640991600,
  "type": "access"
}
```

### Authentication Header
```
Authorization: Bearer <access_token>
```

### Token Refresh Flow
1. Use refresh token to get new access token
2. Access tokens expire in 30 minutes
3. Refresh tokens expire in 7 days

## Rate Limiting

- **Default:** 60 requests per minute per user
- **Burst:** 10 additional requests
- **CSV Import:** 5 requests per minute
- **Headers:** Rate limit info in response headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

## Pagination

### Query Parameters
- `page` - Page number (default: 1)
- `size` - Items per page (default: 50, max: 100)
- `sort` - Sort field (default: created_at)
- `order` - Sort order (asc/desc, default: desc)

### Response Format
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "size": 50,
    "total": 150,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Search

### Common Query Parameters
- `search` - Full-text search
- `date_from` - Start date filter (YYYY-MM-DD)
- `date_to` - End date filter (YYYY-MM-DD)
- `account_id` - Filter by account
- `category_id` - Filter by category
- `amount_min` - Minimum amount filter
- `amount_max` - Maximum amount filter

## File Upload Specifications

### CSV Import
- **Max File Size:** 10MB
- **Supported Formats:** CSV, TXT
- **Required Headers:** Configurable via CSV mappings
- **Encoding:** UTF-8 (with BOM detection)

### Upload Response
```json
{
  "file_id": "upload_123456",
  "filename": "transactions.csv",
  "size": 2048576,
  "rows_processed": 150,
  "rows_imported": 145,
  "rows_duplicate": 5,
  "errors": []
}
```

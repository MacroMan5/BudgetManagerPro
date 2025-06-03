# BudgetManager Pro - System Overview

## Project Information
**Project Name:** BudgetManager Pro  
**Project Type:** Web Application  
**Technology Stack:** FastAPI + Python 3.12, React + Vite, SQLite  
**Scale:** Small to Medium (1-100 users)  
**Duration:** MVP in 4 weeks  

## System Architecture Overview

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │  FastAPI        │    │  SQLite         │
│   (Frontend)    │◄──►│  Backend API    │◄──►│  Database       │
│                 │    │                 │    │                 │
│ - Dashboard     │    │ - CSV Import    │    │ - Users         │
│ - Transactions  │    │ - Categories    │    │ - Accounts      │
│ - Accounts      │    │ - Balance Rec.  │    │ - Transactions  │
│ - Reports       │    │ - Auth/Security │    │ - Categories    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### Frontend (React + Vite)
- **Authentication Module**: User login/logout, session management
- **Account Management**: Create, edit, view accounts and balances
- **Transaction Management**: Import CSV, categorize, reconcile
- **Category Management**: Create hierarchical income/expense categories
- **Dashboard**: Monthly summaries, account balances, visual reports
- **CSV Mapping Configuration**: Bank-specific column mapping interface

#### Backend (FastAPI + Python)
- **Authentication Service**: JWT-based auth with session management
- **Account Service**: CRUD operations for user accounts
- **Transaction Service**: CSV import, duplicate detection, categorization
- **Category Service**: Hierarchical category management
- **Balance Service**: Monthly reconciliation and validation
- **Reporting Service**: Generate financial reports and summaries

#### Database (SQLite)
- **Multi-tenant architecture**: Each user's data isolated
- **Referential integrity**: Foreign key constraints
- **Indexing strategy**: Optimized for monthly queries
- **Backup strategy**: Automated daily backups

### Security Architecture
- **Authentication**: OAuth2/JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Data Isolation**: User-scoped data access patterns
- **Input Validation**: Comprehensive validation on all inputs
- **File Upload Security**: CSV validation and sanitization

### Deployment Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Nginx     │  │  FastAPI    │  │   SQLite    │        │
│  │ (Reverse    │  │   App       │  │  Database   │        │
│  │  Proxy)     │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │               │
│         └────────────────┼────────────────┘               │
│                          │                                │
│  ┌─────────────┐        │        ┌─────────────┐          │
│  │   React     │        │        │   Volume    │          │
│  │ Static Files│        │        │  (Database  │          │
│  │             │        │        │   Storage)  │          │
│  └─────────────┘        │        └─────────────┘          │
└─────────────────────────┼─────────────────────────────────┘
                          │
                          ▼
                    Host Network
                  (localhost:8080)
```

### Data Flow Architecture
1. **User Authentication Flow**
2. **CSV Import Flow**
3. **Transaction Categorization Flow**
4. **Monthly Reconciliation Flow**
5. **Report Generation Flow**

### Performance Considerations
- **Database Indexing**: Optimized for date-range queries
- **Pagination**: Large transaction lists with efficient pagination
- **Caching**: Redis for session storage and frequent queries
- **File Processing**: Asynchronous CSV processing for large files

### Scalability Approach
- **Horizontal Scaling**: Docker containers behind load balancer
- **Database Scaling**: SQLite → PostgreSQL migration path
- **Microservices**: Modular architecture for future service extraction

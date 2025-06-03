# BudgetManager Pro - Component Architecture

## Component Diagram

### Frontend Components (React)

```
┌─────────────────────────────────────────────────────────────┐
│                    React Application                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Auth     │  │  Dashboard  │  │  Accounts   │        │
│  │ Components  │  │ Components  │  │ Components  │        │
│  │             │  │             │  │             │        │
│  │ - Login     │  │ - Summary   │  │ - List      │        │
│  │ - Register  │  │ - Charts    │  │ - Form      │        │
│  │ - Logout    │  │ - Metrics   │  │ - Details   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Transaction  │  │ Categories  │  │   Reports   │        │
│  │ Components  │  │ Components  │  │ Components  │        │
│  │             │  │             │  │             │        │
│  │ - Import    │  │ - Tree      │  │ - Monthly   │        │
│  │ - List      │  │ - Form      │  │ - Yearly    │        │
│  │ - Categorize│  │ - Assign    │  │ - Export    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Shared    │  │   Hooks     │  │  Services   │        │
│  │ Components  │  │             │  │             │        │
│  │             │  │ - useAuth   │  │ - API       │        │
│  │ - Layout    │  │ - useAPI    │  │ - Storage   │        │
│  │ - Forms     │  │ - useForm   │  │ - Utils     │        │
│  │ - Tables    │  │ - useTable  │  │ - Validation│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Backend Components (FastAPI)

```
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                      │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    API      │  │    Core     │  │   Models    │        │
│  │  Routers    │  │             │  │             │        │
│  │             │  │ - Config    │  │ - User      │        │
│  │ - Auth      │  │ - Security  │  │ - Account   │        │
│  │ - Accounts  │  │ - Database  │  │ - Transaction│       │
│  │ - Trans.    │  │ - Logging   │  │ - Category  │        │
│  │ - Categories│  │ - Utils     │  │ - Balance   │        │
│  │ - Reports   │  └─────────────┘  └─────────────┘        │
│  └─────────────┘                                           │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Schemas    │  │  Services   │  │   Utils     │        │
│  │ (Pydantic)  │  │ (Business   │  │             │        │
│  │             │  │   Logic)    │  │ - CSV Parser│        │
│  │ - UserDTO   │  │             │  │ - Validators│        │
│  │ - AccountDTO│  │ - AuthSvc   │  │ - Formatters│        │
│  │ - TransDTO  │  │ - AcctSvc   │  │ - Calculators│       │
│  │ - CatDTO    │  │ - TransSvc  │  │ - Mappers   │        │
│  │ - ReportDTO │  │ - CatSvc    │  │ - Helpers   │        │
│  └─────────────┘  │ - ReportSvc │  └─────────────┘        │
│                   └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

### Database Components (SQLite)

```
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Users    │  │  Accounts   │  │Transactions │        │
│  │             │  │             │  │             │        │
│  │ - id        │  │ - id        │  │ - id        │        │
│  │ - username  │  │ - user_id   │  │ - account_id│        │
│  │ - email     │  │ - name      │  │ - date      │        │
│  │ - password  │  │ - type      │  │ - amount    │        │
│  │ - created   │  │ - bank      │  │ - description│       │
│  └─────────────┘  │ - number    │  │ - category_id│       │
│                   │ - created   │  │ - created   │        │
│                   └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Categories  │  │   Balances  │  │   Mappings  │        │
│  │             │  │             │  │ (CSV Config)│        │
│  │ - id        │  │ - id        │  │             │        │
│  │ - user_id   │  │ - account_id│  │ - id        │        │
│  │ - name      │  │ - month     │  │ - user_id   │        │
│  │ - parent_id │  │ - opening   │  │ - bank_name │        │
│  │ - type      │  │ - closing   │  │ - column_map│        │
│  │ - created   │  │ - created   │  │ - created   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Component Interactions

### 1. Authentication Flow
```
Frontend Auth → API Auth Router → Auth Service → User Model → Database
```

### 2. CSV Import Flow
```
Frontend Upload → API Transaction Router → CSV Parser → Transaction Service → Transaction Model → Database
```

### 3. Categorization Flow
```
Frontend Category → API Category Router → Category Service → Category Model → Database
```

### 4. Reconciliation Flow
```
Frontend Balance → API Account Router → Balance Service → Balance Model → Database
```

## Component Dependencies

### Frontend Dependencies
- **React 18+**: Core framework
- **React Router**: Navigation
- **Axios**: HTTP client
- **React Query**: State management
- **Tailwind CSS**: Styling
- **React Hook Form**: Form handling
- **Chart.js**: Data visualization

### Backend Dependencies
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **python-jose**: JWT handling
- **bcrypt**: Password hashing
- **pytest**: Testing framework

### Database Dependencies
- **SQLite**: Development database
- **SQLAlchemy Core**: Database abstraction
- **Alembic**: Schema migration tool

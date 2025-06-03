# BudgetManager Pro

A secure, multi-user web application for personal and family budget management with automated CSV transaction imports and intelligent categorization.

## 🚀 Features

- **Multi-User Authentication**: Secure user accounts with data isolation
- **CSV Transaction Import**: Support for multiple bank formats with configurable column mapping
- **Intelligent Categorization**: Hierarchical income/expense categories with auto-categorization
- **Balance Reconciliation**: Monthly account balancing with integrity checks
- **Recurring Transactions**: Automatic detection and categorization of recurring items
- **Account Management**: Support for bank accounts, credit cards, mortgages, and lines of credit
- **Financial Reports**: Monthly summaries, yearly reports, and visual dashboards

## 🏗️ Architecture

- **Backend**: FastAPI + Python 3.12
- **Frontend**: React 18 + Vite + TypeScript
- **Database**: SQLite (local, multi-user)
- **Deployment**: Docker Compose
- **Authentication**: OAuth2/JWT with secure session management

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+
- Docker Desktop
- Git

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd BudgetManagerPro
```

### 2. Development Environment
```bash
# Backend setup
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 3. Database Setup
```bash
cd src/backend
alembic upgrade head
```

### 4. Run Development Servers
```bash
# Backend (Terminal 1)
cd src/backend
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd src/frontend
npm run dev
```

### 5. Docker Deployment
```bash
docker-compose up -d
```

Application will be available at: http://localhost:3000

## 📁 Project Structure

```
BudgetManagerPro/
├── src/
│   ├── backend/           # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/       # API routes
│   │   │   ├── core/      # Core configuration
│   │   │   ├── models/    # SQLAlchemy models
│   │   │   ├── schemas/   # Pydantic schemas
│   │   │   ├── services/  # Business logic
│   │   │   └── utils/     # Utilities
│   │   ├── tests/         # Backend tests
│   │   └── requirements.txt
│   └── frontend/          # React frontend
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── hooks/
│       │   ├── services/
│       │   └── utils/
│       └── package.json
├── tests/                 # Integration tests
├── docs/                  # Documentation
├── scripts/               # Build and utility scripts
├── config/                # Configuration files
├── architecture/          # Architecture documentation
├── project_management/    # Project management artifacts
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=sqlite:///./budget_manager.db
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

### CSV Bank Mapping
Configure bank-specific CSV column mappings in the application settings:
- Date format patterns
- Amount column processing
- Description field mapping
- Transaction type detection

## 🧪 Testing

```bash
# Backend tests
cd src/backend
pytest

# Frontend tests
cd src/frontend
npm test

# Integration tests
cd tests
pytest
```

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔒 Security Features

- **Authentication**: JWT-based authentication with refresh tokens
- **Authorization**: User-scoped data access with RBAC
- **Input Validation**: Comprehensive validation on all inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS Configuration**: Secure cross-origin resource sharing
- **File Upload Security**: CSV validation and sanitization

## 🚀 Deployment

### Local Docker Deployment
```bash
docker-compose up -d
```

### Production Considerations
- Use environment-specific configuration files
- Implement proper backup strategies for SQLite database
- Configure reverse proxy (Nginx) for HTTPS
- Set up monitoring and logging

## 📈 Development Roadmap

### Phase 1 (MVP - 4 weeks)
- [x] Architecture and project setup
- [ ] User authentication system
- [ ] Account management
- [ ] CSV import functionality
- [ ] Basic transaction categorization
- [ ] Monthly balance reconciliation

### Phase 2 (Enhancements)
- [ ] Advanced reporting and visualization
- [ ] Recurring transaction automation
- [ ] Mobile-responsive design
- [ ] Data export capabilities
- [ ] Advanced security features

### Phase 3 (Scale)
- [ ] PostgreSQL migration option
- [ ] Advanced analytics
- [ ] API rate limiting
- [ ] Audit logging
- [ ] Performance optimization

## 🤝 Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Review the documentation in the `docs/` directory
- Check the API documentation at `/docs` endpoint

## 🔄 Version History

- **v0.1.0** - Initial project setup and architecture
- **v0.2.0** - Authentication and account management (planned)
- **v0.3.0** - CSV import and transaction management (planned)
- **v1.0.0** - MVP release (planned)

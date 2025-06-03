# Copilot Instructions for BudgetManager Pro

## 🏗️ Project Overview
**Name:** BudgetManager Pro  
**Type:** Full-stack web application for personal and family budget management  
**Architecture:** FastAPI (Python 3.12) backend + React (TypeScript + Vite) frontend + SQLite database + Docker deployment

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.12, SQLAlchemy, JWT Authentication |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Database | SQLite (development), PostgreSQL (production ready) |
| Testing | pytest (backend), Jest/Vitest (frontend) |
| Deployment | Docker Compose, GitHub Actions CI/CD |
| Monitoring | Prometheus metrics, structured logging |

## 📋 Available Commands

### Backend Commands
| Command | Description |
|---------|-------------|
| `cd src/backend && python -m uvicorn app.main:app --reload` | Start development server |
| `cd src/backend && python -m pytest` | Run backend tests |
| `cd src/backend && python -m black .` | Format code |
| `cd src/backend && python -m flake8 .` | Lint code |
| `cd src/backend && python -m mypy .` | Type checking |

### Frontend Commands
| Command | Description |
|---------|-------------|
| `cd src/frontend && npm run dev` | Start development server |
| `cd src/frontend && npm run build` | Build for production |
| `cd src/frontend && npm run test` | Run tests |
| `cd src/frontend && npm run lint` | Lint code |
| `cd src/frontend && npm run type-check` | Type checking |

### Docker Commands
| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |
| `docker-compose build` | Build images |
| `scripts/run-local.ps1` | Start development servers (Windows) |

## ✅ Definition of Done

### For Features
- [ ] Code follows project coding standards (Black, ESLint)
- [ ] All tests pass (pytest for backend, Jest/Vitest for frontend)
- [ ] Type checking passes (MyPy for Python, TypeScript for frontend)
- [ ] Security scan passes (no high/critical vulnerabilities)
- [ ] API endpoints documented in OpenAPI schema
- [ ] Integration tests pass
- [ ] Code review completed
- [ ] Documentation updated

### For Releases
- [ ] All CI/CD pipeline checks pass
- [ ] Docker images build successfully
- [ ] Staging deployment successful
- [ ] Production deployment tested
- [ ] Monitoring and alerting configured
- [ ] Rollback procedure tested

## 🚨 Code Quality Requirements

### Backend (Python)
- Use **Black** for code formatting (line length: 88)
- Use **isort** for import sorting
- Use **flake8** for linting (max complexity: 10)
- Use **MyPy** for type hints (strict mode)
- Minimum test coverage: 80%
- Use **pytest** fixtures for test setup
- Follow FastAPI best practices
- Use Pydantic models for data validation

### Frontend (TypeScript/React)
- Use **ESLint** with strict TypeScript rules
- Use **Prettier** for code formatting
- Use **TypeScript** strict mode
- Follow React hooks best practices
- Use functional components over class components
- Implement proper error boundaries
- Use proper key props for lists
- Implement accessibility (a11y) standards

## 🔒 Security Guidelines
- Never commit secrets or API keys
- Use environment variables for configuration
- Implement proper input validation
- Use JWT for authentication with secure settings
- Hash passwords using bcrypt
- Implement rate limiting on API endpoints
- Use HTTPS in production
- Validate all user inputs
- Implement proper CORS policies

## ⛔ Do Not
- Commit `.env` files (use `.env.example` instead)
- Commit `node_modules/` or `__pycache__/` directories
- Commit database files (`*.db`, `*.sqlite`)
- Commit IDE-specific files (except `.vscode/settings.json`)
- Use `console.log()` in production frontend code
- Use `print()` statements in production backend code (use logging)
- Hardcode configuration values
- Skip type annotations in Python code
- Use `any` type in TypeScript without justification
- Commit with failing tests or linting errors

## 📁 Project Structure

```
BudgetManagerPro/
├── src/
│   ├── backend/          # FastAPI application
│   │   ├── app/
│   │   │   ├── api/      # API routes
│   │   │   ├── core/     # Core configuration
│   │   │   ├── models/   # Database models
│   │   │   ├── schemas/  # Pydantic schemas
│   │   │   └── services/ # Business logic
│   │   └── tests/        # Backend tests
│   └── frontend/         # React application
│       ├── src/
│       │   ├── components/  # Reusable components
│       │   ├── pages/       # Page components
│       │   ├── hooks/       # Custom hooks
│       │   ├── services/    # API services
│       │   └── types/       # TypeScript types
│       └── tests/          # Frontend tests
├── docs/                 # Documentation
├── scripts/              # Build and utility scripts
├── .github/              # CI/CD workflows
└── docker-compose.yml
```

## 🔧 Development Workflow
1. Create feature branch from `develop`
2. Implement feature with tests
3. Run local quality checks (`black`, `eslint`, `mypy`)
4. Run full test suite
5. Create pull request to `develop`
6. CI/CD pipeline runs automatically
7. Code review and approval required
8. Merge to `develop` triggers staging deployment
9. Merge to `main` triggers production deployment

## 🎯 Key Features Being Developed
- **Multi-user authentication** with role-based access
- **Transaction management** with CSV import capabilities
- **Budget planning** with category-based tracking
- **Automated categorization** using intelligent matching
- **Balance reconciliation** with bank account integration
- **Recurring transactions** with automated scheduling
- **Financial reporting** with charts and analytics
- **Family budget sharing** with permission controls

---

💡 **Remember**: This project emphasizes security, user experience, and maintainable code. Always consider the financial nature of the data when making decisions.

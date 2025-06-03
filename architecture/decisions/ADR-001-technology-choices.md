# ADR-001: Technology Stack Choices for BudgetManager Pro

## Status
**ACCEPTED** - 2025-06-02

## Context

BudgetManager Pro is a personal/family budget management web application that requires:
- Multi-user authentication with data isolation
- CSV transaction import with bank-specific column mapping
- Real-time transaction categorization and balance reconciliation
- Local deployment for privacy and security
- Rapid development for 4-week MVP timeline

## Decision

We will use the following technology stack:

### Backend: FastAPI + Python 3.12
**Rationale:**
- FastAPI provides automatic API documentation (OpenAPI/Swagger)
- Excellent performance with async/await support
- Strong typing with Pydantic for data validation
- Built-in security features for OAuth2/JWT
- Rapid development with minimal boilerplate
- Excellent CSV processing libraries (pandas, csv)

### Frontend: React 18 + Vite
**Rationale:**
- React's component-based architecture suits complex UI requirements
- Large ecosystem for financial UI components (charts, tables)
- Vite provides fast development experience and optimized builds
- TypeScript support for type safety
- Excellent state management options (React Query, Zustand)

### Database: SQLite
**Rationale:**
- Zero-configuration setup for local deployment
- ACID compliance for financial data integrity
- Sufficient performance for expected user load (1-100 users)
- Easy backup and migration (single file)
- No external database server required
- Migration path to PostgreSQL if needed

### Containerization: Docker Compose
**Rationale:**
- Consistent development and deployment environment
- Easy local multi-user setup
- Service isolation (frontend, backend, database)
- Simple reverse proxy configuration with Nginx
- Straightforward scaling options

## Alternatives Considered

### Backend Alternatives
- **Django**: More overhead, slower development for API-focused app
- **Express.js**: Less built-in validation, security features
- **ASP.NET Core**: Windows-centric, heavier runtime requirements

### Frontend Alternatives
- **Vue.js**: Smaller ecosystem for financial components
- **Angular**: Too complex for 4-week timeline
- **Svelte**: Less mature ecosystem, fewer financial libraries

### Database Alternatives
- **PostgreSQL**: Requires external server setup, overkill for initial scale
- **MySQL**: Similar complexity to PostgreSQL
- **MongoDB**: Document model doesn't fit financial transaction structure

## Consequences

### Positive
- **Rapid Development**: FastAPI + React enable quick prototyping
- **Type Safety**: Python type hints + TypeScript reduce runtime errors
- **Security**: Built-in auth features and data validation
- **Performance**: Async FastAPI + SQLite provide excellent local performance
- **Maintainability**: Clear separation of concerns, well-documented APIs
- **Scalability**: Clear migration paths to cloud deployment

### Negative
- **SQLite Limitations**: Not suitable for high-concurrency scenarios
- **Local Deployment**: Requires technical setup by users
- **Python Dependency**: Requires Python runtime environment

### Risks & Mitigations
- **Risk**: SQLite performance degradation with large datasets
  - **Mitigation**: Implement pagination, indexing, and archival strategies
- **Risk**: Complex CSV parsing requirements
  - **Mitigation**: Use pandas for robust CSV handling, configurable column mapping
- **Risk**: Multi-user data isolation in SQLite
  - **Mitigation**: Strict user-scoped queries, database-level constraints

## Implementation Notes

### Development Environment
- Python 3.12+ with virtual environment
- Node.js 18+ for frontend tooling
- Docker Desktop for containerization
- VS Code with Python and TypeScript extensions

### Key Libraries
**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0+ (ORM)
- Alembic (migrations)
- Pydantic 2.0+ (validation)
- python-jose (JWT)
- bcrypt (password hashing)
- pandas (CSV processing)

**Frontend:**
- React 18+
- TypeScript 5.0+
- React Router 6+
- React Query (server state)
- Axios (HTTP client)
- Tailwind CSS (styling)
- React Hook Form (forms)
- Chart.js (visualizations)

### Deployment Strategy
1. **Development**: Local Docker Compose with hot reload
2. **Production**: Single Docker Compose stack with Nginx reverse proxy
3. **Future**: Kubernetes deployment for enterprise scale

## Review Date
This decision should be reviewed after MVP completion (approximately 4 weeks) to assess:
- Performance with real-world data volumes
- User feedback on deployment complexity
- Scaling requirements based on adoption

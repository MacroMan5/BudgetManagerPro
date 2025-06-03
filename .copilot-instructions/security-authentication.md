# Security and Authentication Guidelines - BudgetManager Pro

## Project Overview
BudgetManager Pro implements enterprise-grade security measures to protect user financial data, ensure privacy, and maintain regulatory compliance.

## Security Architecture

### Core Security Principles
1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Users access only what they need
3. **Zero Trust**: Verify every request and user
4. **Data Encryption**: Encrypt data at rest and in transit
5. **Security by Design**: Built-in security from ground up

### Authentication Framework
- **Protocol**: JWT (JSON Web Tokens)
- **Algorithm**: HS256 with rotating secret keys
- **Token Types**: Access tokens (short-lived) + Refresh tokens (long-lived)
- **Session Management**: Stateless authentication with secure token storage

## Authentication Implementation

### 1. JWT Token Structure
```python
# Token Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Short-lived access tokens
REFRESH_TOKEN_EXPIRE_DAYS = 30    # Long-lived refresh tokens
ALGORITHM = "HS256"
SECRET_KEY = "your-secret-key"    # Use environment variable in production

# Token Payload Structure
{
    "sub": "user_id",           # Subject (user identifier)
    "exp": timestamp,           # Expiration time
    "iat": timestamp,           # Issued at time  
    "type": "access"|"refresh", # Token type
    "email": "user@email.com"   # User email for verification
}
```

### 2. Password Security
```python
# Password Requirements (Enforced in UserCreateSchema)
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one digit
- At least one special character (!@#$%^&*(),.?\":{}|<>)

# Password Hashing (bcrypt with salt)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 3. Authentication Endpoints
```python
# Registration with validation
POST /api/v1/auth/register
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
}

# Login with credentials
POST /api/v1/auth/login
{
    "email": "user@example.com", 
    "password": "SecurePass123!"
}
Response: {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
}

# Token refresh
POST /api/v1/auth/refresh
{
    "refresh_token": "eyJ..."
}

# Password change (authenticated)
POST /api/v1/auth/change-password
{
    "current_password": "OldPass123!",
    "new_password": "NewPass456!"
}
```

## Authorization and Access Control

### 1. Route Protection
```python
# Dependency for protected routes
async def get_current_user(token: str = Depends(security_scheme)) -> User:
    """Extract and validate user from JWT token"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(user_id)
    if user is None:
        raise credentials_exception
    return user

# Usage in protected endpoints
@router.get("/accounts/")
async def get_accounts(current_user: User = Depends(get_current_user)):
    # Only authenticated users can access
    return get_user_accounts(current_user.id)
```

### 2. Resource-Level Authorization
```python
# Ensure users can only access their own data
async def get_user_account(account_id: int, current_user: User = Depends(get_current_user)):
    account = get_account_by_id(account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return account
```

### 3. Role-Based Access Control (Future Enhancement)
```python
# User roles for enhanced security
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READ_ONLY = "read_only"

# Role-based decorator
def require_role(required_role: UserRole):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role != required_role:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

## Data Security

### 1. Database Security
```python
# User data isolation - every query includes user context
def get_user_accounts(db: Session, user_id: int):
    return db.query(Account).filter(Account.user_id == user_id).all()

def get_user_transactions(db: Session, user_id: int):
    return db.query(Transaction).join(Account).filter(Account.user_id == user_id).all()

# Prevent SQL injection with parameterized queries
def get_account_by_name(db: Session, name: str, user_id: int):
    return db.query(Account).filter(
        and_(Account.name == name, Account.user_id == user_id)
    ).first()
```

### 2. Sensitive Data Protection
```python
# Hide sensitive fields in API responses
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    # Note: password_hash is NOT included

# Sanitize error messages (avoid information disclosure)
try:
    user = authenticate_user(email, password)
except Exception:
    # Generic error message - don't reveal if email exists
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

### 3. Audit Logging
```python
# Security event logging
import logging

security_logger = logging.getLogger("security")

def log_security_event(event_type: str, user_id: int = None, details: dict = None):
    security_logger.info(
        f"Security Event: {event_type}",
        extra={
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "details": details,
            "ip_address": get_client_ip(),
            "user_agent": get_user_agent()
        }
    )

# Log important security events
log_security_event("LOGIN_SUCCESS", user_id=user.id)
log_security_event("LOGIN_FAILED", details={"email": email})
log_security_event("PASSWORD_CHANGED", user_id=user.id)
log_security_event("ACCOUNT_CREATED", user_id=user.id)
```

## Input Validation and Sanitization

### 1. Pydantic Schema Validation
```python
class UserCreateSchema(BaseModel):
    email: EmailStr  # Built-in email validation
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        # Sanitize name (remove potentially dangerous characters)
        sanitized = re.sub(r'[<>\"\'&]', '', v.strip())
        if len(sanitized) == 0:
            raise ValueError('Full name cannot be empty')
        return sanitized
```

### 2. SQL Injection Prevention
```python
# Always use SQLAlchemy ORM or parameterized queries
# GOOD:
accounts = db.query(Account).filter(Account.user_id == user_id).all()

# BAD (vulnerable to SQL injection):
# query = f"SELECT * FROM accounts WHERE user_id = {user_id}"
# db.execute(query)
```

### 3. Cross-Site Scripting (XSS) Prevention
```python
from html import escape

def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return ""
    
    # HTML escape dangerous characters
    sanitized = escape(text)
    
    # Remove potential script tags
    sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized.strip()

# Use in schemas
@validator('description')
def sanitize_description(cls, v):
    return sanitize_user_input(v)
```

## API Security Headers

### 1. CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

### 2. Security Headers Middleware
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

## Rate Limiting and DDoS Protection

### 1. Rate Limiting Implementation
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply rate limits to sensitive endpoints
@router.post("/auth/login")
@limiter.limit("5/minute")  # 5 login attempts per minute
async def login(request: Request, user_data: UserLoginSchema):
    # Login logic here
    pass

@router.post("/auth/register")
@limiter.limit("3/hour")  # 3 registrations per hour
async def register(request: Request, user_data: UserCreateSchema):
    # Registration logic here
    pass
```

### 2. Account Lockout Mechanism
```python
class UserModel(Base):
    # Add fields for account lockout
    failed_login_attempts: int = Column(Integer, default=0)
    locked_until: datetime = Column(DateTime, nullable=True)
    
    def is_locked(self) -> bool:
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False
    
    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes after 5 failed attempts
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.locked_until = None
```

## Environment and Configuration Security

### 1. Environment Variables
```bash
# .env file (never commit to repository)
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///./budget_manager.db
JWT_SECRET_KEY=another-secret-key-for-jwt
BCRYPT_ROUNDS=12
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Production environment should use:
# - Strong random secret keys
# - PostgreSQL instead of SQLite  
# - Redis for session storage
# - HTTPS only
```

### 2. Configuration Validation
```python
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    secret_key: str
    jwt_secret_key: str
    database_url: str
    bcrypt_rounds: int = 12
    access_token_expire_minutes: int = 30
    
    @validator('secret_key', 'jwt_secret_key')
    def secret_keys_not_empty(cls, v):
        if not v or len(v) < 32:
            raise ValueError('Secret keys must be at least 32 characters long')
        return v
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Security Testing

### 1. Authentication Tests
```python
def test_login_with_invalid_credentials():
    response = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "wrong_password"
    })
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_access_protected_route_without_token():
    response = client.get("/api/v1/accounts/")
    assert response.status_code == 401

def test_access_with_expired_token():
    # Test with manually created expired token
    expired_token = create_expired_token()
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/accounts/", headers=headers)
    assert response.status_code == 401
```

### 2. Authorization Tests
```python
def test_user_cannot_access_other_user_data():
    # Create two users
    user1_token = create_user_and_get_token("user1@example.com")
    user2_token = create_user_and_get_token("user2@example.com")
    
    # User 1 creates an account
    account_response = client.post("/api/v1/accounts/", 
        json={"name": "User1 Account"}, 
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    account_id = account_response.json()["id"]
    
    # User 2 tries to access User 1's account
    response = client.get(f"/api/v1/accounts/{account_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403
```

### 3. Input Validation Tests
```python
def test_sql_injection_prevention():
    malicious_input = "'; DROP TABLE accounts; --"
    response = client.post("/api/v1/accounts/", 
        json={"name": malicious_input},
        headers=auth_headers
    )
    # Should not cause SQL injection - either validation error or sanitized
    assert response.status_code in [400, 422, 201]

def test_xss_prevention():
    xss_input = "<script>alert('xss')</script>"
    response = client.post("/api/v1/accounts/", 
        json={"description": xss_input},
        headers=auth_headers
    )
    if response.status_code == 201:
        account = response.json()
        assert "<script>" not in account["description"]
```

## Production Security Checklist

### 1. Deployment Security
- [ ] Use HTTPS only (TLS 1.2+)
- [ ] Set secure HTTP headers
- [ ] Configure proper CORS policy
- [ ] Use environment variables for secrets
- [ ] Enable request logging and monitoring
- [ ] Set up intrusion detection
- [ ] Configure firewall rules
- [ ] Use Docker security best practices

### 2. Database Security
- [ ] Use connection pooling with limits
- [ ] Enable database query logging
- [ ] Set up database backups with encryption
- [ ] Implement database connection encryption
- [ ] Regular security updates for database server
- [ ] Principle of least privilege for database users

### 3. Monitoring and Alerting
- [ ] Log all authentication events
- [ ] Monitor for unusual access patterns
- [ ] Set up alerts for failed login attempts
- [ ] Track API usage and rate limiting
- [ ] Monitor for security vulnerabilities
- [ ] Regular security audits and penetration testing

## Security Incident Response

### 1. Incident Categories
- **Authentication Bypass**: Unauthorized access to user accounts
- **Data Breach**: Unauthorized access to user financial data
- **System Compromise**: Server or application compromise
- **DDoS Attack**: Service availability issues

### 2. Response Procedures
1. **Immediate Response**: Isolate affected systems
2. **Assessment**: Determine scope and impact
3. **Containment**: Stop ongoing attack/breach
4. **Recovery**: Restore normal operations
5. **Lessons Learned**: Update security measures

### 3. Communication Plan
- Internal team notification procedures
- User notification for data breaches
- Regulatory compliance reporting
- Public communication guidelines

This comprehensive security framework ensures BudgetManager Pro maintains the highest standards of security for protecting user financial data and maintaining system integrity.

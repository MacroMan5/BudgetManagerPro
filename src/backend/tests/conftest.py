"""
Test configuration and fixtures
"""
import os
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test_budget_manager.db"

from app.main import app
from app.core.database import get_db, Base
from app.core.security import SecurityManager
from app.models.user import User


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_budget_manager.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create database session for testing"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create test client with database session override"""
    def get_test_db():
        return db_session
    
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data with unique email"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test-{unique_id}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def test_user(db_session: Session, test_user_data: Dict[str, Any]) -> User:
    """Create test user in database"""
    password_hash = SecurityManager.get_password_hash(test_user_data["password"])
    
    user = User(
        email=test_user_data["email"],
        password_hash=password_hash,
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"],
        is_active=True,
        is_superuser=False
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def test_superuser(db_session: Session) -> User:
    """Create test superuser in database"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    password_hash = SecurityManager.get_password_hash("SuperSecret123!")
    
    user = User(
        email=f"admin-{unique_id}@example.com",
        password_hash=password_hash,
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_superuser=True
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def auth_headers(client: TestClient, test_user: User, test_user_data: Dict[str, Any]) -> Dict[str, str]:
    """Get authentication headers for test user"""
    # Login with the existing test user
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
def superuser_headers(client: TestClient, test_superuser: User) -> Dict[str, str]:
    """Get authentication headers for superuser"""
    login_data = {
        "email": test_superuser.email,
        "password": "SuperSecret123!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    """Cleanup test files after testing"""
    yield
    # Clean up test database file
    try:
        import time
        import gc
        # Force garbage collection to close any database connections
        gc.collect()
        time.sleep(0.1)  # Give OS time to release file handles
        os.remove("test_budget_manager.db")
    except (FileNotFoundError, PermissionError):
        # File doesn't exist or is still in use - that's OK
        pass

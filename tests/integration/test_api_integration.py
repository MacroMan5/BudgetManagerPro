# Integration Tests for BudgetManager Pro

import pytest
import httpx
import asyncio
import json
from typing import Dict, Any

# Base URL for the API (configured via environment variable)
BASE_URL = "http://localhost:8000"

@pytest.fixture
async def api_client():
    """Create an async HTTP client for API testing."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client

@pytest.fixture
async def authenticated_client(api_client):
    """Create an authenticated API client."""
    # Register a test user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }
    
    response = await api_client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = await api_client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    token = token_data["access_token"]
    
    # Add authorization header
    api_client.headers.update({"Authorization": f"Bearer {token}"})
    
    return api_client

class TestHealthEndpoints:
    """Test health and monitoring endpoints."""
    
    async def test_health_endpoint(self, api_client):
        """Test the basic health endpoint."""
        response = await api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    async def test_api_health_endpoint(self, api_client):
        """Test the API-specific health endpoint."""
        response = await api_client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "redis" in data

class TestAuthenticationFlow:
    """Test the complete authentication flow."""
    
    async def test_user_registration(self, api_client):
        """Test user registration process."""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "full_name": "New User"
        }
        
        response = await api_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "password" not in data
    
    async def test_user_login(self, api_client):
        """Test user login process."""
        # First register a user
        user_data = {
            "email": "logintest@example.com",
            "password": "LoginPassword123!",
            "full_name": "Login Test User"
        }
        
        register_response = await api_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Then login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = await api_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    async def test_protected_endpoint_access(self, authenticated_client):
        """Test access to protected endpoints with authentication."""
        response = await authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "full_name" in data
        assert "id" in data

class TestAPIEndpoints:
    """Test main API endpoints."""
    
    async def test_api_documentation(self, api_client):
        """Test that API documentation is accessible."""
        response = await api_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    async def test_openapi_schema(self, api_client):
        """Test that OpenAPI schema is accessible."""
        response = await api_client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

class TestErrorHandling:
    """Test error handling and responses."""
    
    async def test_404_error(self, api_client):
        """Test 404 error handling."""
        response = await api_client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
    
    async def test_unauthorized_access(self, api_client):
        """Test unauthorized access to protected endpoints."""
        response = await api_client.get("/api/v1/auth/me")
        assert response.status_code == 401
        
        data = response.json()
        assert "detail" in data
    
    async def test_invalid_login_credentials(self, api_client):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
        
        response = await api_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        
        data = response.json()
        assert "detail" in data

class TestCORS:
    """Test CORS configuration."""
    
    async def test_cors_headers(self, api_client):
        """Test that CORS headers are properly set."""
        response = await api_client.options("/api/v1/health")
        assert response.status_code == 200
        
        # Check for CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers

class TestPerformance:
    """Test basic performance requirements."""
    
    async def test_health_endpoint_response_time(self, api_client):
        """Test that health endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = await api_client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    async def test_concurrent_requests(self, api_client):
        """Test handling of concurrent requests."""
        async def make_request():
            response = await api_client.get("/health")
            return response.status_code
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status == 200 for status in results)

# Pytest configuration for integration tests
pytestmark = pytest.mark.asyncio

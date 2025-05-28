# API Testing Strategy

## Overview

This project focuses on unit testing for API endpoints to ensure reliability and maintainability. The testing framework uses pytest with FastAPI's TestClient for API testing.

## Test Structure

```
tests/
├── conftest.py           # Shared test fixtures
└── api/                 # API endpoint tests
    ├── test_auth.py     # Authentication endpoints (login, register, etc.)
    ├── test_users.py    # User management endpoints
    └── test_ping.py     # Health check endpoint
```

## API Testing

### 1. Test Organization

- Each API module should have a corresponding test file
- Test files should be named `test_*.py`
- Test functions should be named `test_*`
- Group related tests in classes

### 2. Test Structure

```python
# Example API test structure
def test_create_user(client, db_session):
    # Arrange
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    
    # Act
    response = client.post("/api/v1/users/", json=user_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

### 3. Test Categories

1. **Authentication Tests** (`test_auth.py`):
   - Login endpoint
   - Registration endpoint
   - Token validation
   - Password reset
   - Refresh token

2. **User Management Tests** (`test_users.py`):
   - User creation
   - User update
   - User deletion
   - User profile
   - User listing

3. **Health Check Tests** (`test_ping.py`):
   - Ping endpoint
   - API version check

### 4. Best Practices

1. **Test Isolation**:
   - Each test should be independent
   - Use fixtures for setup and teardown
   - Clean up test data after each test
   - Use test database

2. **Mocking**:
   - Mock external services
   - Mock email sending
   - Mock file operations
   - Mock time-dependent functions

3. **Assertions**:
   - Check status codes
   - Verify response structure
   - Validate error messages
   - Test edge cases

## Running Tests

### 1. Run All Tests
```bash
pytest
```

### 2. Run Specific API Tests
```bash
pytest tests/api/test_auth.py
pytest tests/api/test_users.py
pytest tests/api/test_ping.py
```

### 3. Run with Coverage
```bash
pytest --cov=app tests/
```

## Test Coverage

- Maintain minimum 80% code coverage for API endpoints
- Focus on critical endpoints
- Cover error scenarios
- Document uncovered endpoints with reasons

## Common Test Patterns

### 1. Authentication Tests
```python
def test_login_success(client):deco
    # Arrange
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    # Act
    response = client.post("/api/v1/auth/login", json=login_data)
    
    # Assert
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 2. User Management Tests
```python
def test_create_user(client):
    # Arrange
    user_data = {
        "email": "new@example.com",
        "password": "newpassword",
        "full_name": "New User"
    }
    
    # Act
    response = client.post("/api/v1/users/", json=user_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

### 3. Health Check Tests
```python
def test_ping(client):
    # Act
    response = client.get("/api/v1/ping")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["ping"] == "pong"
```

## Test Fixtures

### 1. Client Fixture
```python
@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client
```

### 2. Database Fixture
```python
@pytest.fixture
def db_session():
    # Setup test database
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
```

### 3. Authentication Fixture
```python
@pytest.fixture
def auth_headers(client):
    # Get authentication token
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## Troubleshooting

1. **Test Failures**:
   - Check request data
   - Verify database state
   - Check authentication
   - Review error messages

2. **Slow Tests**:
   - Optimize database operations
   - Use appropriate fixtures
   - Consider parallel execution

3. **Intermittent Failures**:
   - Check for race conditions
   - Verify test isolation
   - Review async operations
   - Check resource cleanup 
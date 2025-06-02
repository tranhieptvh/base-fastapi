# Testing Strategy

## Overview

The project uses pytest for testing with a dedicated test database. The test environment is configured in `.env.test` and uses the following components:

- Test database (MySQL)
- Test client (FastAPI TestClient)
- Fixtures for common test scenarios
- Automatic database cleanup after tests

## Test Environment

### 1. Test Environment Configuration
- Test environment variables are loaded from `.env.test`
- Test database settings are configured in `conftest.py`
- Test database is automatically managed by fixtures

### 2. Test Database Lifecycle
```python
# 1. Session Setup (before all tests)
@pytest.fixture(scope="session")
def engine():
    # Create test database
    # Create all tables
    # Return engine for test session

# 2. Test Setup (before each test)
@pytest.fixture(scope="function")
def db_session(engine):
    # Create new session
    # Start transaction
    # Yield session for test
    # Rollback transaction after test

# 3. Test Cleanup (after all tests)
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db(engine):
    # Drop test database
    # Clean up resources
```

### 3. Test Database Configuration
- Database Name: `test_fastapi_db`
- Host: `db`
- Port: `3306`
- User: `root`
- Password: `root`

## Test Structure

```
.
├── .env.test           # Test environment variables
├── src/
│   ├── db/
│   │   └── init_test_db.py  # Test database initialization
│   └── ...
└── tests/              # Test files
    ├── api/           # API endpoint tests
    │   └── test_auth.py   # Authentication tests
    └── conftest.py    # Test configuration and fixtures
```

## Available Fixtures

### 1. Database Fixtures
- `engine`: Test database engine
- `db_session`: Database session with transaction rollback
- `cleanup_test_db`: Automatic database cleanup

### 2. Authentication Fixtures
- `test_role`: Test role creation
- `test_user`: Test user creation
- `test_inactive_user`: Test inactive user creation
- `test_user_token`: JWT token for test user
- `auth_headers`: Authentication headers
- `expired_token`: Expired JWT token

### 3. Client Fixtures
- `client`: FastAPI TestClient with database session

## Running Tests

```bash
# Inside the application container
make exec

# Run all tests
pytest

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/api/test_auth.py

# Run specific test function
pytest tests/api/test_auth.py::test_register_success

# Run tests with verbose output
pytest -v

# Run tests and show print statements
pytest -s
```

## Writing Tests

### 1. Test Structure
```python
def test_feature_name(client, db_session):
    # Arrange
    # Setup test data
    
    # Act
    # Perform the action being tested
    
    # Assert
    # Verify the results
```

### 2. Example Test
```python
def test_register_success(client, db_session, test_role):
    # Arrange
    input_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "Test123!@#",
        "role_id": test_role.id
    }
    
    # Act
    response = client.post("/auth/register", json=input_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == input_data["email"]
```

## Test Coverage

The project uses pytest-cov for test coverage reporting. To generate a coverage report:

```bash
# Generate coverage report
pytest --cov=src tests/ --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src tests/ --cov-report=html
```

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for common setup
- Clean up after each test

### 2. Database Testing
- Use transactions for test isolation
- Roll back changes after each test
- Use test-specific database

### 3. Authentication Testing
- Test both authenticated and unauthenticated scenarios
- Verify token validation
- Test error cases

### 4. API Testing
- Test all HTTP methods
- Verify response status codes
- Check response data structure
- Test error handling

## Troubleshooting

### 1. Common Issues
- Database connection problems
- Authentication failures
- Test isolation issues
- Resource cleanup problems

### 2. Debugging Tips
- Use `pytest -s` to see print statements
- Check database state after failed tests
- Verify fixture setup
- Review test logs

### 3. Performance Optimization
- Use appropriate fixture scopes
- Optimize database operations
- Consider parallel test execution
- Clean up resources properly 
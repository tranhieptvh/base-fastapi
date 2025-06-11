# Testing Strategy

## Overview

The project uses pytest for testing with a dedicated test database. The test environment is configured in `.env.test` and uses the following components:

- Test database (MySQL/PostgreSQL, based on config)
- Test client (FastAPI TestClient)
- Fixtures for common test scenarios
- Automatic database creation and cleanup after tests

## Test Environment

### 1. Test Environment Configuration
- Test environment variables are loaded from `.env.test` when running locally (this step is skipped in CI environments).
- Test database settings are configured in `conftest.py` using the `DATABASE_URL` from `.env.test`.
- The test database is automatically created, managed, and dropped by fixtures.

### 2. Test Database Lifecycle
```python
# 1. Session Setup (before all tests)
@pytest.fixture(scope="session")
def engine():
    # Create test database if not exists
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
    # Yield to run all tests
    # Drop test database
    # Clean up resources
```

### 3. Test Database Configuration
- The test database connection is managed by the `DATABASE_URL` variable in the `.env.test` file.
- The `engine` fixture in `conftest.py` reads this URL to create and manage the test database.

## Test Structure

```
.
├── .env.test           # Test environment variables
├── src/
│   └── ...
└── tests/              # Test files
    ├── api/            # API endpoint tests
    │   ├── test_auth.py  # Authentication tests
    │   └── test_users.py # User management tests
    └── conftest.py     # Test configuration and fixtures
```

## Available Fixtures

### 1. Database Fixtures
- `engine`: (Scope: session) Test database engine.
- `db_session`: (Scope: function) Database session with automatic transaction rollback after each test.
- `cleanup_test_db`: (Scope: session) Automatically creates the DB before tests and drops it after.

### 2. User & Role Fixtures
- `admin_role`: (Scope: session) Creates the 'admin' role.
- `admin_user`: (Scope: session) Creates a test user with admin privileges.
- `normal_user_role`: (Scope: session) Creates the standard 'user' role.
- `normal_user`: (Scope: session) Creates a standard, active test user.
- `normal_inactive_user`: (Scope: session) Creates a standard, inactive test user.

### 3. Authentication Fixtures
- `admin_auth_header`: (Scope: function) Returns authentication headers for the `admin_user`.
- `normal_user_auth_header`: (Scope: function) Returns authentication headers for the `normal_user`.
- `expired_normal_user_token_header`: (Scope: function) Returns expired authentication headers for a normal user.

### 4. Client Fixtures
- `client`: (Scope: function) FastAPI TestClient with the database session dependency overridden.

## Running Tests

```bash
# Inside the application container
make exec

# Run all tests
pytest

# Run with coverage report
pytest --cov=src tests/

# Run a specific test file
pytest tests/api/test_auth.py

# Run all tests in a directory
pytest tests/api/

# Run a specific test function
pytest tests/api/test_auth.py::test_register_success

# Run tests with verbose output
pytest -v

# Run tests and show print statements
pytest -s
```

## Writing Tests

### 1. Test Structure
```python
def test_feature_name(client, db_session, some_fixture):
    # Arrange
    # Setup test data, if not handled by fixtures
    
    # Act
    # Perform the action being tested using the client
    
    # Assert
    # Verify the results, status code, and response data
```

### 2. Example Test
```python
def test_register_success(client, db_session, normal_user_role):
    # Arrange
    input_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "Test123!@#",
        "role_id": normal_user_role.id
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
# FastAPI Base Project Documentation

## Project Overview

This is a modern FastAPI project template that provides a solid foundation for building scalable and maintainable APIs. The project uses Python 3.12 and follows best practices for API development.

## Key Features

- **Modern Stack**: FastAPI, SQLAlchemy, Pydantic, Poetry
- **Authentication**: JWT-based authentication with password reset
- **Database**: SQLAlchemy ORM with Alembic migrations
- **Code Quality**: Black, isort, Flake8
- **Testing**: pytest with coverage reporting
- **Documentation**: Auto-generated OpenAPI documentation
- **Containerization**: Docker and Docker Compose support

## Detail Project Structure

```
.
├── src/                    # Application source code
│   ├── api/               # API layer
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── users.py       # User management endpoints
│   │   ├── ping.py        # Health check endpoint
│   │   └── __init__.py    # API router configuration
│   ├── core/              # Core functionality
│   │   ├── config.py      # Application configuration
│   │   ├── security.py    # Security utilities (JWT, password hashing)
│   │   ├── middleware.py  # Custom middleware
│   │   ├── exceptions.py  # Custom exceptions
│   │   ├── response.py    # Response models
│   │   ├── enums.py      # Enum definitions
│   │   └── __init__.py
│   ├── db/               # Database layer
│   │   ├── base.py       # SQLAlchemy base
│   │   ├── session.py    # Database session management
│   │   ├── init_db.py    # Database initialization
│   │   ├── init_test_db.py # Test database initialization
│   │   ├── models/       # Database models
│   │   │   ├── user.py   # User model
│   │   │   └── role.py   # Role model
│   │   ├── seeders/      # Database seeders
│   │   │   ├── base.py   # Base seeder class
│   │   │   ├── role_seeder.py
│   │   │   └── user_seeder.py
│   │   └── __init__.py
│   ├── dependencies/     # Dependency injection
│   │   ├── __init__.py   # Dependency exports
│   │   ├── auth.py       # Authentication dependencies
│   │   └── db.py         # Database dependencies
│   ├── schemas/          # Pydantic schemas
│   │   ├── token.py      # Token schemas
│   │   └── user.py       # User schemas
│   ├── services/         # Business logic layer
│   │   └── user.py       # User business logic
│   ├── tasks/            # Celery tasks
│   │   └── __init__.py   # Task configuration
│   ├── templates/        # Email templates
│   │   └── email/        # Email HTML templates
│   ├── docs/             # Project documentation
│   │   └── README.md     # This documentation file
│   ├── main.py          # Application entry point
│   └── __init__.py
├── tests/                # Test files
│   ├── api/             # API tests
│   │   └── test_auth.py # Authentication tests
│   └── conftest.py      # Test configuration
├── migrations/          # Database migrations
│   └── versions/        # Migration versions
├── .env                 # Environment variables
├── .env.example         # Example environment variables
├── .env.test           # Test environment variables
├── alembic.ini         # Alembic configuration
├── pyproject.toml      # Poetry configuration
├── poetry.lock         # Poetry lock file
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── Makefile          # Development commands
└── .dockerignore     # Docker ignore file
```

## API Endpoints

The API is organized into the following main routes:

1. **Health Check**
   - Endpoint: `/ping`
   - Purpose: Verify API availability
   - Tags: `ping`

2. **Authentication**
   - Base Path: `/auth`
   - Features: Login, registration, password reset
   - Tags: `auth`

3. **User Management**
   - Base Path: `/users`
   - Features: User CRUD operations
   - Tags: `users`

## Middleware

The project includes several middleware components to enhance security and functionality:

1. **CORS Middleware**
   - Handles Cross-Origin Resource Sharing
   - Configurable allowed origins, methods, and headers
   - Secure by default with strict settings
   - Location: `src/main.py`
   - Usage: Applied globally to all routes

2. **Authentication Middleware**
   - JWT token validation
   - User session management
   - Role-based access control
   - Location: `src/dependencies/auth.py`
   - Usage: Applied via dependency injection `@Depends(get_current_user)`

3. **Error Handling Middleware**
   - Global exception handling
   - Standardized error responses
   - Detailed error logging
   - Location: `src/core/exceptions.py`
   - Usage: Registered in `src/main.py`

4. **Validation Exception Handler**
   - Custom handler for Pydantic validation errors
   - Location: `src/core/middleware.py`
   - Usage: Registered in `src/main.py` as exception handler
   - Transforms validation errors into standardized format:
     ```json
     {
         "status": "error",
         "message": "Validation error",
         "errors": {
             "fields": [
                 {
                     "field": "email",
                     "message": "invalid email format",
                     "type": "value_error.email"
                 }
             ]
         }
     }
     ```
   - Features:
     - Automatic field name extraction from error location
     - Consistent error response structure
     - Detailed validation error messages
     - HTTP 422 status code for validation errors
     - Support for multiple field errors in a single response

## Request & Response Handling

### Request Validation
- Pydantic models for request validation
- Automatic type conversion
- Custom validators for complex rules
- Detailed error messages for invalid inputs

### Response Models

1. **BaseResponse**
   ```python
   class BaseResponse(BaseModel):
       status: str
       message: str
   ```

2. **SuccessResponse**
   ```python
   class SuccessResponse(BaseResponse, Generic[T]):
       status: str = "success"
       message: str = "Success"
       data: Optional[T] = None
   ```

3. **ErrorResponse**
   ```python
   class ErrorResponse(BaseResponse):
       status: str = "error"
       message: str = "Error"
       errors: Dict[str, Any] = {}
   ```

### Response Format

1. **Success Response**
   ```json
   {
       "status": "success",
       "message": "Success",
       "data": {
           // Response data here
       }
   }
   ```

2. **Error Response**
   ```json
   {
       "status": "error",
       "message": "Error message",
       "errors": {
           // Additional error details
       }
   }
   ```

### Helper Functions

1. **success_response**
   ```python
   def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]
   ```
   - Creates a standardized success response
   - Optional data and custom message
   - Returns dictionary format

2. **error_response**
   ```python
   def error_response(message: str = "Error", errors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
   ```
   - Creates a standardized error response
   - Optional error details and custom message
   - Returns dictionary format

## Development Setup

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Make (optional, for using Makefile commands)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Configure environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env file with your configuration
   nano .env
   ```

3. **Build and start services**
   ```bash
   # Build all services
   make build

   # Start main services (app and database)
   make up

   # Start background workers (Celery worker and beat)
   make up-worker
   ```

### Available Services

1. **FastAPI Application**
   - Container: `fastapi_app`
   - Port: 8000 (API)
   - Port: 5678 (Debug)
   - Hot reload enabled
   - Debug mode enabled

2. **MySQL Database**
   - Container: `fastapi_db`
   - Port: 3307 (mapped to 3306)
   - Persistent volume for data
   - Health checks enabled

3. **Redis**
   - Container: `fastapi_redis`
   - Port: 6379
   - Used for Celery broker
   - Health checks enabled

4. **Celery Worker**
   - Container: `fastapi_worker`
   - Handles background tasks
   - Email queue processing

5. **Celery Beat**
   - Container: `fastapi_beat`
   - Handles scheduled tasks

### Development Commands

```bash
# Start all services
make up

# Stop all services
make down

# Restart services
make restart

# Access application container
make exec

# Start background workers
make up-worker

# Stop background workers
make down-worker

# Clean up (removes containers, volumes, and images)
make clean
```

### Database Management

1. **Run migrations**
   ```bash
   # Inside the application container
   make exec
   alembic upgrade head
   ```

2. **Seed initial data**
   ```bash
   # Inside the application container
   make exec
   python -m src.db.init_db
   ```

### Accessing Services

- API Documentation: `http://localhost:8000/docs`
- API ReDoc: `http://localhost:8000/redoc`
- Database: `localhost:3307`
- Redis: `localhost:6379`

## Testing

### Test Environment

The project uses pytest for testing with a dedicated test database. The test environment is configured in `.env.test` and uses the following components:

- Test database (MySQL)
- Test client (FastAPI TestClient)
- Fixtures for common test scenarios
- Automatic database cleanup after tests

### Setup Testing

1. **Environment Setup**
   - Review test environment configuration in `.env.test`
   - Ensure test database credentials are correct

2. **Database Setup**
   ```bash
   # Access application container
   make exec

   # Create and migrate test database
   DATABASE_URL="mysql+pymysql://root:root@db/test_fastapi_db" alembic upgrade head

   # Initialize test database with seed data
   python -m src.db.init_test_db

   # When database updated with new migrations -> update DB Structure
   DATABASE_URL="mysql+pymysql://root:root@db/test_fastapi_db" alembic upgrade head
   ```

3. **Test Database Configuration**
   - Database Name: `test_fastapi_db`
   - Host: `db`
   - Port: `3306`
   - User: `root`
   - Password: `root`

4. **Verify Setup**
   - Check database connection
   - Verify migrations are applied
   - Confirm test data is seeded

### Running Tests

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

### Test Structure

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

### Available Fixtures

1. **Database Fixtures**
   - `engine`: Test database engine
   - `db_session`: Database session with transaction rollback
   - `cleanup_test_db`: Automatic database cleanup

2. **Authentication Fixtures**
   - `test_role`: Test role creation
   - `test_user`: Test user creation
   - `test_user_token`: JWT token for test user
   - `auth_headers`: Authentication headers
   - `expired_token`: Expired JWT token

3. **Client Fixtures**
   - `client`: FastAPI TestClient with database session

### Writing Tests

1. **Test Structure**
   ```python
   def test_feature_name(client, db_session):
       # Arrange
       # Setup test data
       
       # Act
       # Perform the action being tested
       
       # Assert
       # Verify the results
   ```

2. **Example Test**
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

### Test Coverage

The project uses pytest-cov for test coverage reporting. To generate a coverage report:

```bash
# Generate coverage report
pytest --cov=src tests/ --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src tests/ --cov-report=html
```

### Best Practices

1. **Test Isolation**
   - Each test should be independent
   - Use fixtures for common setup
   - Clean up after each test

2. **Database Testing**
   - Use transactions for test isolation
   - Roll back changes after each test
   - Use test-specific database

3. **Authentication Testing**
   - Test both authenticated and unauthenticated scenarios
   - Verify token validation
   - Test error cases

4. **API Testing**
   - Test all HTTP methods
   - Verify response status codes
   - Check response data structure
   - Test error handling

## Code Quality

The project uses several tools to maintain code quality. All commands should be run inside the application container:

```bash
# Access the application container
make exec

# Format code with Black
black .

# Sort imports with isort
isort .

# Lint code with flake8
flake8

# Run all code quality checks
black . && isort . && flake8
```

### Code Quality Tools

1. **Black**
   - Python code formatter
   - Enforces consistent code style
   - Config: `pyproject.toml`

2. **isort**
   - Import sorter
   - Organizes imports into sections
   - Config: `pyproject.toml`

3. **flake8**
   - Code linter
   - Checks for style and potential errors
   - Config: `.flake8`

## API Documentation

Once the server is running, access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Security Best Practices

1. **Authentication**
   - JWT tokens with expiration
   - Secure password hashing with bcrypt
   - Rate limiting on auth endpoints

2. **Data Protection**
   - Input validation with Pydantic
   - SQL injection prevention with SQLAlchemy
   - XSS protection

3. **Environment**
   - Sensitive data in environment variables
   - Production/development configuration separation
   - Secure headers configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License. 
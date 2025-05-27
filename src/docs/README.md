# FastAPI Base Project Documentation

## Project Overview

This is a modern FastAPI project template that provides a solid foundation for building scalable and maintainable APIs. The project uses Python 3.12 and follows best practices for API development.

## Key Features

- **Modern Stack**: FastAPI, SQLAlchemy, Pydantic, Poetry
- **Authentication**: JWT-based authentication with password reset
- **Database**: SQLAlchemy ORM with Alembic migrations
- **Code Quality**: Black, Isort, Flake8
- **Testing**: Pytest with coverage reporting
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
│   │   ├── init_db.py    # Database initialization
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
├── alembic/             # Database migrations
│   ├── versions/        # Migration versions
│   └── env.py          # Migration environment
├── .env                 # Environment variables
├── .env.example         # Example environment variables
├── alembic.ini          # Alembic configuration
├── pyproject.toml       # Poetry configuration
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Docker Compose configuration
```

## Authentication Flow

1. **Registration**
   - User registers with email and password
   - System creates user account
   - Returns success message

2. **Login**
   - User provides credentials
   - System validates and returns JWT token
   - Token used for subsequent requests

3. **Password Management**
   - Password reset request via email
   - Password reset confirmation with token
   - Password update for authenticated users

4. **Logout**
   - Invalidates current session
   - Clears client-side tokens

## Middleware

The project includes several middleware components to enhance security and functionality:

1. **CORS Middleware**
   - Handles Cross-Origin Resource Sharing
   - Configurable allowed origins, methods, and headers
   - Secure by default with strict settings
   - Location: `app/main.py`
   - Usage: Applied globally to all routes

2. **Authentication Middleware**
   - JWT token validation
   - User session management
   - Role-based access control
   - Location: `app/dependencies/auth.py`
   - Usage: Applied via dependency injection `@Depends(get_current_user)`

3. **Error Handling Middleware**
   - Global exception handling
   - Standardized error responses
   - Detailed error logging
   - Location: `app/core/exceptions.py`
   - Usage: Registered in `app/main.py`

4. **Validation Exception Handler**
   - Custom handler for Pydantic validation errors
   - Location: `app/core/middleware.py`
   - Usage: Registered in `app/main.py` as exception handler
   - Transforms validation errors into standardized format consistent with ErrorResponse:
     ```json
     {
         "status": "error",
         "error": {
             "message": "Validation error",
             "code": "VALIDATION_ERROR",
             "details": {
                 "fields": [
                     {
                         "field": "email",
                         "message": "invalid email format",
                         "type": "value_error.email"
                     }
                 ]
             }
         }
     }
     ```
   - Provides clear error messages for:
     - Invalid data types
     - Missing required fields
     - Format validation (email, password, etc.)
     - Custom validation rules
   - Maintains consistent error response structure with ErrorResponse
   - Improves API documentation with clear error examples

## Request & Response Handling

### Request Validation
- Pydantic models for request validation
- Automatic type conversion
- Custom validators for complex rules
- Detailed error messages for invalid inputs

### Response Format
```json
{
    "status": "success",
    "data": {
        // Response data here
    },
    "message": "Operation completed successfully"
}
```

### Error Response Format
```json
{
    "status": "error",
    "error": {
        "message": "Error description",
        "code": "ERROR_CODE",
        "details": {
            // Additional error details
        }
    }
}
```

### Response Models
1. **SuccessResponse**
   - Generic type for data
   - Optional message field
   - Consistent success status

2. **ErrorResponse**
   - Standardized error format
   - HTTP status code mapping
   - Detailed error information

## Development Setup

1. **Environment Setup**
   ```bash
   # Install Python 3.12
   sudo apt update
   sudo apt install python3.12 python3.12-venv

   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -

   # Install dependencies
   poetry install
   ```

2. **Database Setup**
   ```bash
   # Run migrations
   poetry run alembic upgrade head

   # Seed initial data
   poetry run python -m src.db.init_db
   ```

3. **Run Development Server**
   ```bash
   poetry run uvicorn src.main:app --reload
   ```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app tests/

# Run specific test
poetry run pytest tests/test_file.py::test_function
```

## Code Quality

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Lint code
poetry run flake8
```

## Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build
```

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
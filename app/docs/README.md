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
app/
├── api/
│   ├── api_v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   └── users.py     # User management endpoints
│   │   └── api.py          # API router configuration
│   └── __init__.py
├── core/
│   ├── config.py           # Application configuration
│   ├── security.py         # Security utilities
│   ├── middleware.py       # Custom middleware
│   ├── exceptions.py       # Custom exceptions
│   ├── response.py         # Response models
│   └── __init__.py
├── db/
│   ├── base.py            # SQLAlchemy base
│   ├── init_db.py         # Database initialization
│   ├── models/            # Database models
│   ├── seeders/           # Database seeders
│   └── __init__.py
├── dependencies/
│   ├── __init__.py        # Dependency exports
│   ├── auth.py            # Authentication dependencies
│   └── db.py              # Database dependencies
├── schemas/
│   ├── token.py           # Token schemas
│   └── user.py            # User schemas
├── services/
│   └── user.py            # User business logic
├── docs/                  # Project documentation
└── __init__.py
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

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `POST /api/v1/auth/password-reset` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Reset password
- `POST /api/v1/auth/password/update` - Update password
- `POST /api/v1/auth/logout` - Logout user

### Users

- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

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
   poetry run python -m app.db.init_db
   ```

3. **Run Development Server**
   ```bash
   poetry run uvicorn app.main:app --reload
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
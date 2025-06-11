# FastAPI Base Project Documentation

## Project Overview

This is a modern FastAPI project template that provides a solid foundation for building scalable and maintainable APIs. The project uses Python 3.12 and follows best practices for API development.

## Key Features

- **Modern Stack**: FastAPI, SQLAlchemy, Pydantic, Poetry
- **Authentication**: JWT-based authentication
- **Database**: SQLAlchemy ORM with Alembic migrations
- **Code Quality**: Black, isort, Flake8, mypy
- **Testing**: pytest with coverage reporting
- **Documentation**: Auto-generated OpenAPI documentation
- **Containerization**: Docker and Docker Compose support
- **Logging**: Comprehensive logging system with daily rotation
- **Async Tasks**: Celery with Redis for background jobs.

## Detail Project Structure

```
.
├── .github/              # GitHub Actions workflows
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
│   │   ├── logging.py     # Logging configuration
│   │   ├── enums.py      # Enum definitions
│   │   └── __init__.py
│   ├── db/               # Database layer
│   │   ├── base.py       # SQLAlchemy base
│   │   ├── session.py    # Database session management
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
│   │   ├── README.md     # Main documentation file
│   │   └── architecture/ # Architecture documentation
│   │       ├── core/           # Core system documentation
│   │       │   ├── core_concept.md    # Core concepts
│   │       │   ├── middleware.md      # Middleware system
│   │       │   ├── request_response.md # Request/Response handling
│   │       │   └── logging.md         # Logging system
│   │       ├── data/           # Data and storage documentation
│   │       │   └── batch.md           # Batch processing
│   │       ├── security/       # Security documentation
│   │       │   └── auth.md            # Authentication system
│   │       ├── communication/  # Communication documentation
│   │       │   └── email_system.md    # Email system
│   │       └── devops/         # Development and operations
│   │           ├── debug.md           # Debugging guide
│   │           ├── testing.md         # Testing strategy
│   │           └── ci_cd.md           # CI/CD pipeline
│   ├── main.py          # Application entry point
│   └── __init__.py
├── logs/                 # Application logs
│   ├── YYYY-MM-DD.log   # Current day's log file
│   ├── YYYY-MM-DD.log.1 # Previous day's log file
│   └── YYYY-MM-DD.log.2 # Two days ago log file
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


## Middleware

For detailed information about middleware components, their configuration, and best practices, please refer to the [Middleware Documentation](architecture/core/middleware.md).

## Request & Response Handling

For detailed information about request validation, response formatting, and best practices, please refer to the [Request & Response Documentation](architecture/core/request_response.md).

## Development Setup

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Make (optional, for using Makefile commands)
- Poetry for dependency management

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

3. **Create new migration**
   ```bash
   # Inside the application container
   make exec
   alembic revision --autogenerate -m "description of changes"
   ```

4. **Rollback migration**
   ```bash
   # Rollback one step
   make exec
   alembic downgrade -1

   # Rollback to specific version
   make exec
   alembic downgrade <revision_id>

   # Rollback all migrations
   make exec
   alembic downgrade base
   ```

5. **View migration history**
   ```bash
   # List all migrations
   make exec
   alembic history

   # Show current migration version
   make exec
   alembic current
   ```

6. **Database backup and restore**
   ```bash
   # Backup database
   docker exec -t base-fastapi-db-1 mysqldump -u root -proot base > backup.sql

   # Restore database
   cat backup.sql | docker exec -i base-fastapi-db-1 mysql -u root -proot base
   ```

7. **Reset database**
   ```bash
   # Drop and recreate database
   make exec
   python -m src.db.reset_db

   # Reinitialize database with migrations and seed data
   make exec
   python -m src.db.init_db
   ```

8. **Test database management**
   The test database is now automatically created and destroyed by the `pytest` test suite. There are no manual scripts needed. Please see the [Testing Documentation](architecture/devops/testing.md) for more details.

9. **Database connection**
   ```bash
   # Connect to MySQL container
   docker exec -it base-fastapi-db-1 mysql -u root -proot

   # List databases
   SHOW DATABASES;

   # Use database
   USE base;

   # Show tables
   SHOW TABLES;

   # Describe table
   DESCRIBE table_name;
   ```

10. **Database monitoring**
    ```bash
    # View database logs
    docker logs base-fastapi-db-1

    # Monitor database processes
    docker exec -it base-fastapi-db-1 mysqladmin -u root -proot processlist

    # Check database status
    docker exec -it base-fastapi-db-1 mysqladmin -u root -proot status
    ```

### Accessing Services

- API Documentation: `http://localhost:8000/docs`
- API ReDoc: `http://localhost:8000/redoc`
- Database: `localhost:3307`
- Redis: `localhost:6379`

## Testing

For detailed information about testing strategy, test organization, and best practices, please refer to the [Testing Documentation](architecture/devops/testing.md).

## Continuous Integration & Deployment (CI/CD)

This project uses [GitHub Actions](.github/) for Continuous Integration. The CI pipeline ensures code quality by automatically running tests for every pull request targeting the `develop` and `main` branches.

For a detailed explanation of the CI/CD strategy, workflow configuration, and branch protection rules, please refer to the [**CI/CD Documentation**](architecture/devops/ci_cd.md).

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
# Base FastAPI Project

A base FastAPI project with SQLAlchemy, Alembic, and JWT authentication.

## Features

- **Framework**: FastAPI for high-performance APIs.
- **Database**: SQLAlchemy ORM with Alembic for migrations.
- **Authentication**: JWT token authentication.
- **Async Tasks**: Celery with Redis for background jobs.
- **Containerization**: Docker and Docker Compose for easy setup and deployment.
- **Dependency Management**: Poetry for managing project dependencies.
- **Configuration**: Centralized settings management using python-dotenv.
- **Code Quality**: Pre-configured with Black, isort, flake8, and mypy.
- **Testing**: Pytest for unit and integration testing.
- **Email**: Email integration with FastAPI-mail.
- **Logging**: Comprehensive logging system with daily rotation.

## Development

This project uses Poetry for dependency management and includes development tools:
- black: Code formatting
- isort: Import sorting
- flake8: Code linting
- mypy: Type checking
- pytest: Testing

## Project Structure

```
.
├── .github/              # GitHub Actions workflows
├── logs/                 # Application logs
│   └── YYYY-MM-DD.log    # Daily log files
├── migrations/           # Database migrations (Alembic)
├── src/                  # Application source code
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality
│   ├── db/               # Database models and session
│   ├── dependencies/     # Application dependencies
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   ├── tasks/            # Celery tasks
│   ├── templates/        # Email templates
│   └── docs/             # Project documentation
├── tests/                # Test files
│   ├── api/              # API tests
│   └── conftest.py       # Test configuration
├── .dockerignore         # Docker ignore file
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
├── alembic.ini           # Alembic configuration
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker configuration
├── Makefile              # Makefile for common commands
├── poetry.lock           # Poetry lock file
└── pyproject.toml        # Poetry configuration and dependencies
```

## Setup with Docker

1. Copy `.env.example` to `.env` and update the variables:
```bash
cp .env.example .env
```

2. Build and start the containers:
```bash
docker-compose up --build
```

3. To run in detached mode:
```bash
docker-compose up -d
```

4. To stop the containers:
```bash
docker-compose down
```

## Manual Setup (without Docker)

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
poetry install
```

3. Copy `.env.example` to `.env` and update the variables:
```bash
cp .env.example .env
```

4. Run the application:
```bash
poetry run uvicorn src.main:app --reload
```

## Development

- API documentation will be available at `/docs`
- Alternative API documentation at `/redoc`
- Run tests with: `poetry run pytest`

## Docker Commands

- View logs:
```bash
docker-compose logs -f
```

- Rebuild containers:
```bash
docker-compose up --build
```

- Stop and remove containers:
```bash
docker-compose down
```

- Remove volumes:
```bash
docker-compose down -v
``` 
# FastAPI Project

This is a modern FastAPI project with a well-organized structure.

## Project Structure

```
.
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API endpoints
│   ├── core/            # Core functionality
│   ├── db/              # Database models and session
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── tests/               # Test files
├── .env                 # Environment variables
├── .env.example         # Example environment variables
├── alembic.ini          # Alembic configuration
├── main.py             # Application entry point
├── requirements.txt     # Project dependencies
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Docker Compose configuration
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
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update the variables:
```bash
cp .env.example .env
```

4. Run the application:
```bash
uvicorn main:app --reload
```

## Development

- API documentation will be available at `/docs`
- Alternative API documentation at `/redoc`
- Run tests with: `pytest`

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
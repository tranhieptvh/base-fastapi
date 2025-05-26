FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Update lock file and install dependencies
RUN poetry lock && poetry install --no-interaction --no-ansi --no-root

# Copy project files
COPY . .

# Expose ports
EXPOSE 8000 5678 
# CI/CD Strategy

## Overview

This project uses GitHub Actions for Continuous Integration and Continuous Deployment.
- **Continuous Integration (CI)**: The CI pipeline ensures code quality by running all tests before allowing merges to protected branches (develop and main).
- **Continuous Deployment (CD)**: The CD pipeline automates the deployment of the application to a production environment after changes are merged into the `main` branch.

## Continuous Integration (CI)

### 1. GitHub Actions Workflow

### 1. Pull Request Workflow

```yaml
name: Pull Request Checks

on:
  pull_request:
    branches: [ develop, main ]

jobs:
  test:
    runs-on: ubuntu-latest

    # Provide a MySQL database service
    services:
      db:
        image: mysql:8.0
        # Set environment variables for the database service
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
        # Health check to ensure the database is ready before tests run
        options: >-
          --health-cmd="mysqladmin ping -h localhost --silent"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3

    # Define environment variables for all steps in this job
    env:
      MYSQL_HOST: 127.0.0.1
      MYSQL_PORT: 3306
      MYSQL_USER: root
      MYSQL_PASSWORD: root
      MYSQL_DATABASE: test_db
      MYSQL_ROOT_PASSWORD: root
      
      # Dummy mail settings to satisfy Pydantic settings
      MAIL_USERNAME: "test@example.com"
      MAIL_PASSWORD: "password"
      MAIL_FROM: "test@example.com"
      MAIL_FROM_NAME: "Test Sender"

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          
      - name: Install dependencies
        run: poetry install
        
      - name: Run all tests
        run: poetry run pytest tests/
```

## Continuous Deployment (CD) Strategy

This section outlines a strategy for automatically deploying the application to a production server when code is pushed to the `main` branch.

### 1. Deployment Trigger
The deployment workflow is triggered automatically on every `push` to the `main` branch. This typically happens after a pull request from `develop` is successfully merged.

### 2. Deployment Workflow Example
Below is an example of a new workflow file, which you can create at `.github/workflows/deploy.yml`.

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/your-app-name:latest

      - name: Deploy to Server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /path/to/your/project
            docker-compose pull
            docker-compose up -d
            docker image prune -f
```

### 3. Workflow Explanation
1.  **Checkout code**: The workflow checks out the latest code from the `main` branch.
2.  **Log in to Docker Hub**: It securely logs into a container registry (like Docker Hub) using credentials stored in GitHub Secrets.
3.  **Build and push Docker image**: It builds a new Docker image from the `Dockerfile` and pushes it to the registry, tagging it as `latest`.
4.  **Deploy to Server**: It uses SSH to connect to the production server and runs a script to:
    - Navigate to the project directory.
    - `docker-compose pull`: Pull the latest image that was just pushed.
    - `docker-compose up -d`: Restart the services with the new image.
    - `docker image prune -f`: (Optional) Clean up old, unused Docker images to save space.

### 4. Server Prerequisites
For this deployment strategy to work, your production server must have:
- **Docker** installed.
- **Docker Compose** installed.
- An SSH user configured for access from GitHub Actions.
- The project's `docker-compose.yml` file must be present on the server.

### 5. Security and Configuration
- **GitHub Secrets**: All sensitive information must be stored as GitHub Secrets, not in the workflow file.
  - `DOCKER_USERNAME`: Your Docker Hub username.
  - `DOCKER_PASSWORD`: Your Docker Hub password or access token.
  - `SSH_HOST`: The IP address or domain name of your production server.
  - `SSH_USERNAME`: The username for SSH login.
  - `SSH_PRIVATE_KEY`: The private SSH key to access the server.

## Branch Protection Rules

### Protected Branches
- develop
- main

### Protection Requirements
1. **Required Status Checks**:
   - All tests must pass
   - Branch must be up to date

2. **Pull Request Requirements**:
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Include administrators in these restrictions

## Test Requirements

### Test Coverage
- All tests in `/tests` directory must pass
- No failing tests allowed

## Workflow Process

1. **Pull Request Creation**:
   - Create PR to develop/main
   - GitHub Actions automatically triggers

2. **Automated Checks**:
   - Runs all tests in `/tests`
   - Generates test status report

3. **Review Process**:
   - PR must be reviewed
   - All tests must pass
   - Branch must be up to date

4. **Merge Approval**:
   - Only allowed after all tests pass
   - Requires reviewer approval
   - Maintains branch protection 
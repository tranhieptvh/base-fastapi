# Batch Processing System Architecture

## Overview
The batch processing system is designed to handle background tasks, scheduled jobs, and bulk operations in the application. This document outlines the architecture and implementation details for the batch processing system.

## Current Implementation

### 1. Core Components
- **Celery**: Task queue system for handling asynchronous tasks
- **Redis**: Message broker and result backend
- **Docker**: Containerized deployment of workers and scheduler

### 2. Project Structure
```
app/
├── core/
│   ├── celery_app.py      # Celery configuration
│   └── config.py          # Environment settings
├── tasks/
│   ├── email_tasks.py     # Email-related tasks
│   └── promotion_tasks.py # Promotion-related tasks
└── templates/
    └── email/            # Email templates
```

## Setup Instructions

### 1. Dependencies
Add the following to your `pyproject.toml`:
```toml
[tool.poetry.dependencies]
celery = "^5.3.6"
redis = "^5.0.1"
```

### 2. Environment Variables
Add these variables to your `.env` file:
```env
# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_WORKER_CONCURRENCY=4
CELERY_MAX_TASKS_PER_CHILD=1000
CELERY_MAX_MEMORY_PER_CHILD=200000

# Email Configuration (required for email tasks)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Your Name
```

### 3. Docker Setup
The project uses Docker Compose to manage services. Here's the relevant configuration:

```yaml
# docker-compose.yml
services:
  worker:
    build: .
    container_name: fastapi_worker
    command: celery -A app.core.celery_app worker -Q email_queue -l info
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
      app:
        condition: service_started
    networks:
      - app-network

  beat:
    build: .
    container_name: fastapi_beat
    command: celery -A app.core.celery_app beat -l info
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
      app:
        condition: service_started
    networks:
      - app-network

  redis:
    image: redis:latest
    container_name: fastapi_redis
    ports:
      - "6379:6379"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

### 4. Starting Services
Use the provided Makefile commands:
```bash
# Start the main application
make up

# Start worker and beat services
make up-worker

# Stop all services
make down

# Restart services
make restart
```

## Creating New Batch Tasks

### 1. Basic Task Structure
Create a new file in `app/tasks/` directory:

```python
from app.core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def your_task_name(param1, param2):
    """
    Task description here.
    """
    try:
        # Your task implementation
        logger.info(f"Processing task with params: {param1}, {param2}")
        # ... task logic ...
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise
```

### 2. Scheduled Tasks
To create a scheduled task, add it to the beat schedule in `app/core/celery_app.py`:

```python
celery_app.conf.beat_schedule = {
    "your-task-name": {
        "task": "app.tasks.your_module.your_task_name",
        "schedule": 60*60*24,  # Run every 24 hours
        "options": {
            "queue": "your_queue",
            "retry": True,
            "retry_policy": {
                "max_retries": 3,
                "interval_start": 0,
                "interval_step": 0.2,
                "interval_max": 0.5,
            },
        },
    },
}
```

### 3. Task Queues
The system currently uses the following queues:
- `default`: Default queue for general tasks
- `email_queue`: Dedicated queue for email-related tasks

To route tasks to specific queues, add them to the task routes in `app/core/celery_app.py`:

```python
celery_app.conf.task_routes = {
    "app.tasks.your_module.*": {
        "queue": "your_queue",
        "routing_key": "your_queue",
    },
}
```

## Best Practices

1. **Error Handling**
   - Always use try-except blocks in tasks
   - Log errors with appropriate context
   - Implement retry mechanisms for transient failures

2. **Task Design**
   - Keep tasks idempotent
   - Break large tasks into smaller subtasks
   - Use appropriate task timeouts
   - Clean up resources properly

3. **Monitoring**
   - Use logging for task execution tracking
   - Monitor queue lengths and worker health
   - Track task success/failure rates

4. **Resource Management**
   - Set appropriate concurrency levels
   - Monitor memory usage
   - Implement task rate limiting when needed

## Example Tasks

### 1. Email Task
```python
@celery_app.task
def send_email_task(email_to, subject, template_name, template_data):
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Start sending email to {email_to}")
        asyncio.run(send_email(
            email_to=email_to,
            subject=subject,
            template_name=template_name,
            template_data=template_data
        ))
        logger.info(f"Email sent to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}", exc_info=True)
```

### 2. Scheduled Promotion Task
```python
@celery_app.task
def send_promotion_emails():
    """
    Send promotion emails to all active users.
    """
    try:
        db = SessionLocal()
        users = get_default_users(db)
        logger.info(f"Found {len(users)} users to send promotion emails")
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                template_data = {
                    "username": user.username,
                    "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "promotion_title": "Special Offer Today!",
                    "promotion_content": "Get 50% off on all products!",
                    "promotion_link": f"{settings.FRONTEND_URL}/promotions",
                    "frontend_url": settings.FRONTEND_URL
                }
                
                result = send_email_task.delay(
                    email_to=user.email,
                    subject="Special Promotion Just For You!",
                    template_name="promotion.html",
                    template_data=template_data
                )
                
                logger.info(f"Sent promotion email to {user.email}, task_id: {result.id}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send promotion email to {user.email}: {str(e)}")
                error_count += 1
                continue
            
        return {
            "success_count": success_count,
            "error_count": error_count,
            "total_users": len(users)
        }
            
    except Exception as e:
        logger.error(f"Error in send_promotion_emails: {str(e)}")
        raise
    finally:
        db.close() 
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.promotion_tasks", "app.tasks.email_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Queue configuration
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "email_queue": {
            "exchange": "email",
            "routing_key": "email",
        },
    },
    
    # Task routing
    task_routes={
        "app.tasks.promotion_tasks.*": {
            "queue": "email_queue",
            "routing_key": "email",
        },
        "app.tasks.email_tasks.*": {
            "queue": "email_queue",
            "routing_key": "email",
        },
    },
    
    # Task settings
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_max_memory_per_child=200000,
    
    # Beat schedule for promotion emails (every 5 minutes for testing)
    beat_schedule={
        "send-promotion-emails": {
            "task": "app.tasks.promotion_tasks.send_promotion_emails",
            "schedule": 60*60*24,  # 1 day in seconds
            "options": {
                "queue": "email_queue",
                "retry": True,
                "retry_policy": {
                    "max_retries": 3,
                    "interval_start": 0,
                    "interval_step": 0.2,
                    "interval_max": 0.5,
                },
            },
        },
    },
) 
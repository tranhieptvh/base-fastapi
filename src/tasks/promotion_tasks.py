from typing import List
from src.core.enums import RoleEnum
from sqlalchemy.orm import Session
from src.core.celery_app import celery_app
from src.services.email import send_email
from src.dependencies.db import SessionLocal
from src.services.user import get_default_users
from datetime import datetime
from src.core.config import settings
import logging
from src.tasks.email_tasks import send_email_task

logger = logging.getLogger(__name__)

@celery_app.task
def send_promotion_emails():
    """
    Send promotion emails to all active users.
    This task will be scheduled to run every 5 minutes for testing.
    """
    try:
        db = SessionLocal()
        # Get all active users
        users = get_default_users(db)  # Adjust limit as needed
        logger.info(f"Found {len(users)} users to send promotion emails")
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                # Prepare promotion email content
                template_data = {
                    "username": user.username,
                    "current_time": current_time,
                    "promotion_title": "Special Offer Today!",
                    "promotion_content": "Get 50% off on all products!",
                    "promotion_link": f"{settings.FRONTEND_URL}/promotions",
                    "frontend_url": settings.FRONTEND_URL
                }
                
                # Send promotion email
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
            
        logger.info(f"Promotion email sending completed. Success: {success_count}, Errors: {error_count}")
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
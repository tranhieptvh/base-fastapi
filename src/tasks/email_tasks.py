from src.core.celery_app import celery_app
from src.services.email import send_email, send_reset_password_email
import asyncio
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def send_email_task(email_to, subject, template_name, template_data):
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

@celery_app.task
def send_reset_password_email_task(email_to: str, username: str, token: str):
    try:
        logger.info(f"Start sending password reset email to {email_to}")
        asyncio.run(send_reset_password_email(
            email_to=email_to,
            username=username,
            token=token
        ))
        logger.info(f"Password reset email sent to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email_to}: {e}", exc_info=True)
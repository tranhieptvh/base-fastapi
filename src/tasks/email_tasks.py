from src.core.celery_app import celery_app
from src.services.email import send_email
import asyncio
import logging

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
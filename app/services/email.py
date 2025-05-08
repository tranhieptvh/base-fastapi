from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Dict, Any
from app.core.config import settings
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import os

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates' / 'email'
)

# Setup Jinja2 environment
template_dir = Path(__file__).parent.parent / 'templates' / 'email'
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=True
)

def render_template(template_name: str, data: Dict[str, Any]) -> str:
    """
    Render email template with given data.
    
    Args:
        template_name: Name of the template file
        data: Dictionary containing template variables
    
    Returns:
        Rendered HTML string
    """
    template = env.get_template(template_name)
    return template.render(**data)

async def send_email(
    email_to: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any]
) -> None:
    """
    Send email using template.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        template_name: Name of the template file
        template_data: Dictionary containing template variables
    """
    # Render template
    html_content = render_template(template_name, template_data)
    
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_welcome_email(email_to: str, username: str) -> None:
    """
    Send welcome email to newly registered user.
    
    Args:
        email_to: User's email address
        username: User's username
    """
    template_data = {
        "username": username,
        "login_url": f"{settings.FRONTEND_URL}/login"
    }
    
    await send_email(
        email_to=email_to,
        subject="Welcome to Our Platform!",
        template_name="welcome.html",
        template_data=template_data
    ) 
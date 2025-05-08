# Email System Architecture

## Overview
The email system is designed to handle automated email communications within the application, particularly for user registration and other system notifications. This document outlines the architecture and implementation details.

## Components

### 1. Email Service (`app/services/email.py`)
- **Purpose**: Central service for handling all email-related operations
- **Key Features**:
  - Email configuration management
  - Template-based email sending using Jinja2
  - HTML email support
  - Async email sending to prevent blocking
- **Implemented Features**:
  - Welcome email sending on user registration
  - Async email delivery
  - Jinja2 template rendering
  - Error handling and logging

### 2. Configuration (`app/core/config.py`)
- **Email Settings**:
  ```python
  MAIL_USERNAME: str
  MAIL_PASSWORD: str
  MAIL_FROM: str
  MAIL_PORT: int
  MAIL_SERVER: str
  MAIL_FROM_NAME: str
  FRONTEND_URL: str  # For generating login URLs in emails
  ```
- **Security**: Sensitive credentials stored in environment variables

### 3. Email Templates
- **Location**: `app/templates/email/`
- **Format**: HTML templates using Jinja2 templating engine
- **Types**:
  - Welcome email (Implemented)
  - Password reset (Planned)
  - Account verification (Planned)
  - System notifications (Planned)

## Implementation Status

### ✅ Completed
1. Basic email service setup
2. Welcome email implementation with Jinja2 templates
3. Async email sending
4. Environment configuration
5. Email templates for welcome emails
6. Template rendering system

### 🚧 In Progress
1. Password reset email functionality
2. Email queue system
3. Additional email templates

### 📋 Planned
1. Account verification emails
2. System notification emails
3. Email analytics
4. Template versioning

## Implementation Steps

### 1. Setup Dependencies
Add to `pyproject.toml`:
```toml
[tool.poetry.dependencies]
fastapi-mail = "^1.4.1"
jinja2 = "^3.1.2"
```

Then run:
```bash
poetry add fastapi-mail jinja2
```

### 2. Environment Configuration
Add to `.env`:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=Your App Name
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
FRONTEND_URL=http://your-frontend-url
```

### 3. Email Service Implementation
```python
# app/services/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Dict, Any
from app.core.config import settings
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

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
    """Render email template with given data."""
    template = env.get_template(template_name)
    return template.render(**data)

async def send_email(
    email_to: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any]
) -> None:
    """Send email using template."""
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
    """Send welcome email to newly registered user."""
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
```

### 4. Email Template Example
```html
<!-- app/templates/email/welcome.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Our Platform</title>
</head>
<body>
    <h1>Welcome {{ username }}!</h1>
    <p>Thank you for joining our platform.</p>
    <p>You can now <a href="{{ login_url }}">login to your account</a>.</p>
</body>
</html>
```

## Security Considerations

1. **Email Credentials**
   - ✅ Never hardcode email credentials
   - ✅ Use environment variables
   - ✅ For Gmail, use App Passwords instead of regular passwords

2. **Rate Limiting**
   - 🚧 Implement rate limiting for email sending
   - 🚧 Prevent email spam

3. **Error Handling**
   - ✅ Graceful handling of email sending failures
   - ✅ Logging of email-related errors
   - 🚧 Retry mechanism for failed emails

## Best Practices

1. **Template Management**
   - ✅ Use HTML templates with Jinja2
   - ✅ Keep templates separate from code
   - ✅ Template autoescaping enabled
   - 🚧 Support for multiple languages

2. **Async Operations**
   - ✅ Use async/await for email sending
   - ✅ Prevent blocking of main application

3. **Monitoring**
   - ✅ Log all email operations
   - 🚧 Track email delivery status
   - 🚧 Monitor email queue

## Future Enhancements

1. **Email Queue System**
   - Implement background task queue
   - Handle email sending asynchronously
   - Retry failed emails

2. **Template Engine**
   - ✅ Integration with Jinja2 for dynamic templates
   - ✅ Support for email variables
   - 🚧 Template versioning

3. **Analytics**
   - Track email open rates
   - Monitor delivery success
   - User engagement metrics

## Testing Strategy

1. **Unit Tests**
   - ✅ Test email service functions
   - ✅ Validate email templates
   - ✅ Check configuration loading
   - ✅ Test template rendering

2. **Integration Tests**
   - ✅ Test email sending flow
   - ✅ Verify template rendering
   - ✅ Check error handling

3. **Mock Testing**
   - Use email testing services
   - Simulate email sending
   - Test error scenarios 
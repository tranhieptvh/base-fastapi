import asyncio
from app.services.email import send_email

asyncio.run(send_email(
    email_to="hieptv.develop@gmail.com",
    subject="Test from worker",
    template_name="welcome.html",
    template_data={"username": "Test"}
))
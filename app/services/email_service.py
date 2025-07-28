from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config.settings import settings
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_USERNAME,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_SERVER,
    MAIL_TLS=True,
    MAIL_SSL=False
)

async def send_payment_confirmation(user_email: EmailStr, amount: float, transaction_id: str):
    message = MessageSchema(
        subject="Payment Confirmation - Sibol",
        recipients=[user_email],
        body=f"""
        <h2>Payment Confirmation</h2>
        <p>Thank you for your payment of PHP {amount:.2f}.</p>
        <p>Transaction ID: {transaction_id}</p>
        <p>Contact us at support@sibol.com for any inquiries.</p>
        """,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
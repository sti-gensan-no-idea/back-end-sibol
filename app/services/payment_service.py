import uuid
import aiohttp
from sqlalchemy.orm import Session
from app.models.payment import Payment, Balance
from app.config.settings import settings
from fastapi import BackgroundTasks
from app.services.email_service import send_payment_confirmation

async def create_payment_intent(amount: float, description: str, email: str):
    idempotency_key = str(uuid.uuid4())
    payload = {
        "reference_id": f"payment-{uuid.uuid4()}",
        "channel_code": "QRPH",
        "first_name": "User",
        "last_name": "Sibol",
        "email": email,
        "failure_return_url": "https://example.com/payment/failure",
        "success_return_url": "https://example.com/payment/success",
        "cancel_return_url": "https://example.com/payment/cancel",
        "description": description,
        "metadata": {"amount": amount}
    }
    headers = {
        "Authorization": f"Bearer {settings.PAYFUSION_SECRET_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Idempotency-Key": idempotency_key
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://payfusion.solutions/api/v1/live/payment-tokens",
            json=payload,
            headers=headers
        ) as response:
            if response.status != 200:
                raise Exception(f"PayFusion error: {await response.text()}")
            data = await response.json()
    return {
        "id": data.get("id"),
        "attributes": {
            "currency": "PHP",
            "qr_code_url": data.get("qr_code_url", ""),
            "status": "PENDING"
        }
    }

async def get_payment_intent(payment_intent_id: str, db: Session):
    payment = db.query(Payment).filter(Payment.payment_intent_id == payment_intent_id).first()
    if not payment:
        return None
    return {
        "id": payment.payment_intent_id,
        "attributes": {
            "currency": payment.currency,
            "qr_code_url": payment.qr_code_url,
            "status": payment.status.value
        }
    }
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks
from app.models.payment import Payment, PaymentStatus, Balance
from app.models.user import User
from app.services.payment_service import create_payment_intent, get_payment_intent
from app.services.email_service import send_payment_confirmation

class PaymentController:
    @staticmethod
    async def create_payment(db: Session, user_id: int, amount: float, description: str, 
                            background_tasks: BackgroundTasks):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        payment_intent = await create_payment_intent(amount, description, user.email)
        payment = Payment(
            user_id=user_id,
            transaction_id=payment_intent["id"],
            amount=amount,
            currency=payment_intent["attributes"]["currency"],
            status=PaymentStatus.PENDING,
            qr_code_url=payment_intent["attributes"].get("qr_code_url"),
            description=description
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Update balance
        balance = db.query(Balance).filter(Balance.user_id == user_id).first()
        if not balance:
            balance = Balance(user_id=user_id, amount=0.0)
            db.add(balance)
        balance.amount += amount
        db.commit()

        # Send email in background
        background_tasks.add_task(
            send_payment_confirmation,
            user_email=user.email,
            amount=amount,
            transaction_id=payment.transaction_id
        )
        return payment

    @staticmethod
    def get_user_balance(db: Session, user_id: int):
        balance = db.query(Balance).filter(Balance.user_id == user_id).first()
        if not balance:
            return Balance(user_id=user_id, amount=0.0)
        return balance

    @staticmethod
    def get_user_payments(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(Payment).filter(Payment.user_id == user_id).offset(skip).limit(limit).all()
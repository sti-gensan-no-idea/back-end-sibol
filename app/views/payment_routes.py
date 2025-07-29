from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.payment_controller import PaymentController
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.payment import PaymentCreate, PaymentResponse, BalanceResponse
from fastapi import BackgroundTasks

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

@router.post("/", response_model=PaymentResponse, summary="Create a payment request")
async def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), 
                        current_user: User = Depends(get_current_user), 
                        background_tasks: BackgroundTasks = None):
    return await PaymentController.create_payment(db, current_user.id, payment.amount, 
                                                 payment.description, background_tasks)

@router.get("/balance", response_model=BalanceResponse, summary="Get user balance")
async def get_balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    balance = PaymentController.get_user_balance(db, current_user.id)
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return balance

@router.get("/", response_model=list[PaymentResponse], summary="Get user payments")
async def get_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), 
                      skip: int = 0, limit: int = 100):
    return PaymentController.get_user_payments(db, current_user.id, skip, limit)
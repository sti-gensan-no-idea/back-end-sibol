from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"

class PaymentCreate(BaseModel):
    amount: float
    description: str

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    transaction_id: str
    amount: float
    currency: str
    status: PaymentStatus
    qr_code_url: str | None
    description: str | None
    created_at: datetime

    class Config:
        orm_mode = True

class BalanceResponse(BaseModel):
    user_id: int
    amount: float

    class Config:
        orm_mode = True
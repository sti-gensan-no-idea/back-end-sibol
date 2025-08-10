"""
Enhanced Payment and Transaction models with comprehensive tracking
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey, Text, JSON
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    EXPIRED = "EXPIRED"


class PaymentMethod(enum.Enum):
    QR_CODE = "QR_CODE"
    BANK_TRANSFER = "BANK_TRANSFER"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    E_WALLET = "E_WALLET"
    CASH = "CASH"
    CRYPTOCURRENCY = "CRYPTOCURRENCY"


class TransactionType(enum.Enum):
    PURCHASE = "PURCHASE"
    COMMISSION = "COMMISSION"
    REFUND = "REFUND"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    FEE = "FEE"
    BONUS = "BONUS"


class TransactionStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REVERSED = "REVERSED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Payment Details
    amount = Column(Decimal(12, 2), nullable=False)
    currency = Column(String(3), default="PHP")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    method = Column(Enum(PaymentMethod), default=PaymentMethod.QR_CODE)
    
    # External References
    transaction_id = Column(String(255), unique=True, index=True)
    reference_number = Column(String(255))
    external_transaction_id = Column(String(255))  # From payment provider
    
    # Payment Provider Details
    provider = Column(String(100), default="PayFusion")  # PayFusion, GCash, PayMaya, etc.
    provider_response = Column(JSON)  # Store provider response
    
    # QR Code Information
    qr_code_url = Column(String(500))
    qr_code_data = Column(Text)
    qr_expires_at = Column(DateTime(timezone=True))
    
    # Description and Metadata
    description = Column(Text)
    metadata = Column(JSON)  # Additional custom data
    notes = Column(Text)
    
    # Fee Information
    processing_fee = Column(Decimal(10, 2), default=0.00)
    platform_fee = Column(Decimal(10, 2), default=0.00)
    net_amount = Column(Decimal(12, 2))  # Amount after fees
    
    # Refund Information
    refund_amount = Column(Decimal(12, 2), default=0.00)
    refund_reason = Column(Text)
    refunded_at = Column(DateTime(timezone=True))
    
    # Payment Flow
    payment_url = Column(String(500))  # Redirect URL for payment
    webhook_received = Column(Boolean, default=False)
    confirmation_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    @property
    def is_successful(self) -> bool:
        """Check if payment is successful"""
        return self.status == PaymentStatus.SUCCESSFUL
    
    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == PaymentStatus.PENDING
    
    @property
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded"""
        return (self.status == PaymentStatus.SUCCESSFUL and 
                self.refund_amount < self.amount)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status.value}', user_id={self.user_id})>"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), index=True)
    
    # Transaction Details
    amount = Column(Decimal(12, 2), nullable=False)
    currency = Column(String(3), default="PHP")
    type = Column(Enum(TransactionType), nullable=False, index=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    
    # References
    reference_number = Column(String(255), unique=True, index=True)
    external_reference = Column(String(255))
    batch_id = Column(String(255))  # For batch transactions
    
    # Description and Details
    description = Column(Text)
    details = Column(JSON)  # Additional transaction details
    notes = Column(Text)
    
    # Balance Impact
    balance_before = Column(Decimal(12, 2))
    balance_after = Column(Decimal(12, 2))
    
    # Commission Details (for agent transactions)
    commission_rate = Column(Decimal(5, 2))  # Percentage
    base_amount = Column(Decimal(12, 2))  # Amount commission is calculated from
    
    # Approval and Processing
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    processed_by = Column(Integer, ForeignKey("users.id"))
    
    # Reversal Information
    reversed_transaction_id = Column(Integer, ForeignKey("transactions.id"))
    reversal_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    property = relationship("Property", back_populates="transactions")
    payment = relationship("Payment")
    approver = relationship("User", foreign_keys=[approved_by])
    processor = relationship("User", foreign_keys=[processed_by])
    reversed_transaction = relationship("Transaction", remote_side=[id])
    
    @property
    def is_completed(self) -> bool:
        """Check if transaction is completed"""
        return self.status == TransactionStatus.COMPLETED
    
    @property
    def is_commission(self) -> bool:
        """Check if transaction is a commission"""
        return self.type == TransactionType.COMMISSION
    
    @property
    def can_be_reversed(self) -> bool:
        """Check if transaction can be reversed"""
        return (self.status == TransactionStatus.COMPLETED and 
                self.reversed_transaction_id is None)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.type.value}', amount={self.amount}, status='{self.status.value}')>"


class PaymentWebhook(Base):
    __tablename__ = "payment_webhooks"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), index=True)
    
    # Webhook Details
    provider = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False)
    webhook_id = Column(String(255))  # Provider's webhook ID
    
    # Request Details
    headers = Column(JSON)
    payload = Column(JSON)
    signature = Column(String(500))
    
    # Processing Status
    processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    payment = relationship("Payment")
    
    def __repr__(self):
        return f"<PaymentWebhook(id={self.id}, provider='{self.provider}', event_type='{self.event_type}')>"

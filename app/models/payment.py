"""
Comprehensive Payment and Transaction models for Real Estate Management System
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey, Text, JSON
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class PaymentMethod(enum.Enum):
    QR_CODE = "qr_code"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    E_WALLET = "e_wallet"
    CASH = "cash"
    CHECK = "check"
    CRYPTOCURRENCY = "cryptocurrency"


class PaymentType(enum.Enum):
    RESERVATION_FEE = "reservation_fee"
    DOWNPAYMENT = "downpayment"
    EQUITY = "equity"
    MONTHLY_AMORTIZATION = "monthly_amortization"
    MAINTENANCE_FEE = "maintenance_fee"
    COMMISSION = "commission"
    REFUND = "refund"


class TransactionType(enum.Enum):
    PROPERTY_PURCHASE = "property_purchase"
    COMMISSION_PAYOUT = "commission_payout"
    REFUND = "refund"
    MAINTENANCE_PAYMENT = "maintenance_payment"
    PENALTY = "penalty"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    FEE = "fee"
    BONUS = "bonus"


class TransactionStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True, index=True)
    
    # Payment Details
    amount = Column(Decimal(15, 2), nullable=False)
    currency = Column(String(3), default="PHP")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    method = Column(Enum(PaymentMethod), default=PaymentMethod.QR_CODE)
    payment_type = Column(Enum(PaymentType), nullable=False, index=True)
    
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
    
    # Real Estate Specific
    installment_number = Column(Integer)  # For monthly payments
    total_installments = Column(Integer)  # Total installments for this payment plan
    is_overdue = Column(Boolean, default=False)
    days_overdue = Column(Integer, default=0)
    penalty_amount = Column(Decimal(15, 2), default=0.00)
    
    # Construction Trigger
    triggers_construction = Column(Boolean, default=False)
    construction_percentage_reached = Column(Decimal(5, 2))
    
    # Description and Metadata
    description = Column(Text)
    metadata = Column(JSON)  # Additional custom data
    notes = Column(Text)
    
    # Fee Information
    processing_fee = Column(Decimal(10, 2), default=0.00)
    platform_fee = Column(Decimal(10, 2), default=0.00)
    net_amount = Column(Decimal(15, 2))  # Amount after fees
    
    # Refund Information
    refund_amount = Column(Decimal(15, 2), default=0.00)
    refund_reason = Column(Text)
    refunded_at = Column(DateTime(timezone=True))
    
    # Payment Flow
    payment_url = Column(String(500))  # Redirect URL for payment
    webhook_received = Column(Boolean, default=False)
    confirmation_sent = Column(Boolean, default=False)
    
    # Due dates
    due_date = Column(DateTime(timezone=True))
    paid_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="payments")
    property = relationship("Property")
    contract = relationship("Contract", back_populates="payments")
    
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
    
    def calculate_penalty(self) -> Decimal:
        """Calculate penalty for overdue payment"""
        if not self.is_overdue or self.days_overdue <= 0:
            return Decimal('0.00')
        
        # Example: 1% per month overdue, minimum 30 days
        penalty_rate = Decimal('0.01')  # 1%
        months_overdue = max(1, self.days_overdue // 30)
        return self.amount * penalty_rate * months_overdue
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status.value}', user_id={self.user_id})>"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True, index=True)
    
    # Transaction Details
    amount = Column(Decimal(15, 2), nullable=False)
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
    balance_before = Column(Decimal(15, 2))
    balance_after = Column(Decimal(15, 2))
    
    # Commission Details (for agent/broker transactions)
    commission_rate = Column(Decimal(5, 2))  # Percentage
    base_amount = Column(Decimal(15, 2))  # Amount commission is calculated from
    agent_id = Column(Integer, ForeignKey("users.id"))  # Agent earning commission
    broker_id = Column(Integer, ForeignKey("users.id"))  # Broker earning commission
    
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
    user = relationship("User", foreign_keys=[user_id], back_populates="transactions")
    property = relationship("Property")
    payment = relationship("Payment")
    agent = relationship("User", foreign_keys=[agent_id])
    broker = relationship("User", foreign_keys=[broker_id])
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
        return self.type == TransactionType.COMMISSION_PAYOUT
    
    @property
    def can_be_reversed(self) -> bool:
        """Check if transaction can be reversed"""
        return (self.status == TransactionStatus.COMPLETED and 
                self.reversed_transaction_id is None)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.type.value}', amount={self.amount}, status='{self.status.value}')>"


class PaymentPlan(Base):
    """Payment plans for properties"""
    __tablename__ = "payment_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    
    # Plan details
    total_amount = Column(Decimal(15, 2), nullable=False)
    downpayment_amount = Column(Decimal(15, 2), nullable=False)
    equity_amount = Column(Decimal(15, 2), nullable=False)
    loanable_amount = Column(Decimal(15, 2), nullable=False)
    
    # Payment schedule
    monthly_payment = Column(Decimal(15, 2))
    total_months = Column(Integer)
    payments_made = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Amounts paid
    total_paid = Column(Decimal(15, 2), default=0.00)
    remaining_balance = Column(Decimal(15, 2))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    property = relationship("Property")
    client = relationship("User", foreign_keys=[client_id])
    contract = relationship("Contract")
    scheduled_payments = relationship("ScheduledPayment", back_populates="payment_plan")
    
    @property
    def payment_progress_percentage(self) -> float:
        """Calculate payment progress percentage"""
        if self.total_amount <= 0:
            return 0.0
        return float(self.total_paid / self.total_amount * 100)
    
    @property
    def can_trigger_construction(self) -> bool:
        """Check if payment reached construction trigger threshold"""
        if not self.property:
            return False
        trigger_amount = self.total_amount * (self.property.construction_trigger_percentage / 100)
        return self.total_paid >= trigger_amount


class ScheduledPayment(Base):
    """Scheduled payments for payment plans"""
    __tablename__ = "scheduled_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_plan_id = Column(Integer, ForeignKey("payment_plans.id"), nullable=False)
    
    # Schedule details
    installment_number = Column(Integer, nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    
    # Status
    is_paid = Column(Boolean, default=False)
    paid_amount = Column(Decimal(15, 2), default=0.00)
    paid_date = Column(DateTime(timezone=True))
    payment_id = Column(Integer, ForeignKey("payments.id"))
    
    # Overdue tracking
    is_overdue = Column(Boolean, default=False)
    days_overdue = Column(Integer, default=0)
    penalty_amount = Column(Decimal(15, 2), default=0.00)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    payment_plan = relationship("PaymentPlan", back_populates="scheduled_payments")
    payment = relationship("Payment")


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

"""
Contract model for Real Estate Management System
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey, Text, JSON
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class ContractStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TERMINATED = "terminated"
    EXPIRED = "expired"


class ContractType(enum.Enum):
    RESERVATION_AGREEMENT = "reservation_agreement"
    PURCHASE_AGREEMENT = "purchase_agreement"
    LEASE_AGREEMENT = "lease_agreement"
    BROKER_AGREEMENT = "broker_agreement"
    AGENT_AGREEMENT = "agent_agreement"
    MAINTENANCE_AGREEMENT = "maintenance_agreement"


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Parties involved
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Buyer/Tenant
    developer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Property owner/Developer
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Handling agent
    broker_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Broker
    
    # Contract details
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    contract_type = Column(Enum(ContractType), nullable=False)
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    
    # Financial terms
    total_amount = Column(Decimal(15, 2), nullable=False)
    reservation_fee = Column(Decimal(15, 2), default=0.00)
    downpayment_amount = Column(Decimal(15, 2), nullable=False)
    equity_amount = Column(Decimal(15, 2))
    loanable_amount = Column(Decimal(15, 2))
    monthly_payment = Column(Decimal(15, 2))
    
    # Payment schedule
    downpayment_months = Column(Integer, default=12)  # Months to pay downpayment
    total_contract_months = Column(Integer)
    
    # Commission structure
    agent_commission_rate = Column(Decimal(5, 2))  # Percentage
    broker_commission_rate = Column(Decimal(5, 2))  # Percentage
    agent_commission_amount = Column(Decimal(15, 2))
    broker_commission_amount = Column(Decimal(15, 2))
    
    # Construction and delivery
    construction_start_condition = Column(Text)  # e.g., "50% downpayment received"
    estimated_completion_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    turnover_date = Column(DateTime(timezone=True))
    
    # Legal terms
    terms_and_conditions = Column(Text)
    special_provisions = Column(Text)
    cancellation_policy = Column(Text)
    
    # Document management
    contract_template = Column(String(500))  # Template used
    signed_contract_url = Column(String(500))  # Final signed contract
    attachments = Column(JSON)  # Array of attachment URLs
    
    # Digital signatures
    client_signed = Column(Boolean, default=False)
    client_signature = Column(Text)  # Digital signature data
    client_signed_at = Column(DateTime(timezone=True))
    
    developer_signed = Column(Boolean, default=False)
    developer_signature = Column(Text)
    developer_signed_at = Column(DateTime(timezone=True))
    
    agent_signed = Column(Boolean, default=False)
    agent_signature = Column(Text)
    agent_signed_at = Column(DateTime(timezone=True))
    
    # Witness signatures
    witness1_name = Column(String(200))
    witness1_signature = Column(Text)
    witness1_signed_at = Column(DateTime(timezone=True))
    
    witness2_name = Column(String(200))
    witness2_signature = Column(Text)
    witness2_signed_at = Column(DateTime(timezone=True))
    
    # Contract lifecycle
    effective_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))
    renewal_date = Column(DateTime(timezone=True))
    
    # Status tracking
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    cancelled_by = Column(Integer, ForeignKey("users.id"))
    cancellation_reason = Column(Text)
    cancelled_at = Column(DateTime(timezone=True))
    
    # Metadata
    metadata = Column(JSON)  # Additional contract data
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="tenant_contracts")
    developer = relationship("User", foreign_keys=[developer_id])
    agent = relationship("User", foreign_keys=[agent_id])
    broker = relationship("User", foreign_keys=[broker_id])
    property = relationship("Property", back_populates="contracts")
    approver = relationship("User", foreign_keys=[approved_by])
    canceller = relationship("User", foreign_keys=[cancelled_by])
    payments = relationship("Payment", back_populates="contract")
    
    @property
    def is_fully_signed(self) -> bool:
        """Check if contract is fully signed by all required parties"""
        required_signatures = [self.client_signed, self.developer_signed]
        if self.agent_id:
            required_signatures.append(self.agent_signed)
        return all(required_signatures)
    
    @property
    def is_active(self) -> bool:
        """Check if contract is currently active"""
        return self.status == ContractStatus.ACTIVE
    
    @property
    def total_commission(self) -> Decimal:
        """Calculate total commission amount"""
        total = Decimal('0.00')
        if self.agent_commission_amount:
            total += self.agent_commission_amount
        if self.broker_commission_amount:
            total += self.broker_commission_amount
        return total
    
    @property
    def payment_progress(self) -> dict:
        """Get payment progress for this contract"""
        # This would calculate based on related payments
        total_paid = sum([p.amount for p in self.payments if p.is_successful])
        progress_percentage = (total_paid / self.total_amount * 100) if self.total_amount > 0 else 0
        
        return {
            "total_amount": float(self.total_amount),
            "total_paid": float(total_paid),
            "remaining": float(self.total_amount - total_paid),
            "progress_percentage": float(progress_percentage)
        }
    
    def can_start_construction(self) -> bool:
        """Check if construction can be started based on payment received"""
        if not self.property:
            return False
        
        total_paid = sum([p.amount for p in self.payments if p.is_successful])
        trigger_amount = self.total_amount * (self.property.construction_trigger_percentage / 100)
        
        return total_paid >= trigger_amount
    
    def __repr__(self):
        return f"<Contract(id={self.id}, contract_number='{self.contract_number}', status='{self.status.value}')>"


class ContractAmendment(Base):
    """Contract amendments and modifications"""
    __tablename__ = "contract_amendments"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    # Amendment details
    amendment_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Changes made
    changes = Column(JSON)  # Structured data of what changed
    old_values = Column(JSON)  # Previous values
    new_values = Column(JSON)  # New values
    
    # Legal text
    amendment_text = Column(Text)
    
    # Approval and signatures
    requires_client_approval = Column(Boolean, default=True)
    requires_developer_approval = Column(Boolean, default=True)
    
    client_approved = Column(Boolean, default=False)
    client_approved_at = Column(DateTime(timezone=True))
    
    developer_approved = Column(Boolean, default=False)
    developer_approved_at = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected
    effective_date = Column(DateTime(timezone=True))
    
    # Created by
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contract = relationship("Contract")
    creator = relationship("User", foreign_keys=[created_by])


class ContractTemplate(Base):
    """Contract templates for different types of agreements"""
    __tablename__ = "contract_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contract_type = Column(Enum(ContractType), nullable=False)
    
    # Template content
    template_content = Column(Text, nullable=False)  # HTML template with placeholders
    required_fields = Column(JSON)  # Fields that must be filled
    optional_fields = Column(JSON)  # Optional fields
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    version = Column(String(20), default="1.0")
    
    # Metadata
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

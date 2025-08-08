from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Decimal, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from datetime import datetime

class ContractStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    CANCELLED = "cancelled"

class ContractType(enum.Enum):
    RESIDENTIAL_LEASE = "residential_lease"
    COMMERCIAL_LEASE = "commercial_lease"
    SHORT_TERM_RENTAL = "short_term_rental"
    PROPERTY_MANAGEMENT = "property_management"
    PURCHASE_AGREEMENT = "purchase_agreement"
    SUBLEASE = "sublease"

class PaymentFrequency(enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    WEEKLY = "weekly"
    ONE_TIME = "one_time"

class Contract(Base):
    __tablename__ = "contracts"

    # Primary identifiers
    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relationships
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Primary tenant
    landlord_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Contract details
    contract_type = Column(Enum(ContractType), nullable=False, default=ContractType.RESIDENTIAL_LEASE)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.DRAFT)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Full contract text
    
    # Financial terms
    monthly_rent = Column(Decimal(10, 2), nullable=False)
    security_deposit = Column(Decimal(10, 2), nullable=False, default=0)
    late_fee = Column(Decimal(10, 2), nullable=True)
    late_fee_grace_period = Column(Integer, default=5)  # days
    payment_frequency = Column(Enum(PaymentFrequency), default=PaymentFrequency.MONTHLY)
    
    # Date fields
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    move_in_date = Column(DateTime, nullable=True)
    move_out_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    signed_at = Column(DateTime, nullable=True)
    
    # Contract terms
    is_renewable = Column(Boolean, default=True)
    auto_renewal = Column(Boolean, default=False)
    renewal_notice_period = Column(Integer, default=30)  # days
    termination_notice_period = Column(Integer, default=30)  # days
    
    # Utilities and services
    utilities_included = Column(Text, nullable=True)  # JSON string
    services_included = Column(Text, nullable=True)  # JSON string
    
    # Rules and restrictions
    pet_policy = Column(Text, nullable=True)
    smoking_allowed = Column(Boolean, default=False)
    subletting_allowed = Column(Boolean, default=False)
    max_occupants = Column(Integer, nullable=True)
    
    # Legal and compliance
    governing_law = Column(String(100), nullable=True)
    jurisdiction = Column(String(100), nullable=True)
    
    # Document management
    original_document_path = Column(String(500), nullable=True)
    signed_document_path = Column(String(500), nullable=True)
    template_id = Column(Integer, nullable=True)  # Reference to contract template
    
    # AI and automation
    ai_generated = Column(Boolean, default=False)
    ai_analysis = Column(Text, nullable=True)  # AI analysis results
    risk_score = Column(Decimal(3, 2), nullable=True)  # 0.00 to 1.00
    
    # Signatures and approval
    tenant_signed = Column(Boolean, default=False)
    landlord_signed = Column(Boolean, default=False)
    tenant_signature_date = Column(DateTime, nullable=True)
    landlord_signature_date = Column(DateTime, nullable=True)
    witness_required = Column(Boolean, default=False)
    notarization_required = Column(Boolean, default=False)
    
    # Relationships
    property = relationship("Property", back_populates="contracts")
    tenant = relationship("User", foreign_keys=[tenant_id], back_populates="tenant_contracts")
    landlord = relationship("User", foreign_keys=[landlord_id], back_populates="landlord_contracts")
    
    # Additional relationships for advanced features
    amendments = relationship("ContractAmendment", back_populates="contract", cascade="all, delete-orphan")
    violations = relationship("ContractViolation", back_populates="contract", cascade="all, delete-orphan")
    renewals = relationship("ContractRenewal", back_populates="original_contract", cascade="all, delete-orphan")
    
    @property
    def is_active(self) -> bool:
        """Check if contract is currently active"""
        return (
            self.status == ContractStatus.ACTIVE and
            self.start_date <= datetime.now() <= self.end_date
        )
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until contract expires"""
        if self.end_date:
            delta = self.end_date - datetime.now()
            return max(0, delta.days)
        return 0
    
    @property
    def is_renewable_now(self) -> bool:
        """Check if contract can be renewed now"""
        if not self.is_renewable:
            return False
        days_left = self.days_until_expiry
        return days_left <= self.renewal_notice_period
    
    @property
    def total_value(self) -> float:
        """Calculate total contract value"""
        if self.start_date and self.end_date and self.monthly_rent:
            months = (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
            return float(self.monthly_rent * months)
        return 0.0


class ContractAmendment(Base):
    __tablename__ = "contract_amendments"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    amendment_number = Column(Integer, nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    changes = Column(Text, nullable=False)  # JSON string of changes
    
    effective_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    tenant_approved = Column(Boolean, default=False)
    landlord_approved = Column(Boolean, default=False)
    tenant_approval_date = Column(DateTime, nullable=True)
    landlord_approval_date = Column(DateTime, nullable=True)
    
    contract = relationship("Contract", back_populates="amendments")
    created_by_user = relationship("User")


class ContractViolation(Base):
    __tablename__ = "contract_violations"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    violation_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    reported_date = Column(DateTime, default=func.now())
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    resolved = Column(Boolean, default=False)
    resolution_date = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    fine_amount = Column(Decimal(10, 2), nullable=True)
    fine_paid = Column(Boolean, default=False)
    
    contract = relationship("Contract", back_populates="violations")
    reporter = relationship("User")


class ContractRenewal(Base):
    __tablename__ = "contract_renewals"
    
    id = Column(Integer, primary_key=True, index=True)
    original_contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    new_contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    
    renewal_type = Column(String(50), nullable=False)  # automatic, manual, negotiated
    requested_date = Column(DateTime, default=func.now())
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    new_terms = Column(Text, nullable=True)  # JSON string of proposed changes
    new_rent = Column(Decimal(10, 2), nullable=True)
    new_end_date = Column(DateTime, nullable=True)
    
    status = Column(String(50), default="pending")  # pending, approved, rejected, completed
    approved_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    original_contract = relationship("Contract", foreign_keys=[original_contract_id], back_populates="renewals")
    new_contract = relationship("Contract", foreign_keys=[new_contract_id])
    requester = relationship("User")


class ContractTemplate(Base):
    __tablename__ = "contract_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contract_type = Column(Enum(ContractType), nullable=False)
    
    content_template = Column(Text, nullable=False)  # Template with placeholders
    default_terms = Column(Text, nullable=True)  # JSON string of default terms
    
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    usage_count = Column(Integer, default=0)
    
    creator = relationship("User")


class ContractSignature(Base):
    __tablename__ = "contract_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    signature_type = Column(String(50), nullable=False)  # electronic, digital, physical
    signature_data = Column(Text, nullable=True)  # Base64 encoded signature image or hash
    
    signed_at = Column(DateTime, default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    verified = Column(Boolean, default=False)
    verification_method = Column(String(100), nullable=True)
    
    contract = relationship("Contract")
    signer = relationship("User")

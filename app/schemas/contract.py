# app/schemas/contract.py
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Enums
class ContractStatus(str, Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    CANCELLED = "cancelled"

class ContractType(str, Enum):
    RESIDENTIAL_LEASE = "residential_lease"
    COMMERCIAL_LEASE = "commercial_lease"
    SHORT_TERM_RENTAL = "short_term_rental"
    PROPERTY_MANAGEMENT = "property_management"
    PURCHASE_AGREEMENT = "purchase_agreement"
    SUBLEASE = "sublease"

class PaymentFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    WEEKLY = "weekly"
    ONE_TIME = "one_time"

class ViolationSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Base schemas
class ContractBase(BaseModel):
    property_id: int
    tenant_id: int
    landlord_id: int
    contract_type: ContractType = ContractType.RESIDENTIAL_LEASE
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    monthly_rent: Decimal = Field(..., gt=0)
    security_deposit: Decimal = Field(default=0, ge=0)
    late_fee: Optional[Decimal] = Field(None, ge=0)
    late_fee_grace_period: int = Field(default=5, ge=0)
    payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY
    start_date: datetime
    end_date: datetime
    move_in_date: Optional[datetime] = None
    move_out_date: Optional[datetime] = None
    is_renewable: bool = True
    auto_renewal: bool = False
    renewal_notice_period: int = Field(default=30, ge=0)
    termination_notice_period: int = Field(default=30, ge=0)
    utilities_included: Optional[str] = None
    services_included: Optional[str] = None
    pet_policy: Optional[str] = None
    smoking_allowed: bool = False
    subletting_allowed: bool = False
    max_occupants: Optional[int] = Field(None, ge=1)
    governing_law: Optional[str] = None
    jurisdiction: Optional[str] = None
    witness_required: bool = False
    notarization_required: bool = False

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @validator('move_in_date')
    def move_in_date_validation(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('move_in_date cannot be before start_date')
        return v

    @validator('move_out_date')
    def move_out_date_validation(cls, v, values):
        if v and 'end_date' in values and v > values['end_date']:
            raise ValueError('move_out_date cannot be after end_date')
        return v

class ContractCreate(ContractBase):
    contract_number: Optional[str] = None  # Will be auto-generated if not provided
    template_id: Optional[int] = None

class ContractUpdate(BaseModel):
    property_id: Optional[int] = None
    tenant_id: Optional[int] = None
    landlord_id: Optional[int] = None
    contract_type: Optional[ContractType] = None
    status: Optional[ContractStatus] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    monthly_rent: Optional[Decimal] = Field(None, gt=0)
    security_deposit: Optional[Decimal] = Field(None, ge=0)
    late_fee: Optional[Decimal] = Field(None, ge=0)
    late_fee_grace_period: Optional[int] = Field(None, ge=0)
    payment_frequency: Optional[PaymentFrequency] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    move_in_date: Optional[datetime] = None
    move_out_date: Optional[datetime] = None
    is_renewable: Optional[bool] = None
    auto_renewal: Optional[bool] = None
    renewal_notice_period: Optional[int] = Field(None, ge=0)
    termination_notice_period: Optional[int] = Field(None, ge=0)
    utilities_included: Optional[str] = None
    services_included: Optional[str] = None
    pet_policy: Optional[str] = None
    smoking_allowed: Optional[bool] = None
    subletting_allowed: Optional[bool] = None
    max_occupants: Optional[int] = Field(None, ge=1)
    governing_law: Optional[str] = None
    jurisdiction: Optional[str] = None
    witness_required: Optional[bool] = None
    notarization_required: Optional[bool] = None

# Response schemas
class ContractResponse(ContractBase):
    id: int
    contract_number: str
    status: ContractStatus
    created_at: datetime
    updated_at: datetime
    signed_at: Optional[datetime] = None
    tenant_signed: bool = False
    landlord_signed: bool = False
    tenant_signature_date: Optional[datetime] = None
    landlord_signature_date: Optional[datetime] = None
    ai_generated: bool = False
    ai_analysis: Optional[str] = None
    risk_score: Optional[Decimal] = None
    original_document_path: Optional[str] = None
    signed_document_path: Optional[str] = None
    
    # Computed properties
    is_active: bool
    days_until_expiry: int
    is_renewable_now: bool
    total_value: float

    class Config:
        from_attributes = True

class ContractSummary(BaseModel):
    id: int
    contract_number: str
    title: str
    status: ContractStatus
    contract_type: ContractType
    property_id: int
    tenant_id: int
    landlord_id: int
    monthly_rent: Decimal
    start_date: datetime
    end_date: datetime
    is_active: bool
    days_until_expiry: int

    class Config:
        from_attributes = True

class ContractListResponse(BaseModel):
    contracts: List[ContractSummary]
    total: int
    page: int
    size: int

# Amendment schemas
class ContractAmendmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    changes: Dict[str, Any]  # JSON object of changes
    effective_date: datetime

class ContractAmendmentCreate(ContractAmendmentBase):
    contract_id: int

class ContractAmendmentResponse(ContractAmendmentBase):
    id: int
    contract_id: int
    amendment_number: int
    created_at: datetime
    created_by: int
    tenant_approved: bool = False
    landlord_approved: bool = False
    tenant_approval_date: Optional[datetime] = None
    landlord_approval_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Violation schemas
class ContractViolationBase(BaseModel):
    violation_type: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    severity: ViolationSeverity
    fine_amount: Optional[Decimal] = Field(None, ge=0)

class ContractViolationCreate(ContractViolationBase):
    contract_id: int

class ContractViolationUpdate(BaseModel):
    violation_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    severity: Optional[ViolationSeverity] = None
    resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None
    fine_amount: Optional[Decimal] = Field(None, ge=0)
    fine_paid: Optional[bool] = None

class ContractViolationResponse(ContractViolationBase):
    id: int
    contract_id: int
    reported_date: datetime
    reported_by: int
    resolved: bool = False
    resolution_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    fine_paid: bool = False

    class Config:
        from_attributes = True

# Renewal schemas
class ContractRenewalBase(BaseModel):
    renewal_type: str = Field(..., min_length=1, max_length=50)
    new_terms: Optional[Dict[str, Any]] = None
    new_rent: Optional[Decimal] = Field(None, gt=0)
    new_end_date: Optional[datetime] = None
    notes: Optional[str] = None

class ContractRenewalCreate(ContractRenewalBase):
    original_contract_id: int

class ContractRenewalUpdate(BaseModel):
    status: Optional[str] = None
    new_terms: Optional[Dict[str, Any]] = None
    new_rent: Optional[Decimal] = Field(None, gt=0)
    new_end_date: Optional[datetime] = None
    notes: Optional[str] = None

class ContractRenewalResponse(ContractRenewalBase):
    id: int
    original_contract_id: int
    new_contract_id: Optional[int] = None
    requested_date: datetime
    requested_by: int
    status: str
    approved_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Template schemas
class ContractTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contract_type: ContractType
    content_template: str = Field(..., min_length=1)
    default_terms: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_default: bool = False

class ContractTemplateCreate(ContractTemplateBase):
    pass

class ContractTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    content_template: Optional[str] = Field(None, min_length=1)
    default_terms: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class ContractTemplateResponse(ContractTemplateBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    usage_count: int = 0

    class Config:
        from_attributes = True

# Signature schemas
class ContractSignatureBase(BaseModel):
    signature_type: str = Field(..., min_length=1, max_length=50)
    signature_data: Optional[str] = None
    verification_method: Optional[str] = Field(None, max_length=100)

class ContractSignatureCreate(ContractSignatureBase):
    contract_id: int

class ContractSignatureResponse(ContractSignatureBase):
    id: int
    contract_id: int
    user_id: int
    signed_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    verified: bool = False

    class Config:
        from_attributes = True

# Analysis and AI schemas
class ContractAnalysisRequest(BaseModel):
    contract_id: int
    analysis_type: str = Field(default="comprehensive", regex="^(basic|comprehensive|risk|legal|financial)$")

class ContractAnalysisResponse(BaseModel):
    contract_id: int
    analysis_type: str
    analysis: Dict[str, Any]
    risk_score: Optional[float] = None
    recommendations: List[str] = []
    warnings: List[str] = []
    analysis_date: datetime

class ContractGenerationRequest(BaseModel):
    property_id: int
    tenant_id: int
    landlord_id: int
    contract_type: ContractType
    template_id: Optional[int] = None
    custom_terms: Optional[Dict[str, Any]] = None
    monthly_rent: Decimal = Field(..., gt=0)
    security_deposit: Decimal = Field(default=0, ge=0)
    start_date: datetime
    end_date: datetime
    additional_clauses: Optional[List[str]] = None

class ContractComparisonRequest(BaseModel):
    contract_id_1: int
    contract_id_2: int
    comparison_fields: Optional[List[str]] = None

class ContractComparisonResponse(BaseModel):
    contract_1_id: int
    contract_2_id: int
    differences: Dict[str, Dict[str, Any]]
    similarities: Dict[str, Any]
    recommendations: List[str] = []

# Search and filter schemas
class ContractSearchRequest(BaseModel):
    q: Optional[str] = None  # General search query
    status: Optional[List[ContractStatus]] = None
    contract_type: Optional[List[ContractType]] = None
    property_id: Optional[int] = None
    tenant_id: Optional[int] = None
    landlord_id: Optional[int] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    end_date_from: Optional[datetime] = None
    end_date_to: Optional[datetime] = None
    min_rent: Optional[Decimal] = None
    max_rent: Optional[Decimal] = None
    expiring_within_days: Optional[int] = None
    renewable_only: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = Field(default="created_at", regex="^(created_at|updated_at|start_date|end_date|monthly_rent|title)$")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$")

# Bulk operations
class BulkContractUpdateRequest(BaseModel):
    contract_ids: List[int]
    updates: ContractUpdate

class BulkOperationResponse(BaseModel):
    successful_ids: List[int]
    failed_ids: List[int]
    errors: Dict[int, str]
    total_processed: int

# Dashboard and statistics
class ContractStatistics(BaseModel):
    total_contracts: int
    active_contracts: int
    expiring_soon: int  # Within 30 days
    draft_contracts: int
    pending_signature: int
    average_monthly_rent: float
    total_monthly_revenue: float
    renewal_rate: float  # Percentage
    violation_count: int
    by_contract_type: Dict[str, int]
    by_status: Dict[str, int]
    monthly_trend: List[Dict[str, Any]]  # 12 months of data

class ContractDashboard(BaseModel):
    statistics: ContractStatistics
    recent_contracts: List[ContractSummary]
    expiring_contracts: List[ContractSummary]
    pending_renewals: List[ContractRenewalResponse]
    recent_violations: List[ContractViolationResponse]

"""
CRM schemas for lead management and site visits
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.crm import LeadStatus, LeadSource, SiteVisitStatus


class LeadBase(BaseModel):
    """Base lead schema"""
    # Client information (for guest leads)
    guest_name: Optional[str] = None
    guest_email: Optional[EmailStr] = None
    guest_phone: Optional[str] = None
    
    # Lead details
    source: LeadSource = LeadSource.WEBSITE
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    
    # Qualification details
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    move_in_timeline: Optional[str] = None
    financing_method: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    tags: Optional[List[str]] = []


class LeadCreate(LeadBase):
    """Schema for creating a new lead"""
    property_id: int
    client_id: Optional[int] = None  # Can be null for guest leads
    
    @validator('guest_name')
    def validate_guest_info(cls, v, values):
        # If no client_id, guest info is required
        if not values.get('client_id') and not v:
            raise ValueError('Guest name is required when client_id is not provided')
        return v


class LeadUpdate(BaseModel):
    """Schema for updating lead information"""
    status: Optional[LeadStatus] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Qualification updates
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    move_in_timeline: Optional[str] = None
    financing_method: Optional[str] = None
    
    # Follow-up scheduling
    next_followup: Optional[datetime] = None


class LeadResponse(LeadBase):
    """Schema for lead response"""
    id: int
    client_id: Optional[int] = None
    agent_id: int
    property_id: int
    status: LeadStatus
    
    # Tracking
    last_contact: Optional[datetime] = None
    next_followup: Optional[datetime] = None
    contact_attempts: int = 0
    days_in_pipeline: int = 0
    touchpoints: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    status_changed_at: datetime
    
    # Computed properties
    client_name: str
    client_email: Optional[str] = None
    
    # Relationships (basic info)
    agent: dict
    property: dict
    client: Optional[dict] = None

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Schema for paginated lead list response"""
    leads: List[LeadResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class LeadActivityCreate(BaseModel):
    """Schema for creating lead activity"""
    lead_id: int
    activity_type: str = Field(..., min_length=1, max_length=100)
    subject: Optional[str] = None
    description: Optional[str] = None
    completed: bool = True
    scheduled_for: Optional[datetime] = None


class LeadActivityResponse(BaseModel):
    """Schema for lead activity response"""
    id: int
    lead_id: int
    user_id: int
    activity_type: str
    subject: Optional[str] = None
    description: Optional[str] = None
    completed: bool
    scheduled_for: Optional[datetime] = None
    created_at: datetime
    
    # Relationships
    user: dict  # Basic user info

    class Config:
        from_attributes = True


class SiteVisitBase(BaseModel):
    """Base site visit schema"""
    # Guest information (if not registered client)
    guest_name: Optional[str] = None
    guest_email: Optional[EmailStr] = None
    guest_phone: Optional[str] = None
    
    # Visit details
    scheduled_date: datetime
    number_of_attendees: int = 1
    special_requirements: Optional[str] = None
    transportation_needed: bool = False


class SiteVisitCreate(SiteVisitBase):
    """Schema for creating site visit"""
    property_id: int
    client_id: Optional[int] = None  # Can be null for guest visits
    lead_id: Optional[int] = None  # Link to existing lead if available
    
    @validator('guest_name')
    def validate_guest_info(cls, v, values):
        # If no client_id, guest info is required
        if not values.get('client_id') and not v:
            raise ValueError('Guest name is required when client_id is not provided')
        return v


class SiteVisitUpdate(BaseModel):
    """Schema for updating site visit"""
    status: Optional[SiteVisitStatus] = None
    scheduled_date: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    agent_notes: Optional[str] = None
    client_feedback: Optional[str] = None
    interest_level: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    next_steps: Optional[str] = None


class SiteVisitResponse(SiteVisitBase):
    """Schema for site visit response"""
    id: int
    client_id: Optional[int] = None
    agent_id: int
    property_id: int
    lead_id: Optional[int] = None
    status: SiteVisitStatus
    
    # Visit tracking
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Follow-up
    agent_notes: Optional[str] = None
    client_feedback: Optional[str] = None
    interest_level: Optional[str] = None
    next_steps: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed properties
    client_name: str
    
    # Relationships
    agent: dict
    property: dict
    client: Optional[dict] = None
    lead: Optional[dict] = None

    class Config:
        from_attributes = True


class SiteVisitListResponse(BaseModel):
    """Schema for paginated site visit list response"""
    site_visits: List[SiteVisitResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class NotificationCreate(BaseModel):
    """Schema for creating notification"""
    user_id: int
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    notification_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    action_url: Optional[str] = None


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: int
    user_id: int
    title: str
    message: str
    notification_type: Optional[str] = None
    read: bool = False
    read_at: Optional[datetime] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    action_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list response"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
    unread_count: int


class PipelineStatusUpdate(BaseModel):
    """Schema for updating lead status in pipeline"""
    lead_id: int
    new_status: LeadStatus
    notes: Optional[str] = None


class CRMAnalyticsResponse(BaseModel):
    """Schema for CRM analytics response"""
    agent_id: int
    
    # Lead metrics
    total_leads: int = 0
    leads_by_status: Dict[str, int] = {}
    conversion_rate: float = 0.0
    average_days_to_close: Optional[float] = None
    
    # Site visit metrics
    site_visits_scheduled: int = 0
    site_visits_completed: int = 0
    site_visit_conversion_rate: float = 0.0
    
    # Performance metrics
    closed_deals: int = 0
    total_revenue: float = 0.0
    average_deal_value: Optional[float] = None
    
    # Time period
    period_start: datetime
    period_end: datetime
    
    class Config:
        from_attributes = True

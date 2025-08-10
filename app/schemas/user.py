"""
User schemas for data validation and serialization
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.user import UserRole, AccountStatus


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: UserRole
    
    # Professional credentials (optional)
    license_number: Optional[str] = None
    cpd_units: Optional[int] = 0
    pic_number: Optional[str] = None
    
    # Company information (optional)
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    team_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None
    
    # Professional credentials
    license_number: Optional[str] = None
    cpd_units: Optional[int] = None
    pic_number: Optional[str] = None
    
    # Company information
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    team_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (excludes sensitive data)"""
    id: int
    uuid: str
    role: UserRole
    status: AccountStatus
    is_active: bool
    
    # Professional credentials
    license_number: Optional[str] = None
    cpd_units: Optional[int] = None
    cpd_expiry: Optional[datetime] = None
    pic_number: Optional[str] = None
    pic_expiry: Optional[datetime] = None
    
    # Company information
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    team_name: Optional[str] = None
    
    # Hierarchy
    broker_id: Optional[int] = None
    
    # Verification status
    office_verified: bool = False
    document_verified: bool = False
    email_verified: bool = False
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    # Computed properties
    full_name: str
    requires_verification: bool
    cpd_valid: bool

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class UserAnalyticsResponse(BaseModel):
    """Schema for user analytics response"""
    user_id: int
    
    # Common metrics
    total_properties: int = 0
    active_leads: int = 0
    total_revenue: float = 0.0
    
    # Agent-specific metrics
    conversion_rate: Optional[float] = None
    site_visits_scheduled: Optional[int] = None
    reservations_made: Optional[int] = None
    closed_deals: Optional[int] = None
    
    # Developer-specific metrics
    projects_completed: Optional[int] = None
    units_sold: Optional[int] = None
    construction_started: Optional[int] = None
    
    # Broker-specific metrics
    team_size: Optional[int] = None
    team_revenue: Optional[float] = None
    best_performing_agent_id: Optional[int] = None
    
    last_updated: datetime

    class Config:
        from_attributes = True


class TeamMemberResponse(UserResponse):
    """Extended user response for team members"""
    analytics: Optional[UserAnalyticsResponse] = None


class TeamResponse(BaseModel):
    """Schema for broker team response"""
    broker: UserResponse
    members: List[TeamMemberResponse]
    team_analytics: Dict[str, Any]

    class Config:
        from_attributes = True

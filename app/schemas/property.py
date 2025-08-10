"""
Property schemas for data validation and serialization
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.property import PropertyStatus, PropertyType, ConstructionStatus


class PropertyBase(BaseModel):
    """Base property schema with common fields"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_name: str = Field(..., min_length=1, max_length=200)
    property_type: PropertyType
    
    # Location
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1, max_length=100)
    province: str = Field(..., min_length=1, max_length=100)
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyCreate(PropertyBase):
    """Schema for creating a new property"""
    # Property specifications
    floor_area: Optional[float] = None
    lot_area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = 0
    floors: Optional[int] = 1
    
    # Pricing
    price: float = Field(..., gt=0)
    expected_downpayment: Optional[float] = None
    reservation_fee: Optional[float] = 0.0
    
    # Payment schemes
    downpayment_percentage: Optional[float] = 20.0
    equity_percentage: Optional[float] = 20.0
    loanable_percentage: Optional[float] = 80.0
    
    # Construction trigger
    construction_trigger_percentage: Optional[float] = 50.0
    turnover_readiness_percentage: Optional[float] = 85.0
    
    # Legal documents
    license_to_sell_id: Optional[str] = None
    certificate_of_registration_id: Optional[str] = None
    
    # Media
    images: Optional[List[str]] = []
    virtual_tour_url: Optional[str] = None
    ar_model_url: Optional[str] = None
    floor_plan_url: Optional[str] = None
    
    # Features
    features: Optional[List[str]] = []
    amenities: Optional[List[str]] = []


class PropertyUpdate(BaseModel):
    """Schema for updating property information"""
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    construction_status: Optional[ConstructionStatus] = None
    
    # Location
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Specifications
    floor_area: Optional[float] = None
    lot_area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    floors: Optional[int] = None
    
    # Pricing
    price: Optional[float] = None
    expected_downpayment: Optional[float] = None
    reservation_fee: Optional[float] = None
    
    # Media
    images: Optional[List[str]] = None
    virtual_tour_url: Optional[str] = None
    ar_model_url: Optional[str] = None
    floor_plan_url: Optional[str] = None
    
    # Features
    features: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    
    # Visibility
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class PropertyResponse(PropertyBase):
    """Schema for property response"""
    id: int
    developer_id: int
    status: PropertyStatus
    construction_status: ConstructionStatus
    
    # Specifications
    floor_area: Optional[float] = None
    lot_area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: int = 0
    floors: int = 1
    
    # Pricing
    price: float
    expected_downpayment: Optional[float] = None
    reservation_fee: float = 0.0
    
    # Payment schemes
    downpayment_percentage: float = 20.0
    equity_percentage: float = 20.0
    loanable_percentage: float = 80.0
    construction_trigger_percentage: float = 50.0
    turnover_readiness_percentage: float = 85.0
    
    # Legal documents
    license_to_sell_id: Optional[str] = None
    license_to_sell_file: Optional[str] = None
    certificate_of_registration_id: Optional[str] = None
    certificate_of_registration_file: Optional[str] = None
    
    # Media
    images: Optional[List[str]] = []
    virtual_tour_url: Optional[str] = None
    ar_model_url: Optional[str] = None
    floor_plan_url: Optional[str] = None
    
    # Features
    features: Optional[List[str]] = []
    amenities: Optional[List[str]] = []
    
    # Visibility
    is_featured: bool = False
    is_active: bool = True
    views_count: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    construction_start_date: Optional[datetime] = None
    expected_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    
    # Computed properties
    is_available: bool
    downpayment_amount: float
    loanable_amount: float
    construction_trigger_amount: float

    class Config:
        from_attributes = True


class PropertyListResponse(BaseModel):
    """Schema for paginated property list response"""
    properties: List[PropertyResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class PropertyBulkCreate(BaseModel):
    """Schema for bulk property creation via CSV"""
    csv_data: List[Dict[str, Any]]
    project_name: str
    developer_id: int


class PropertyAssignmentCreate(BaseModel):
    """Schema for assigning property to broker/agent"""
    property_id: int
    user_id: int  # Broker or Agent ID
    is_exclusive: Optional[bool] = False
    commission_rate: Optional[float] = None
    expires_at: Optional[datetime] = None


class PropertyAssignmentResponse(BaseModel):
    """Schema for property assignment response"""
    id: int
    property_id: int
    user_id: int
    assigned_by: int
    is_active: bool
    is_exclusive: bool
    commission_rate: Optional[float] = None
    assigned_at: datetime
    expires_at: Optional[datetime] = None
    
    # Relationships
    property: PropertyResponse
    user: dict  # Basic user info
    assigner: dict  # Basic assigner info

    class Config:
        from_attributes = True


class BookmarkCreate(BaseModel):
    """Schema for creating a bookmark"""
    property_id: int


class BookmarkResponse(BaseModel):
    """Schema for bookmark response"""
    id: int
    user_id: int
    property_id: int
    created_at: datetime
    
    # Relationships
    property: PropertyResponse

    class Config:
        from_attributes = True


class MaintenanceRequestCreate(BaseModel):
    """Schema for creating maintenance request"""
    property_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category: Optional[str] = None
    priority: Optional[str] = "medium"
    images: Optional[List[str]] = []


class MaintenanceRequestResponse(BaseModel):
    """Schema for maintenance request response"""
    id: int
    property_id: int
    client_id: int
    title: str
    description: str
    category: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    assigned_to: Optional[int] = None
    images: Optional[List[str]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Relationships
    property: PropertyResponse
    client: dict  # Basic client info
    assigned_person: Optional[dict] = None  # Basic assignee info

    class Config:
        from_attributes = True

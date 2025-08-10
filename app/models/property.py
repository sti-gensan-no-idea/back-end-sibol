"""
Comprehensive Property model for Real Estate Management System
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class PropertyStatus(enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    UNDER_CONSTRUCTION = "under_construction"
    READY_FOR_TURNOVER = "ready_for_turnover"
    MAINTENANCE = "maintenance"


class PropertyType(enum.Enum):
    HOUSE_AND_LOT = "house_and_lot"
    CONDOMINIUM = "condominium"
    TOWNHOUSE = "townhouse"
    LOT_ONLY = "lot_only"
    COMMERCIAL = "commercial"


class ConstructionStatus(enum.Enum):
    NOT_STARTED = "not_started"
    FOUNDATION = "foundation"
    FRAMING = "framing"
    ROOFING = "roofing"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    FINISHING = "finishing"
    COMPLETED = "completed"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Developer information
    developer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_name = Column(String(200), nullable=False)  # e.g., "Camella Homes Subd"
    
    # Property details
    property_type = Column(Enum(PropertyType), nullable=False)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    construction_status = Column(Enum(ConstructionStatus), default=ConstructionStatus.NOT_STARTED)
    
    # Location
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    province = Column(String(100), nullable=False)
    zip_code = Column(String(10))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    
    # Property specifications
    floor_area = Column(Numeric(10, 2))  # Square meters
    lot_area = Column(Numeric(10, 2))    # Square meters
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    parking_spaces = Column(Integer, default=0)
    floors = Column(Integer, default=1)
    
    # Pricing
    price = Column(Numeric(15, 2), nullable=False)
    expected_downpayment = Column(Numeric(15, 2))  # From CSV or manual entry
    reservation_fee = Column(Numeric(15, 2), default=0.00)
    
    # Payment schemes
    downpayment_percentage = Column(Numeric(5, 2), default=20.00)  # Default 20%
    equity_percentage = Column(Numeric(5, 2), default=20.00)
    loanable_percentage = Column(Numeric(5, 2), default=80.00)
    
    # Construction trigger
    construction_trigger_percentage = Column(Numeric(5, 2), default=50.00)  # Start at 50% downpayment
    turnover_readiness_percentage = Column(Numeric(5, 2), default=85.00)   # Ready at 80-90%
    
    # Legal documents
    license_to_sell_id = Column(String(100))  # License to Sale ID
    license_to_sell_file = Column(String(500))  # File path/URL
    certificate_of_registration_id = Column(String(100))  # Certificate ID
    certificate_of_registration_file = Column(String(500))  # File path/URL
    
    # Media and virtual tour
    images = Column(JSON)  # Array of image URLs
    virtual_tour_url = Column(String(500))
    ar_model_url = Column(String(500))  # AR model for viewing
    floor_plan_url = Column(String(500))
    
    # Features and amenities
    features = Column(JSON)  # Array of property features
    amenities = Column(JSON)  # Array of community amenities
    
    # Visibility and marketing
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    construction_start_date = Column(DateTime(timezone=True))
    expected_completion_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Relationships
    developer = relationship("User", foreign_keys=[developer_id], back_populates="owned_properties")
    assignments = relationship("PropertyAssignment", back_populates="property", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="property", cascade="all, delete-orphan")
    site_visits = relationship("SiteVisit", back_populates="property", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="property")
    contracts = relationship("Contract", back_populates="property")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property")
    
    @property
    def is_available(self) -> bool:
        """Check if property is available for sale"""
        return self.status == PropertyStatus.AVAILABLE and self.is_active
    
    @property
    def downpayment_amount(self) -> float:
        """Calculate downpayment amount"""
        return float(self.price * self.downpayment_percentage / 100)
    
    @property
    def loanable_amount(self) -> float:
        """Calculate loanable amount"""
        return float(self.price * self.loanable_percentage / 100)
    
    @property
    def construction_trigger_amount(self) -> float:
        """Amount needed to trigger construction"""
        return float(self.price * self.construction_trigger_percentage / 100)
    
    @property
    def is_construction_ready(self) -> bool:
        """Check if construction can be started (based on payment received)"""
        # This would check actual payments received vs trigger amount
        return False  # Would need payment calculation logic
    
    def __repr__(self):
        return f"<Property(id={self.id}, title='{self.title}', status='{self.status.value}')>"


class PropertyAssignment(Base):
    """Property assignments to brokers/agents"""
    __tablename__ = "property_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Broker or Agent
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who made the assignment
    
    # Assignment details
    is_active = Column(Boolean, default=True)
    is_exclusive = Column(Boolean, default=False)  # Exclusive assignment
    commission_rate = Column(Numeric(5, 2))  # Commission percentage
    
    # Timestamps
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    property = relationship("Property", back_populates="assignments")
    user = relationship("User", foreign_keys=[user_id], back_populates="assigned_properties")
    assigner = relationship("User", foreign_keys=[assigned_by])


class Bookmark(Base):
    """Client property bookmarks"""
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookmarked_properties")
    property = relationship("Property", back_populates="bookmarks")


class MaintenanceRequest(Base):
    """Maintenance requests from clients to developers"""
    __tablename__ = "maintenance_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))  # Plumbing, Electrical, etc.
    priority = Column(String(50), default="medium")  # low, medium, high, urgent
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    assigned_to = Column(Integer, ForeignKey("users.id"))  # Maintenance personnel
    
    # Media
    images = Column(JSON)  # Array of issue images
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    property = relationship("Property", back_populates="maintenance_requests")
    client = relationship("User", foreign_keys=[client_id])
    assigned_person = relationship("User", foreign_keys=[assigned_to])

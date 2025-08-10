"""
Enhanced Property model with comprehensive features and relationships
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, ForeignKey, JSON
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class PropertyType(enum.Enum):
    VILLA = "VILLA"
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    CONDO = "CONDO"
    TOWNHOUSE = "TOWNHOUSE"
    COMMERCIAL = "COMMERCIAL"
    LAND = "LAND"


class PropertyStatus(enum.Enum):
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"
    SOLD = "SOLD"
    RENTED = "RENTED"
    MAINTENANCE = "MAINTENANCE"
    INACTIVE = "INACTIVE"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    price = Column(Decimal(12, 2), nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    address = Column(Text)
    
    # Property Details
    type = Column(Enum(PropertyType), nullable=False, index=True)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE, index=True)
    total_bed = Column(Integer, default=0)
    total_bathroom = Column(Integer, default=0)
    area_size = Column(Decimal(10, 2))  # in square meters
    lot_size = Column(Decimal(10, 2))   # in square meters
    floor_count = Column(Integer, default=1)
    parking_spaces = Column(Integer, default=0)
    year_built = Column(Integer)
    
    # Features and Amenities
    features = Column(JSON)  # Store as JSON array
    amenities = Column(JSON)  # Store as JSON array
    
    # Media and AR
    thumbnail = Column(String(500))
    image_360 = Column(String(500))
    images = Column(JSON)  # Array of image URLs
    ar_model_url = Column(String(500))
    ar_scene_config = Column(JSON)
    virtual_tour_url = Column(String(500))
    
    # Financial Information
    monthly_rent = Column(Decimal(10, 2))
    security_deposit = Column(Decimal(10, 2))
    maintenance_fee = Column(Decimal(10, 2))
    property_tax = Column(Decimal(10, 2))
    
    # Utilities
    electricity_included = Column(Boolean, default=False)
    water_included = Column(Boolean, default=False)
    gas_included = Column(Boolean, default=False)
    internet_included = Column(Boolean, default=False)
    
    # Property Management
    property_manager = Column(String(255))
    property_manager_contact = Column(String(100))
    
    # SEO and Marketing
    seo_title = Column(String(255))
    seo_description = Column(Text)
    keywords = Column(JSON)  # Array of keywords
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    owner = relationship("User", back_populates="properties")
    contracts = relationship("Contract", back_populates="property", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="property", cascade="all, delete-orphan")
    listing = relationship("PropertyListing", back_populates="property", uselist=False, cascade="all, delete-orphan")
    events = relationship("Event", back_populates="property", cascade="all, delete-orphan")
    analytics = relationship("PropertyAnalytics", back_populates="property", uselist=False, cascade="all, delete-orphan")
    
    @property
    def is_available(self) -> bool:
        """Check if property is available"""
        return self.status == PropertyStatus.AVAILABLE
    
    @property
    def is_for_rent(self) -> bool:
        """Check if property is for rent"""
        return self.monthly_rent is not None and self.monthly_rent > 0
    
    @property
    def is_for_sale(self) -> bool:
        """Check if property is for sale"""
        return self.price is not None and self.price > 0
    
    @property
    def total_rooms(self) -> int:
        """Get total number of rooms"""
        return (self.total_bed or 0) + (self.total_bathroom or 0)
    
    @property
    def price_per_sqm(self) -> float:
        """Calculate price per square meter"""
        if self.area_size and self.area_size > 0:
            return float(self.price / self.area_size)
        return 0.0
    
    def __repr__(self):
        return f"<Property(id={self.id}, title='{self.title}', type='{self.type.value}', status='{self.status.value}')>"


class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    amount = Column(Decimal(12, 2), default=0.00, nullable=False)
    
    # Balance tracking
    available_balance = Column(Decimal(12, 2), default=0.00)
    pending_balance = Column(Decimal(12, 2), default=0.00)
    escrow_balance = Column(Decimal(12, 2), default=0.00)
    
    # Currency
    currency = Column(String(3), default="PHP")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_transaction_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="balance")
    
    @property
    def total_balance(self) -> float:
        """Get total balance"""
        return float(self.amount or 0)
    
    def __repr__(self):
        return f"<Balance(user_id={self.user_id}, amount={self.amount})>"


class PropertyListing(Base):
    __tablename__ = "property_listings"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, unique=True, index=True)
    
    # Listing Status
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, PENDING, SOLD, RENTED
    
    # Analytics
    views = Column(Integer, default=0)
    inquiries = Column(Integer, default=0)
    favorites = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # SEO and Marketing
    featured = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    boost_expires = Column(DateTime(timezone=True))
    
    # Timestamps
    listed_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delisted_at = Column(DateTime(timezone=True))
    
    # Relationships
    property = relationship("Property", back_populates="listing")
    
    def __repr__(self):
        return f"<PropertyListing(property_id={self.property_id}, status='{self.status}', views={self.views})>"


class PropertyAnalytics(Base):
    __tablename__ = "property_analytics"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, unique=True, index=True)
    
    # View Analytics
    total_views = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    total_inquiries = Column(Integer, default=0)
    conversion_rate = Column(Decimal(5, 2), default=0.00)  # Percentage
    
    # Performance Metrics
    avg_time_on_market = Column(String(50))  # e.g., "30 days"
    price_changes = Column(Integer, default=0)
    last_price_change = Column(DateTime(timezone=True))
    
    # Engagement Metrics
    avg_session_duration = Column(Integer, default=0)  # in seconds
    bounce_rate = Column(Decimal(5, 2), default=0.00)  # Percentage
    
    # Lead Quality
    qualified_leads = Column(Integer, default=0)
    tours_scheduled = Column(Integer, default=0)
    tours_completed = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    property = relationship("Property", back_populates="analytics")
    
    def __repr__(self):
        return f"<PropertyAnalytics(property_id={self.property_id}, views={self.total_views}, conversion_rate={self.conversion_rate})>"

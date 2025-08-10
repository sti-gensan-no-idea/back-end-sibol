"""
Comprehensive User model for Real Estate Management System
Supporting Developer, Broker, Agent, Client, and Admin roles
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class UserRole(enum.Enum):
    ADMIN = "admin"
    DEVELOPER = "developer" 
    BROKER = "broker"
    AGENT = "agent"
    CLIENT = "client"


class AccountStatus(enum.Enum):
    PENDING = "pending"  # Account created but not verified
    ACTIVE = "active"    # Account verified and active
    INACTIVE = "inactive"  # Account deactivated
    SUSPENDED = "suspended"  # Account suspended


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)  # For JWT payload
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    status = Column(Enum(AccountStatus), default=AccountStatus.PENDING, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Profile fields
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    profile_image = Column(String(500))
    
    # Professional credentials (for brokers and agents)
    license_number = Column(String(100))  # PRC License number
    cpd_units = Column(Integer, default=0)  # CPD credit units
    cpd_expiry = Column(DateTime(timezone=True))  # CPD renewal date
    pic_number = Column(String(100))  # Professional Identification Card
    pic_expiry = Column(DateTime(timezone=True))
    
    # Office/Company information
    company_name = Column(String(200))
    company_address = Column(Text)
    company_phone = Column(String(20))
    
    # Team/hierarchy relationships
    broker_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Agent's broker
    team_name = Column(String(100))  # Broker's team name
    
    # Verification status
    office_verified = Column(Boolean, default=False)  # Office verification for brokers/developers
    document_verified = Column(Boolean, default=False)  # Document verification
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255))
    
    # Password reset
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime(timezone=True))
    
    # Relationships
    broker = relationship("User", remote_side=[id], back_populates="agents")  # Broker of this agent
    agents = relationship("User", back_populates="broker", cascade="all, delete-orphan")  # Agents under this broker
    
    # Properties owned (for developers)
    owned_properties = relationship("Property", foreign_keys="Property.developer_id", back_populates="developer")
    
    # Properties assigned/handled
    assigned_properties = relationship("PropertyAssignment", back_populates="user")
    
    # Bookmarked properties (for clients)
    bookmarked_properties = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    
    # Client interactions
    leads = relationship("Lead", back_populates="agent")
    site_visits = relationship("SiteVisit", back_populates="client")
    
    # Contracts and payments
    tenant_contracts = relationship("Contract", back_populates="tenant")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    
    # Communication
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    # Analytics and performance
    analytics = relationship("UserAnalytics", back_populates="user", uselist=False)
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email.split('@')[0]
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_developer(self) -> bool:
        """Check if user is developer"""
        return self.role == UserRole.DEVELOPER
    
    @property
    def is_broker(self) -> bool:
        """Check if user is broker"""
        return self.role == UserRole.BROKER
    
    @property
    def is_agent(self) -> bool:
        """Check if user is agent"""
        return self.role == UserRole.AGENT
    
    @property
    def is_client(self) -> bool:
        """Check if user is client"""
        return self.role == UserRole.CLIENT
    
    @property
    def requires_verification(self) -> bool:
        """Check if user role requires office verification"""
        return self.role in [UserRole.DEVELOPER, UserRole.BROKER]
    
    @property
    def cpd_valid(self) -> bool:
        """Check if CPD is still valid"""
        if not self.cpd_expiry:
            return False
        return self.cpd_expiry > func.now()
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"


class UserAnalytics(Base):
    """User analytics and performance metrics"""
    __tablename__ = "user_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Common metrics
    total_properties = Column(Integer, default=0)
    active_leads = Column(Integer, default=0)
    total_revenue = Column(Numeric(15, 2), default=0.00)
    
    # Agent-specific metrics
    conversion_rate = Column(Numeric(5, 2), default=0.00)  # Percentage
    site_visits_scheduled = Column(Integer, default=0)
    reservations_made = Column(Integer, default=0)
    closed_deals = Column(Integer, default=0)
    
    # Developer-specific metrics
    projects_completed = Column(Integer, default=0)
    units_sold = Column(Integer, default=0)
    construction_started = Column(Integer, default=0)
    
    # Broker-specific metrics
    team_size = Column(Integer, default=0)
    team_revenue = Column(Numeric(15, 2), default=0.00)
    best_performing_agent_id = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="analytics")
    best_performing_agent = relationship("User", foreign_keys=[best_performing_agent_id])

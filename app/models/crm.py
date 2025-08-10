"""
CRM Pipeline and Lead Management Models
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class LeadStatus(enum.Enum):
    PROSPECTING = "prospecting"      # Initial interest
    CONTACTED = "contacted"          # Agent has made contact
    SITE_VIEWED = "site_viewed"     # Property has been viewed
    RESERVED = "reserved"           # Property reserved
    CLOSED = "closed"               # Deal completed
    LOST = "lost"                   # Lead lost


class LeadSource(enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    WALK_IN = "walk_in"
    PHONE_INQUIRY = "phone_inquiry"
    EMAIL_INQUIRY = "email_inquiry"


class SiteVisitStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Lead(Base):
    """Lead management for CRM pipeline"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Client information
    client_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Can be null for guest leads
    guest_name = Column(String(200))  # For guest leads
    guest_email = Column(String(255))
    guest_phone = Column(String(20))
    
    # Agent and property
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    
    # Lead details
    status = Column(Enum(LeadStatus), default=LeadStatus.PROSPECTING)
    source = Column(Enum(LeadSource), default=LeadSource.WEBSITE)
    priority = Column(String(20), default="medium")  # low, medium, high
    
    # Communication tracking
    last_contact = Column(DateTime(timezone=True))
    next_followup = Column(DateTime(timezone=True))
    contact_attempts = Column(Integer, default=0)
    
    # Notes and details
    notes = Column(Text)
    tags = Column(JSON)  # Array of tags for categorization
    
    # Qualification details
    budget_min = Column(Numeric(15, 2))
    budget_max = Column(Numeric(15, 2))
    preferred_location = Column(String(255))
    move_in_timeline = Column(String(100))  # e.g., "3-6 months"
    financing_method = Column(String(100))  # cash, bank_loan, in_house
    
    # Conversion metrics
    days_in_pipeline = Column(Integer, default=0)
    touchpoints = Column(Integer, default=0)  # Number of interactions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status_changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("User", foreign_keys=[client_id])
    agent = relationship("User", foreign_keys=[agent_id], back_populates="leads")
    property = relationship("Property", back_populates="leads")
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    site_visits = relationship("SiteVisit", back_populates="lead")
    
    @property
    def client_name(self) -> str:
        """Get client name (registered or guest)"""
        if self.client:
            return self.client.full_name
        return self.guest_name or "Unknown"
    
    @property
    def client_email(self) -> str:
        """Get client email (registered or guest)"""
        if self.client:
            return self.client.email
        return self.guest_email
    
    def __repr__(self):
        return f"<Lead(id={self.id}, client='{self.client_name}', status='{self.status.value}')>"


class LeadActivity(Base):
    """Track all activities related to a lead"""
    __tablename__ = "lead_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who performed the activity
    
    # Activity details
    activity_type = Column(String(100), nullable=False)  # call, email, meeting, site_visit, etc.
    subject = Column(String(255))
    description = Column(Text)
    
    # Status tracking
    completed = Column(Boolean, default=True)
    scheduled_for = Column(DateTime(timezone=True))  # For future activities
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lead = relationship("Lead", back_populates="activities")
    user = relationship("User", foreign_keys=[user_id])


class SiteVisit(Base):
    """Site visit scheduling and management"""
    __tablename__ = "site_visits"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Participants
    client_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Can be guest
    guest_name = Column(String(200))
    guest_email = Column(String(255))
    guest_phone = Column(String(20))
    
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)  # Connected to lead if exists
    
    # Visit details
    status = Column(Enum(SiteVisitStatus), default=SiteVisitStatus.SCHEDULED)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    
    # Visit information
    number_of_attendees = Column(Integer, default=1)
    special_requirements = Column(Text)  # Wheelchair access, etc.
    transportation_needed = Column(Boolean, default=False)
    
    # Follow-up
    agent_notes = Column(Text)
    client_feedback = Column(Text)
    interest_level = Column(String(20))  # low, medium, high
    next_steps = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="site_visits")
    agent = relationship("User", foreign_keys=[agent_id])
    property = relationship("Property", back_populates="site_visits")
    lead = relationship("Lead", back_populates="site_visits")
    
    @property
    def client_name(self) -> str:
        """Get client name (registered or guest)"""
        if self.client:
            return self.client.full_name
        return self.guest_name or "Unknown"
    
    def __repr__(self):
        return f"<SiteVisit(id={self.id}, client='{self.client_name}', date='{self.scheduled_date}')>"


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(100))  # lead_update, site_visit, payment, etc.
    
    # Status
    read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    # Optional references
    reference_id = Column(Integer)  # ID of related object
    reference_type = Column(String(100))  # Type of related object
    
    # Action URL
    action_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")

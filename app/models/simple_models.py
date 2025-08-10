"""
Simplified models for basic functionality
"""

# Import all the working models
from app.models.user import User, UserRole
from app.models.chat import Chatroom, Message

# Create minimal models for other functionality
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Enum
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from datetime import datetime

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
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    price = Column(Decimal(12, 2), nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    address = Column(Text)
    
    type = Column(Enum(PropertyType), nullable=False, index=True)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE, index=True)
    total_bed = Column(Integer, default=0)
    total_bathroom = Column(Integer, default=0)
    area_size = Column(Decimal(10, 2))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ContractStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.DRAFT)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    monthly_rent = Column(Decimal(10, 2), nullable=False)
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    amount = Column(Decimal(12, 2), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    description = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TransactionType(enum.Enum):
    PURCHASE = "PURCHASE"
    COMMISSION = "COMMISSION"
    REFUND = "REFUND"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"))
    
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Decimal(12, 2), nullable=False)
    description = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Balance(Base):
    __tablename__ = "balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    amount = Column(Decimal(12, 2), default=0.00, nullable=False)
    currency = Column(String(3), default="PHP")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Export all models
__all__ = [
    "User", "UserRole", "Property", "PropertyType", "PropertyStatus", 
    "Contract", "ContractStatus", "Payment", "PaymentStatus", 
    "Transaction", "TransactionType", "Balance", "Chatroom", "Message"
]

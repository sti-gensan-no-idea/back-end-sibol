# app/models/user.py
from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    SUB_ADMIN = "SUB_ADMIN"
    AGENT = "AGENT"
    CLIENT = "CLIENT"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    
    properties = relationship("Property", back_populates="owner")
    contracts = relationship("Contract", back_populates="tenant")
from sqlalchemy import Column, Integer, String, Boolean, Enum
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
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    payments = relationship("Payment", back_populates="user")
    balance = relationship("Balance", back_populates="user", uselist=False)
    properties = relationship("Property", back_populates="owner")
    contracts = relationship("Contract", back_populates="tenant")
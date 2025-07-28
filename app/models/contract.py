# app/models/contract.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    tenant_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    status = Column(String, default="PENDING")
    
    property = relationship("Property", back_populates="contracts")
    tenant = relationship("User", back_populates="contracts")
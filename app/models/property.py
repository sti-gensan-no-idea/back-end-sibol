# app/models/property.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.database import Base

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., apartment, house, commercial
    status = Column(String, default="available")  # available, rented, sold
    owner_id = Column(Integer, ForeignKey("users.id"))
    ar_model_url = Column(String, nullable=True)  # URL to 3D model for AR
    ar_scene_config = Column(String, nullable=True)  # JSON string for AR scene setup
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
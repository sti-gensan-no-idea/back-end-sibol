# app/models/property.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    location = Column(String)
    type = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="AVAILABLE")
    ar_model_url = Column(String, nullable=True)
    ar_scene_config = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)
    image_360 = Column(String, nullable=True)
    address = Column(String, nullable=True)
    total_bed = Column(Integer, nullable=True)
    total_bathroom = Column(Integer, nullable=True)
    area_size = Column(Float, nullable=True)
    
    owner = relationship("User", back_populates="properties")
    contracts = relationship("Contract", back_populates="property")
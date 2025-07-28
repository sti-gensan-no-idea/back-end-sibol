# app/schemas/property.py
from pydantic import BaseModel
from typing import Optional

class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    location: str
    type: str
    owner_id: int
    ar_model_url: Optional[str] = None
    thumbnail: Optional[str] = None
    image_360: Optional[str] = None
    address: Optional[str] = None
    total_bed: Optional[int] = None
    total_bathroom: Optional[int] = None
    area_size: Optional[float] = None

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    type: Optional[str] = None
    owner_id: Optional[int] = None
    ar_model_url: Optional[str] = None
    thumbnail: Optional[str] = None
    image_360: Optional[str] = None
    address: Optional[str] = None
    total_bed: Optional[int] = None
    total_bathroom: Optional[int] = None
    area_size: Optional[float] = None

class PropertyResponse(PropertyBase):
    id: int
    status: str
    ar_scene_config: Optional[str] = None

    class Config:
        from_attributes = True
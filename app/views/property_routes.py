# app/views/property_routes.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.property_controller import PropertyController
from app.services.auth_service import get_current_user, oauth2_scheme
from app.models.user import User

router = APIRouter()

class PropertyCreate(BaseModel):
    title: str
    description: str
    price: float
    location: str
    type: str
    owner_id: int
    ar_model_url: str | None = None

class PropertyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    location: str | None = None
    type: str | None = None
    owner_id: int | None = None
    ar_model_url: str | None = None

@router.post("/", summary="Create a new property")
async def create_property(property: PropertyCreate, db: Session = Depends(get_db), 
                        current_user: User = Depends(get_current_user)):
    return PropertyController.create_property(
        db, 
        property.title, 
        property.description, 
        property.price, 
        property.location, 
        property.type, 
        property.owner_id,
        property.ar_model_url,
        current_user
    )

@router.get("/{property_id}", summary="Get a property by ID")
async def get_property(property_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    return PropertyController.get_property(db, property_id)

@router.get("/", summary="Get a list of properties")
async def get_properties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    return PropertyController.get_properties(db, skip, limit)

@router.put("/{property_id}", summary="Update a property")
async def update_property(property_id: int, property: PropertyUpdate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    return PropertyController.update_property(
        db, 
        property_id, 
        property.title, 
        property.description, 
        property.price, 
        property.location, 
        property.type, 
        property.owner_id,
        property.ar_model_url,
        current_user
    )

@router.delete("/{property_id}", summary="Delete a property")
async def delete_property(property_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    return PropertyController.delete_property(db, property_id, current_user)

@router.post("/{property_id}/generate-description", summary="Generate AI-powered property description")
async def generate_property_description(property_id: int, db: Session = Depends(get_db),
                                     current_user: User = Depends(get_current_user)):
    return await PropertyController.generate_property_description(db, property_id, current_user)

@router.get("/{property_id}/ar-view", summary="Get AR view data for a property")
async def get_ar_property_view(property_id: int, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    return PropertyController.get_ar_property_view(db, property_id, current_user)
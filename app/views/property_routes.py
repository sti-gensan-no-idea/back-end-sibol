# app/views/property_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.property_controller import PropertyController
from app.services.auth_service import get_current_user
from app.models.user import User
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse

router = APIRouter()

@router.post("/", response_model=PropertyResponse, summary="Create a new property")
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
        current_user,
        property.thumbnail,
        property.image_360,
        property.address,
        property.total_bed,
        property.total_bathroom,
        property.area_size
    )

@router.get("/{property_id}", response_model=PropertyResponse, summary="Get a property by ID")
async def get_property(property_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    return PropertyController.get_property(db, property_id)

@router.get("/", response_model=list[PropertyResponse], summary="Get a list of properties")
async def get_properties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    return PropertyController.get_properties(db, skip, limit)

@router.put("/{property_id}", response_model=PropertyResponse, summary="Update a property")
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
        current_user,
        property.thumbnail,
        property.image_360,
        property.address,
        property.total_bed,
        property.total_bathroom,
        property.area_size
    )

@router.delete("/{property_id}", response_model=dict, summary="Delete a property")
async def delete_property(property_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    return PropertyController.delete_property(db, property_id, current_user)

@router.post("/{property_id}/generate-description", response_model=PropertyResponse, summary="Generate AI-powered property description")
async def generate_property_description(property_id: int, db: Session = Depends(get_db),
                                       current_user: User = Depends(get_current_user)):
    return await PropertyController.generate_property_description(db, property_id, current_user)

@router.get("/{property_id}/ar-view", response_model=dict, summary="Get AR view data for a property")
async def get_ar_property_view(property_id: int, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    return PropertyController.get_ar_property_view(db, property_id, current_user)
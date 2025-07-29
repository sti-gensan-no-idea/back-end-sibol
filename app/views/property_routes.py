from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.controllers.property_controller import PropertyController
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()

@router.post("/api/v1/properties/", response_model=dict)
async def create_property(property: PropertyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PropertyController.create_property(
        db=db,
        title=property.title,
        description=property.description,
        price=property.price,
        location=property.location,
        type=property.type,
        owner_id=property.owner_id,
        ar_model_url=property.ar_model_url,
        current_user=current_user,
        thumbnail=property.thumbnail,
        image_360=property.image_360,
        address=property.address,
        total_bed=property.total_bed,
        total_bathroom=property.total_bathroom,
        area_size=property.area_size
    )

@router.get("/api/v1/properties/{property_id}", response_model=dict)
async def get_property(property_id: int, db: Session = Depends(get_db)):
    return PropertyController.get_property(db, property_id)

@router.get("/api/v1/properties/", response_model=list[dict])
async def get_properties(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return PropertyController.get_properties(db, skip, limit)

@router.put("/api/v1/properties/{property_id}", response_model=dict)
async def update_property(property_id: int, property: PropertyUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PropertyController.update_property(
        db=db,
        property_id=property_id,
        title=property.title,
        description=property.description,
        price=property.price,
        location=property.location,
        type=property.type,
        owner_id=property.owner_id,
        ar_model_url=property.ar_model_url,
        current_user=current_user,
        thumbnail=property.thumbnail,
        image_360=property.image_360,
        address=property.address,
        total_bed=property.total_bed,
        total_bathroom=property.total_bathroom,
        area_size=property.area_size
    )

@router.delete("/api/v1/properties/{property_id}", response_model=dict)
async def delete_property(property_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PropertyController.delete_property(db, property_id, current_user)

@router.get("/api/v1/properties/{property_id}/ar-view", response_model=dict)
async def get_ar_property_view(property_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PropertyController.get_ar_property_view(db, property_id, current_user)
# app/controllers/property_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.property import Property
from app.models.user import UserRole
from app.services.ai_service import AIService
from app.services.ar_service import ARService

class PropertyController:
    @staticmethod
    def create_property(db: Session, title: str, description: str, price: float, 
                      location: str, type: str, owner_id: int, ar_model_url: str, current_user):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        property = Property(
            title=title,
            description=description,
            price=price,
            location=location,
            type=type,
            owner_id=owner_id,
            ar_model_url=ar_model_url
        )
        ar_service = ARService()
        property_details = {
            "id": property.id,
            "title": title,
            "type": type,
            "location": location
        }
        property.ar_scene_config = ar_service.generate_ar_scene_config(property_details)
        db.add(property)
        db.commit()
        db.refresh(property)
        return property

    @staticmethod
    def get_property(db: Session, property_id: int):
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        return property

    @staticmethod
    def get_properties(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Property).offset(skip).limit(limit).all()

    @staticmethod
    def update_property(db: Session, property_id: int, title: str = None, description: str = None, 
                      price: float = None, location: str = None, type: str = None, 
                      owner_id: int = None, ar_model_url: str = None, current_user=None):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        if title:
            property.title = title
        if description:
            property.description = description
        if price:
            property.price = price
        if location:
            property.location = location
        if type:
            property.type = type
        if owner_id:
            property.owner_id = owner_id
        if ar_model_url:
            property.ar_model_url = ar_model_url
            ar_service = ARService()
            property_details = {
                "id": property.id,
                "title": property.title,
                "type": property.type,
                "location": property.location
            }
            property.ar_scene_config = ar_service.generate_ar_scene_config(property_details)
        db.commit()
        db.refresh(property)
        return property

    @staticmethod
    def delete_property(db: Session, property_id: int, current_user):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        db.delete(property)
        db.commit()
        return {"detail": "Property deleted"}

    @staticmethod
    async def generate_property_description(db: Session, property_id: int, current_user):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        ai_service = AIService()
        property_details = {
            "title": property.title,
            "price": property.price,
            "location": property.location,
            "type": property.type
        }
        description = await ai_service.generate_property_description(property_details)
        property.description = description
        db.commit()
        db.refresh(property)
        return property

    @staticmethod
    def get_ar_property_view(db: Session, property_id: int, current_user):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT, UserRole.CLIENT]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return {
            "property_id": property.id,
            "ar_model_url": property.ar_model_url,
            "ar_scene_config": property.ar_scene_config
        }
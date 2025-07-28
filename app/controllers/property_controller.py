# app/controllers/property_controller.py
from sqlalchemy.orm import Session
from app.models.property import Property
from app.models.user import User, UserRole  # Added User import
from fastapi import HTTPException
from app.config.settings import settings
import openai
import json

class PropertyController:
    @staticmethod
    def create_property(db: Session, title: str, description: str, price: float, location: str, type: str,
                       owner_id: int, ar_model_url: str, current_user: User, thumbnail: str, image_360: str,
                       address: str, total_bed: int, total_bathroom: int, area_size: float):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
            raise HTTPException(status_code=403, detail="Not authorized")
        owner = db.query(User).filter(User.id == owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")
        ar_scene_config = json.dumps({"model_url": ar_model_url, "scale": 1.0, "rotation": 0}) if ar_model_url else None
        property = Property(
            title=title, description=description, price=price, location=location, type=type,
            owner_id=owner_id, ar_model_url=ar_model_url, ar_scene_config=ar_scene_config,
            thumbnail=thumbnail, image_360=image_360, address=address, total_bed=total_bed,
            total_bathroom=total_bathroom, area_size=area_size
        )
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
    def get_properties(db: Session, skip: int, limit: int):
        return db.query(Property).offset(skip).limit(limit).all()

    @staticmethod
    def update_property(db: Session, property_id: int, title: str, description: str, price: float, 
                       location: str, type: str, owner_id: int, ar_model_url: str, current_user: User,
                       thumbnail: str, image_360: str, address: str, total_bed: int, 
                       total_bathroom: int, area_size: float):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
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
            owner = db.query(User).filter(User.id == owner_id).first()
            if not owner:
                raise HTTPException(status_code=404, detail="Owner not found")
            property.owner_id = owner_id
        if ar_model_url:
            property.ar_model_url = ar_model_url
            property.ar_scene_config = json.dumps({"model_url": ar_model_url, "scale": 1.0, "rotation": 0})
        if thumbnail:
            property.thumbnail = thumbnail
        if image_360:
            property.image_360 = image_360
        if address:
            property.address = address
        if total_bed:
            property.total_bed = total_bed
        if total_bathroom:
            property.total_bathroom = total_bathroom
        if area_size:
            property.area_size = area_size
        db.commit()
        db.refresh(property)
        return property

    @staticmethod
    def delete_property(db: Session, property_id: int, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
            raise HTTPException(status_code=403, detail="Not authorized")
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        db.delete(property)
        db.commit()
        return {"message": "Property deleted"}

    @staticmethod
    async def generate_property_description(db: Session, property_id: int, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
            raise HTTPException(status_code=403, detail="Not authorized")
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        openai.api_key = settings.AI_API_KEY
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Generate a detailed description for a real estate property: {property.title}, located at {property.address}, {property.location}. Type: {property.type}, Price: ${property.price}, Beds: {property.total_bed}, Baths: {property.total_bathroom}, Area: {property.area_size} sq ft.",
                max_tokens=200
            )
            property.description = response.choices[0].text.strip()
            db.commit()
            db.refresh(property)
            return property
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

    @staticmethod
    def get_ar_property_view(db: Session, property_id: int, current_user: User):
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        return {
            "ar_model_url": property.ar_model_url,
            "ar_scene_config": property.ar_scene_config,
            "thumbnail": property.thumbnail,
            "image_360": property.image_360
        }
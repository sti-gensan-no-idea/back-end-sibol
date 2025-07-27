# app/controllers/user_controller.py
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.services.email_service import send_registration_email
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserController:
    @staticmethod
    def create_user(db: Session, email: str, password: str, role: UserRole):
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = pwd_context.hash(password)
        user = User(email=email, password=hashed_password, role=role, is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        # Send registration email
        send_registration_email(email, f"Welcome to {settings.APP_NAME}!")
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not pwd_context.verify(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        from app.services.auth_service import create_access_token
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def get_users(db: Session, skip: int, limit: int):
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, email: str, password: str, role: UserRole, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if email:
            user.email = email
        if password:
            user.password = pwd_context.hash(password)
        if role:
            user.role = role
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_active = False
        db.commit()
        return {"message": "User deactivated"}
# app/controllers/user_controller.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.services.auth_service import get_password_hash, verify_password, create_access_token

class UserController:
    @staticmethod
    def create_user(db: Session, email: str, password: str, role: UserRole):
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = get_password_hash(password)
        user = User(email=email, hashed_password=hashed_password, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, email: str = None, password: str = None, role: UserRole = None, current_user: User = None):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN] and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if email:
            if db.query(User).filter(User.email == email, User.id != user_id).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = email
        if password:
            user.hashed_password = get_password_hash(password)
        if role and current_user.role in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            user.role = role
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN] and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = False
        db.commit()
        return {"detail": "User deactivated"}

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email, User.is_active == True).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
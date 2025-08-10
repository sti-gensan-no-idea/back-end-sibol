from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.services.auth_service import hash_password, create_access_token, verify_password
from fastapi import HTTPException

class UserController:
    @staticmethod
    async def create_user(db: Session, email: str, password: str, role: str, background_tasks=None):
        # Check if user already exists
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate role
        if not isinstance(role, str):
            raise HTTPException(status_code=400, detail="Role must be a string")
        
        try:
            user_role = UserRole[role.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        # Create new user
        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=user_role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "access_token": access_token,
            "token_type": "bearer"
        }

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.email})
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value
            }
        }

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
    def update_user(db: Session, user_id: int, email: str, password: str, role: str, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if email:
            db_user = db.query(User).filter(User.email == email, User.id != user_id).first()
            if db_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = email
        
        if password:
            user.hashed_password = hash_password(password)
        
        if role:
            if not isinstance(role, str):
                raise HTTPException(status_code=400, detail="Role must be a string")
            try:
                user_role = UserRole[role.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail="Invalid role")
            user.role = user_role
        
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
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}

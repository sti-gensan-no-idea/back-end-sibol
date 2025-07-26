# app/views/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.user_controller import UserController
from app.models.user import UserRole, User
from app.services.auth_service import get_current_user, oauth2_scheme

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole

class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    role: UserRole | None = None

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register", summary="Register a new user")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserController.create_user(db, user.email, user.password, user.role)

@router.post("/login", summary="User login with email and password")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    return UserController.authenticate_user(db, user.email, user.password)

@router.get("/me", summary="Get current authenticated user")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", summary="Get a user by ID")
async def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return UserController.get_user(db, user_id)

@router.get("/", summary="Get a list of users")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
                  current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return UserController.get_users(db, skip, limit)

@router.put("/{user_id}", summary="Update a user")
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user)):
    return UserController.update_user(db, user_id, user.email, user.password, user.role, current_user)

@router.delete("/{user_id}", summary="Delete (deactivate) a user")
async def delete_user(user_id: int, db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user)):
    return UserController.delete_user(db, user_id, current_user)
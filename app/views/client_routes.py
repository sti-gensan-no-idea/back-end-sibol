"""
Client routes for client management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.database import get_db
from app.controllers.user_controller import UserController
from app.models.user import User, UserRole
from app.services.auth_service import get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.crm import SiteVisitCreate, SiteVisitResponse, SiteVisitListResponse
from app.schemas.property import BookmarkCreate, BookmarkResponse

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/",
             response_model=UserResponse,
             summary="Create client account",
             description="Register a new client account")
async def create_client(
    client_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new client account"""
    # Force role to CLIENT
    client_data.role = UserRole.CLIENT
    
    try:
        client = await UserController.create_user(
            db=db,
            email=client_data.email,
            password=client_data.password,
            role=UserRole.CLIENT,
            user_data=client_data.dict(exclude={"password", "role"})
        )
        return client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/",
            response_model=UserListResponse,
            summary="Get paginated list of clients",
            description="Retrieve all clients with pagination")
async def get_clients(
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of clients"""
    # Only admins, developers, and brokers can view client lists
    if current_user.role not in [UserRole.ADMIN, UserRole.DEVELOPER, UserRole.BROKER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view client lists"
        )
    
    try:
        return UserController.get_users_paginated(
            db=db,
            role_filter=UserRole.CLIENT,
            limit=limit,
            offset=offset,
            search=search
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{client_id}",
            response_model=UserResponse,
            summary="Get client by ID",
            description="Retrieve a specific client by their ID")
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific client by ID"""
    # Users can view their own profile, others need appropriate permissions
    if current_user.id != client_id and current_user.role not in [
        UserRole.ADMIN, UserRole.DEVELOPER, UserRole.BROKER, UserRole.AGENT
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this client"
        )
    
    client = UserController.get_user(db, client_id)
    if not client or client.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.put("/{client_id}",
            response_model=UserResponse,
            summary="Update client information",
            description="Update a client's profile information")
async def update_client(
    client_id: int,
    client_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update client information"""
    # Users can update their own profile, others need admin permissions
    if current_user.id != client_id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this client"
        )
    
    try:
        return UserController.update_user(
            db=db,
            user_id=client_id,
            user_data=client_data.dict(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{client_id}",
               response_model=dict,
               summary="Archive client",
               description="Soft delete (archive) a client account")
async def archive_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive (soft delete) a client"""
    # Only admins can archive clients
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive clients"
        )
    
    try:
        return UserController.archive_user(db, client_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

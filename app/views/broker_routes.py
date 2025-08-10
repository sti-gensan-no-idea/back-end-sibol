"""
Broker routes for broker and team management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.database import get_db
from app.controllers.user_controller import UserController
from app.controllers.property_controller import PropertyController
from app.models.user import User, UserRole
from app.services.auth_service import get_current_user
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, 
    UserAnalyticsResponse, TeamResponse, TeamMemberResponse
)
from app.schemas.property import PropertyAssignmentCreate, PropertyListResponse

router = APIRouter(prefix="/brokers", tags=["Brokers"])


@router.post("/",
             response_model=UserResponse,
             summary="Create broker account",
             description="Register a new broker account")
async def create_broker(
    broker_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new broker account"""
    # Only admins can create broker accounts
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create broker accounts"
        )
    
    # Force role to BROKER
    broker_data.role = UserRole.BROKER
    
    try:
        broker = await UserController.create_user(
            db=db,
            email=broker_data.email,
            password=broker_data.password,
            role=UserRole.BROKER,
            user_data=broker_data.dict(exclude={"password", "role"})
        )
        return broker
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/",
            response_model=UserListResponse,
            summary="Get paginated list of brokers",
            description="Retrieve all brokers with pagination")
async def get_brokers(
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of brokers"""
    # Only admins and developers can view broker lists
    if current_user.role not in [UserRole.ADMIN, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view broker lists"
        )
    
    try:
        return UserController.get_users_paginated(
            db=db,
            role_filter=UserRole.BROKER,
            limit=limit,
            offset=offset,
            search=search
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{broker_id}",
            response_model=UserResponse,
            summary="Get broker by ID",
            description="Retrieve a specific broker by their ID")
async def get_broker(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific broker by ID"""
    # Users can view their own profile, others need appropriate permissions
    if current_user.id != broker_id and current_user.role not in [
        UserRole.ADMIN, UserRole.DEVELOPER
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this broker"
        )
    
    broker = UserController.get_user(db, broker_id)
    if not broker or broker.role != UserRole.BROKER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )
    
    return broker


@router.put("/{broker_id}",
            response_model=UserResponse,
            summary="Update broker information",
            description="Update a broker's profile information")
async def update_broker(
    broker_id: int,
    broker_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update broker information"""
    # Users can update their own profile, others need admin permissions
    if current_user.id != broker_id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this broker"
        )
    
    try:
        return UserController.update_user(
            db=db,
            user_id=broker_id,
            user_data=broker_data.dict(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{broker_id}",
               response_model=dict,
               summary="Archive broker",
               description="Soft delete (archive) a broker account")
async def archive_broker(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive (soft delete) a broker"""
    # Only admins can archive brokers
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive brokers"
        )
    
    try:
        return UserController.archive_user(db, broker_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Team Management Features
@router.get("/{broker_id}/team",
            response_model=TeamResponse,
            summary="Get broker's team",
            description="Get all agents under a broker's team")
async def get_broker_team(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get broker's team members"""
    # Brokers can view their own team, others need admin permissions
    if current_user.id != broker_id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this team"
        )
    
    try:
        return UserController.get_broker_team(db, broker_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{broker_id}/team/{agent_id}",
             response_model=dict,
             summary="Add agent to team",
             description="Add an agent to broker's team")
async def add_agent_to_team(
    broker_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add agent to broker's team"""
    # Only the broker themselves or admin can add agents to team
    if current_user.id != broker_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this team"
        )
    
    try:
        return UserController.add_agent_to_team(db, broker_id, agent_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Analytics and Performance
@router.get("/{broker_id}/analytics",
            response_model=UserAnalyticsResponse,
            summary="Get broker analytics",
            description="Get performance analytics for a broker and their team")
async def get_broker_analytics(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get broker analytics"""
    # Brokers can view their own analytics, others need admin permissions
    if current_user.id != broker_id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these analytics"
        )
    
    try:
        return UserController.get_user_analytics(db, broker_id, UserRole.BROKER)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Property Management
@router.get("/{broker_id}/properties",
            response_model=PropertyListResponse,
            summary="Get broker's assigned properties",
            description="Get all properties assigned to a broker")
async def get_broker_properties(
    broker_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get broker's assigned properties"""
    # Brokers can view their own properties, others need admin permissions
    if current_user.id != broker_id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these properties"
        )
    
    try:
        return PropertyController.get_properties_by_assignee(
            db=db,
            user_id=broker_id,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{broker_id}/verify",
             response_model=dict,
             summary="Verify broker account",
             description="Office verification for broker account")
async def verify_broker(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify broker account (office verification)"""
    # Only admins can verify broker accounts
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can verify broker accounts"
        )
    
    try:
        return UserController.verify_account(db, broker_id, "office")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

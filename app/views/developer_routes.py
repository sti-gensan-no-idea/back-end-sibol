"""
Developer routes for developer management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.database import get_db
from app.controllers.user_controller import UserController
from app.controllers.property_controller import PropertyController
from app.models.user import User, UserRole
from app.services.auth_service import get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, UserAnalyticsResponse
from app.schemas.property import PropertyCreate, PropertyBulkCreate, PropertyResponse, PropertyListResponse, PropertyAssignmentCreate

router = APIRouter(prefix="/developers", tags=["Developers"])


@router.post("/",
             response_model=UserResponse,
             summary="Create developer account",
             description="Register a new developer account")
async def create_developer(
    developer_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new developer account"""
    # Only admins can create developer accounts
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create developer accounts"
        )
    
    # Force role to DEVELOPER
    developer_data.role = UserRole.DEVELOPER
    
    try:
        developer = await UserController.create_user(
            db=db,
            email=developer_data.email,
            password=developer_data.password,
            role=UserRole.DEVELOPER,
            user_data=developer_data.dict(exclude={"password", "role"})
        )
        return developer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/",
            response_model=UserListResponse,
            summary="Get paginated list of developers",
            description="Retrieve all developers with pagination")
async def get_developers(
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of developers"""
    # Only admins and brokers can view developer lists
    if current_user.role not in [UserRole.ADMIN, UserRole.BROKER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view developer lists"
        )
    
    try:
        return UserController.get_users_paginated(
            db=db,
            role_filter=UserRole.DEVELOPER,
            limit=limit,
            offset=offset,
            search=search
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{developer_id}",
            response_model=UserResponse,
            summary="Get developer by ID",
            description="Retrieve a specific developer by their ID")
async def get_developer(
    developer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific developer by ID"""
    # Users can view their own profile, others need appropriate permissions
    if current_user.id != developer_id and current_user.role not in [
        UserRole.ADMIN, UserRole.BROKER
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this developer"
        )
    
    developer = UserController.get_user(db, developer_id)
    if not developer or developer.role != UserRole.DEVELOPER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found"
        )
    
    return developer


@router.put("/{developer_id}",
            response_model=UserResponse,
            summary="Update developer information",
            description="Update a developer's profile information")
async def update_developer(
    developer_id: int,
    developer_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update developer information"""
    # Users can update their own profile, others need admin permissions
    if current_user.id != developer_id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this developer"
        )
    
    try:
        return UserController.update_user(
            db=db,
            user_id=developer_id,
            user_data=developer_data.dict(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{developer_id}",
               response_model=dict,
               summary="Archive developer",
               description="Soft delete (archive) a developer account")
async def archive_developer(
    developer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive (soft delete) a developer"""
    # Only admins can archive developers
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive developers"
        )
    
    try:
        return UserController.archive_user(db, developer_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{developer_id}/analytics",
            response_model=UserAnalyticsResponse,
            summary="Get developer analytics",
            description="Get performance analytics for a developer")
async def get_developer_analytics(
    developer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get developer analytics"""
    # Users can view their own analytics, others need admin permissions
    if current_user.id != developer_id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these analytics"
        )
    
    try:
        return UserController.get_user_analytics(db, developer_id, UserRole.DEVELOPER)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{developer_id}/properties",
            response_model=PropertyListResponse,
            summary="Get developer's properties",
            description="Get all properties owned by a developer")
async def get_developer_properties(
    developer_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get developer's properties"""
    # Users can view their own properties, others need appropriate permissions
    if current_user.id != developer_id and current_user.role not in [
        UserRole.ADMIN, UserRole.BROKER, UserRole.AGENT
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these properties"
        )
    
    try:
        return PropertyController.get_properties_by_developer(
            db=db,
            developer_id=developer_id,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{developer_id}/properties",
             response_model=PropertyResponse,
             summary="Add property to developer",
             description="Add a new property for a developer")
async def add_developer_property(
    developer_id: int,
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add property for developer"""
    # Only the developer themselves or admin can add properties
    if current_user.id != developer_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add properties for this developer"
        )
    
    try:
        return await PropertyController.create_property(
            db=db,
            property_data=property_data,
            developer_id=developer_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{developer_id}/properties/bulk",
             response_model=List[PropertyResponse],
             summary="Bulk add properties via CSV",
             description="Bulk upload properties for a developer via CSV")
async def bulk_add_properties(
    developer_id: int,
    csv_file: UploadFile = File(...),
    project_name: str = Query(..., description="Project name for all properties"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk add properties via CSV upload"""
    # Only the developer themselves or admin can bulk add properties
    if current_user.id != developer_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add properties for this developer"
        )
    
    try:
        return await PropertyController.bulk_create_properties(
            db=db,
            csv_file=csv_file,
            developer_id=developer_id,
            project_name=project_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{developer_id}/properties/{property_id}/assign",
             response_model=dict,
             summary="Assign property to broker",
             description="Assign a property to a broker or agent")
async def assign_property_to_broker(
    developer_id: int,
    property_id: int,
    assignment_data: PropertyAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign property to broker or agent"""
    # Only the developer themselves or admin can assign properties
    if current_user.id != developer_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign properties for this developer"
        )
    
    try:
        return await PropertyController.assign_property(
            db=db,
            property_id=property_id,
            user_id=assignment_data.user_id,
            assigned_by=current_user.id,
            assignment_data=assignment_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{developer_id}/verify",
             response_model=dict,
             summary="Verify developer account",
             description="Office verification for developer account")
async def verify_developer(
    developer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify developer account (office verification)"""
    # Only admins can verify developer accounts
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can verify developer accounts"
        )
    
    try:
        return UserController.verify_account(db, developer_id, "office")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

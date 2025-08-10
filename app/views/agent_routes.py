"""
Agent routes for agent management and CRM features
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.database import get_db
from app.controllers.user_controller import UserController
from app.controllers.crm_controller import CRMController
from app.models.user import User, UserRole
from app.services.auth_service import get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, UserAnalyticsResponse
from app.schemas.crm import (
    LeadCreate, LeadUpdate, LeadResponse, LeadListResponse, 
    SiteVisitCreate, SiteVisitUpdate, SiteVisitResponse, SiteVisitListResponse,
    CRMAnalyticsResponse, PipelineStatusUpdate
)

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/",
             response_model=UserResponse,
             summary="Create agent account",
             description="Register a new agent account")
async def create_agent(
    agent_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new agent account (no verification required)"""
    # Force role to AGENT
    agent_data.role = UserRole.AGENT
    
    try:
        agent = await UserController.create_user(
            db=db,
            email=agent_data.email,
            password=agent_data.password,
            role=UserRole.AGENT,
            user_data=agent_data.dict(exclude={"password", "role"})
        )
        return agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/",
            response_model=UserListResponse,
            summary="Get paginated list of agents",
            description="Retrieve all agents with pagination")
async def get_agents(
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    broker_id: Optional[int] = Query(None, description="Filter by broker ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of agents"""
    # Brokers can view their own agents, others need admin permissions
    if current_user.role == UserRole.BROKER:
        broker_id = current_user.id  # Override to show only their agents
    elif current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view agent lists"
        )
    
    try:
        return UserController.get_agents_paginated(
            db=db,
            limit=limit,
            offset=offset,
            search=search,
            broker_id=broker_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{agent_id}",
            response_model=UserResponse,
            summary="Get agent by ID",
            description="Retrieve a specific agent by their ID")
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific agent by ID"""
    agent = UserController.get_user(db, agent_id)
    if not agent or agent.role != UserRole.AGENT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Users can view their own profile, brokers can view their agents, admins can view all
    if current_user.id != agent_id:
        if current_user.role == UserRole.BROKER and agent.broker_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this agent"
            )
        elif current_user.role not in [UserRole.ADMIN, UserRole.BROKER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this agent"
            )
    
    return agent


@router.put("/{agent_id}",
            response_model=UserResponse,
            summary="Update agent information",
            description="Update an agent's profile information")
async def update_agent(
    agent_id: int,
    agent_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update agent information"""
    # Users can update their own profile, others need appropriate permissions
    if current_user.id != agent_id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this agent"
        )
    
    try:
        return UserController.update_user(
            db=db,
            user_id=agent_id,
            user_data=agent_data.dict(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{agent_id}",
               response_model=dict,
               summary="Archive agent",
               description="Soft delete (archive) an agent account")
async def archive_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive (soft delete) an agent"""
    # Only admins and brokers can archive agents
    if current_user.role not in [UserRole.ADMIN, UserRole.BROKER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive agents"
        )
    
    # Brokers can only archive their own agents
    if current_user.role == UserRole.BROKER:
        agent = UserController.get_user(db, agent_id)
        if not agent or agent.broker_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to archive this agent"
            )
    
    try:
        return UserController.archive_user(db, agent_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# CRM Pipeline Management
@router.get("/{agent_id}/leads",
            response_model=LeadListResponse,
            summary="Get agent's leads",
            description="Get all leads assigned to an agent with CRM pipeline status")
async def get_agent_leads(
    agent_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Filter by lead status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get agent's leads in CRM pipeline"""
    # Agents can view their own leads, brokers can view their agents' leads, admins can view all
    if current_user.id != agent_id:
        if current_user.role == UserRole.BROKER:
            agent = UserController.get_user(db, agent_id)
            if not agent or agent.broker_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this agent's leads"
                )
        elif current_user.role not in [UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these leads"
            )
    
    try:
        return CRMController.get_agent_leads(
            db=db,
            agent_id=agent_id,
            limit=limit,
            offset=offset,
            status_filter=status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Analytics and Performance
@router.get("/{agent_id}/analytics",
            response_model=CRMAnalyticsResponse,
            summary="Get agent CRM analytics",
            description="Get performance analytics for an agent's CRM activities")
async def get_agent_analytics(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get agent CRM analytics"""
    # Agents can view their own analytics, brokers can view their agents' analytics
    if current_user.id != agent_id:
        if current_user.role == UserRole.BROKER:
            agent = UserController.get_user(db, agent_id)
            if not agent or agent.broker_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this agent's analytics"
                )
        elif current_user.role not in [UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these analytics"
            )
    
    try:
        return CRMController.get_agent_analytics(db, agent_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

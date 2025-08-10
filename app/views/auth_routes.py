"""
Authentication routes for different user types
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.user_controller import UserController
from app.schemas.auth import (
    ClientSignIn, DeveloperSignIn, AgentSignIn, BrokerSignIn, AdminSignIn,
    SignInResponse
)
from app.models.user import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signin", 
             response_model=SignInResponse,
             summary="Generic user sign-in",
             description="General sign-in endpoint for any user type")
async def signin(
    credentials: ClientSignIn,
    db: Session = Depends(get_db)
):
    """Generic sign-in for any user type"""
    try:
        result = UserController.authenticate_user(db, credentials.email, credentials.password)
        return SignInResponse(
            user=result["user"],
            token=result["token"],
            message="Sign-in successful"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/client/signin",
             response_model=SignInResponse,
             summary="Client sign-in",
             description="Sign-in endpoint specifically for clients")
async def client_signin(
    credentials: ClientSignIn,
    db: Session = Depends(get_db)
):
    """Client-specific sign-in"""
    try:
        result = UserController.authenticate_user(
            db, credentials.email, credentials.password, required_role=UserRole.CLIENT
        )
        return SignInResponse(
            user=result["user"],
            token=result["token"],
            message="Client sign-in successful"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials"
        )


@router.post("/developer/signin",
             response_model=SignInResponse,
             summary="Developer sign-in",
             description="Sign-in endpoint specifically for developers")
async def developer_signin(
    credentials: DeveloperSignIn,
    db: Session = Depends(get_db)
):
    """Developer-specific sign-in"""
    try:
        result = UserController.authenticate_user(
            db, credentials.email, credentials.password, required_role=UserRole.DEVELOPER
        )
        
        # Check if developer is verified
        if not result["user"]["office_verified"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Developer account requires office verification"
            )
            
        return SignInResponse(
            user=result["user"],
            token=result["token"],
            message="Developer sign-in successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid developer credentials"
        )


@router.post("/agent/signin",
             response_model=SignInResponse,
             summary="Agent sign-in",
             description="Sign-in endpoint specifically for agents")
async def agent_signin(
    credentials: AgentSignIn,
    db: Session = Depends(get_db)
):
    """Agent-specific sign-in"""
    try:
        result = UserController.authenticate_user(
            db, credentials.email, credentials.password, required_role=UserRole.AGENT
        )
        
        # Check if agent is assigned to a team
        if not result["user"]["broker_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Agent must be assigned to a team before accessing the system"
            )
            
        return SignInResponse(
            user=result["user"],
            token=result["token"],
            message="Agent sign-in successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent credentials"
        )


@router.post("/broker/signin",
             response_model=SignInResponse,
             summary="Broker sign-in",
             description="Sign-in endpoint specifically for brokers")
async def broker_signin(
    credentials: BrokerSignIn,
    db: Session = Depends(get_db)
):
    """Broker-specific sign-in"""
    try:
        result = UserController.authenticate_user(
            db, credentials.email, credentials.password, required_role=UserRole.BROKER
        )
        
        # Check if broker is verified
        if not result["user"]["office_verified"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Broker account requires office verification"
            )
            
        return SignInResponse(
            user=result["user"],
            token=result["token"],
            message="Broker sign-in successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid broker credentials"
        )


@router.post("/admin/signin",
             response_model=SignInResponse,
             summary="Admin sign-in",
             description="Sign-in endpoint specifically for admins")
async def admin_signin(
    credentials: AdminSignIn,
    db: Session = Depends(get_db)
):
    """Admin-specific sign-in"""
    try:
        result = UserController.authenticate_user(
            db, credentials.email, credentials.password, required_role=UserRole.ADMIN
        )
        return SignInResponse(
            user=result["user"],
            token=result["token"],
            message="Admin sign-in successful"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )

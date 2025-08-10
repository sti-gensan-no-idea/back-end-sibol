"""
Authentication schemas for different user types
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class BaseUserSignIn(BaseModel):
    """Base sign-in schema"""
    email: EmailStr
    password: str


class ClientSignIn(BaseUserSignIn):
    """Client sign-in schema"""
    pass


class DeveloperSignIn(BaseUserSignIn):
    """Developer sign-in schema"""
    pass


class AgentSignIn(BaseUserSignIn):
    """Agent sign-in schema"""
    pass


class BrokerSignIn(BaseUserSignIn):
    """Broker sign-in schema"""
    pass


class AdminSignIn(BaseUserSignIn):
    """Admin sign-in schema"""
    pass


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: UserRole
    expires_in: int


class SignInResponse(BaseModel):
    """Sign-in response schema"""
    user: dict
    token: TokenResponse
    message: str = "Sign-in successful"

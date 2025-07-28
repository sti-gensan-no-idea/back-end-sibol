from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

    @validator('role')
    def validate_role(cls, v):
        valid_roles = ["ADMIN", "SUB_ADMIN", "AGENT", "CLIENT"]
        if not isinstance(v, str):
            raise ValueError("Role must be a string")
        if v.upper() not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

    @validator('role', allow_reuse=True)
    def validate_role(cls, v):
        if v is None:
            return v
        valid_roles = ["ADMIN", "SUB_ADMIN", "AGENT", "CLIENT"]
        if not isinstance(v, str):
            raise ValueError("Role must be a string")
        if v.upper() not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True
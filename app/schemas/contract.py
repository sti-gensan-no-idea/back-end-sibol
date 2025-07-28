# app/schemas/contract.py
from pydantic import BaseModel
from typing import Optional

class ContractBase(BaseModel):
    property_id: int
    tenant_id: int
    content: str

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    property_id: Optional[int] = None
    tenant_id: Optional[int] = None
    content: Optional[str] = None
    status: Optional[str] = None

class ContractResponse(ContractBase):
    id: int
    status: str

    class Config:
        from_attributes = True

class ContractAnalysisResponse(BaseModel):
    contract_id: int
    analysis: str
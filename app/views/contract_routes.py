# app/views/contract_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.contract_controller import ContractController
from app.services.auth_service import get_current_user
from app.models.user import User
from app.schemas.contract import ContractCreate, ContractUpdate, ContractResponse, ContractAnalysisResponse

router = APIRouter()

@router.post("/", response_model=ContractResponse, summary="Create a new contract")
async def create_contract(contract: ContractCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    return ContractController.create_contract(
        db, 
        contract.property_id, 
        contract.tenant_id, 
        contract.content,
        current_user
    )

@router.get("/{contract_id}", response_model=ContractResponse, summary="Get a contract by ID")
async def get_contract(contract_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    return ContractController.get_contract(db, contract_id)

@router.get("/", response_model=list[ContractResponse], summary="Get a list of contracts")
async def get_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ContractController.get_contracts(db, skip, limit)

@router.put("/{contract_id}", response_model=ContractResponse, summary="Update a contract")
async def update_contract(contract_id: int, contract: ContractUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    return ContractController.update_contract(
        db, 
        contract_id, 
        contract.property_id, 
        contract.tenant_id, 
        contract.content, 
        contract.status,
        current_user
    )

@router.delete("/{contract_id}", response_model=dict, summary="Delete a contract")
async def delete_contract(contract_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    return ContractController.delete_contract(db, contract_id, current_user)

@router.get("/{contract_id}/analyze", response_model=ContractAnalysisResponse, summary="Analyze contract with AI")
async def analyze_contract(contract_id: int, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    return await ContractController.analyze_contract(db, contract_id, current_user)
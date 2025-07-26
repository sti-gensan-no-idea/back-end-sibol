# app/controllers/contract_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.contract import Contract
from app.models.user import UserRole
from app.services.ai_service import AIService

class ContractController:
    @staticmethod
    def create_contract(db: Session, property_id: int, tenant_id: int, content: str, current_user):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        contract = Contract(
            property_id=property_id,
            tenant_id=tenant_id,
            content=content
        )
        db.add(contract)
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def get_contract(db: Session, contract_id: int):
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return contract

    @staticmethod
    def get_contracts(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Contract).offset(skip).limit(limit).all()

    @staticmethod
    def update_contract(db: Session, contract_id: int, property_id: int = None, 
                      tenant_id: int = None, content: str = None, status: str = None, current_user=None):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        if property_id:
            contract.property_id = property_id
        if tenant_id:
            contract.tenant_id = tenant_id
        if content:
            contract.content = content
        if status:
            contract.status = status
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def delete_contract(db: Session, contract_id: int, current_user):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        db.delete(contract)
        db.commit()
        return {"detail": "Contract deleted"}

    @staticmethod
    async def analyze_contract(db: Session, contract_id: int, current_user):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        ai_service = AIService()
        analysis = await ai_service.analyze_contract(contract.content)
        return {"contract_id": contract.id, "analysis": analysis}
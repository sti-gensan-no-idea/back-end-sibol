# app/controllers/contract_controller.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.simple_models import Contract, ContractStatus
from app.models.user import User

class ContractController:
    @staticmethod
    def create_contract(db: Session, contract_number: str, property_id: int, tenant_id: int, 
                       title: str, content: str, monthly_rent: float, start_date, end_date, user: User):
        """Create a new contract."""
        contract = Contract(
            contract_number=contract_number,
            property_id=property_id,
            tenant_id=tenant_id,
            title=title,
            content=content,
            monthly_rent=monthly_rent,
            start_date=start_date,
            end_date=end_date
        )
        db.add(contract)
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def get_contracts(db: Session, skip: int = 0, limit: int = 100):
        """Retrieve contracts with pagination."""
        return db.query(Contract).offset(skip).limit(limit).all()

    @staticmethod
    def get_contract(db: Session, contract_id: int):
        """Get a contract by ID."""
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return contract

    @staticmethod
    def update_contract_status(db: Session, contract_id: int, status: ContractStatus, user: User):
        """Update contract status."""
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        contract.status = status
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def delete_contract(db: Session, contract_id: int, user: User):
        """Delete a contract."""
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        db.delete(contract)
        db.commit()
        return {"message": "Contract deleted successfully"}

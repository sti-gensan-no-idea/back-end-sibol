from sqlalchemy.orm import Session
from app.models.contract import Contract
from app.models.user import User, UserRole
from app.models.property import Property
from fastapi import HTTPException
from app.config.settings import settings

class ContractController:
    @staticmethod
    def create_contract(db: Session, property_id: int, tenant_id: int, content: str, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
            raise HTTPException(status_code=403, detail="Not authorized")
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        tenant = db.query(User).filter(User.id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        contract = Contract(property_id=property_id, tenant_id=tenant_id, content=content)
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
    def get_contracts(db: Session, skip: int, limit: int):
        return db.query(Contract).offset(skip).limit(limit).all()

    @staticmethod
    def update_contract(db: Session, contract_id: int, property_id: int, tenant_id: int, 
                       content: str, status: str, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
            raise HTTPException(status_code=403, detail="Not authorized")
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        if property_id:
            property = db.query(Property).filter(Property.id == property_id).first()
            if not property:
                raise HTTPException(status_code=404, detail="Property not found")
            contract.property_id = property_id
        if tenant_id:
            tenant = db.query(User).filter(User.id == tenant_id).first()
            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")
            contract.tenant_id = tenant_id
        if content:
            contract.content = content
        if status:
            contract.status = status
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def delete_contract(db: Session, contract_id: int, current_user: User):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN, UserRole.AGENT]:
            raise HTTPException(status_code=403, detail="Not authorized")
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        db.delete(contract)
        db.commit()
        return {"message": "Contract deleted"}
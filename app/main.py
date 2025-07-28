from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.views import user_routes, property_routes, contract_routes, payment_routes, chat_routes
from app.database.database import engine, get_db
from app.models import payment, chat, user, property, contract
from app.config.settings import settings
from app.models.user import User, UserRole
from app.models.payment import Payment, Balance
from app.models.property import Property
from app.models.contract import Contract
from app.models.chat import Chatroom, Message
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_tags=[
        {"name": "Users", "description": "User management operations with role-based access"},
        {"name": "Properties", "description": "Property management with AR viewing and new fields"},
        {"name": "Contracts", "description": "Contract management operations"},
        {"name": "Payments", "description": "Payment processing with PayFusion QR Ph"},
        {"name": "Chats", "description": "Chatroom and messaging with emoji reactions"},
        {"name": "Seed", "description": "Seed dummy data for testing"}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
payment.Base.metadata.create_all(bind=engine)
chat.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)
property.Base.metadata.create_all(bind=engine)
contract.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(property_routes.router, prefix="/api/v1/properties", tags=["Properties"])
app.include_router(contract_routes.router, prefix="/api/v1/contracts", tags=["Contracts"])
app.include_router(payment_routes.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(chat_routes.router, prefix="/api/v1/chats", tags=["Chats"])

@app.get("/")
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

@app.post("/seed", summary="Seed dummy data into the database")
async def seed_data(db: Session = Depends(get_db)):
    # Clear existing data
    db.query(Message).delete()
    db.query(Chatroom).delete()
    db.query(Payment).delete()
    db.query(Balance).delete()
    db.query(Contract).delete()
    db.query(Property).delete()
    db.query(User).delete()
    db.commit()

    # Insert Users
    users = [
        User(id=1, email="admin@sibol.com", hashed_password="$2b$12$Q7z9X8Y2z3W4x5Y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4", role=UserRole.ADMIN, is_active=True),
        User(id=2, email="agent1@sibol.com", hashed_password="$2b$12$R8A9B0C1D2E3F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3", role=UserRole.ADMIN, is_active=True),]
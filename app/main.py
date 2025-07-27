# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.views import user_routes, property_routes, contract_routes
from app.database.database import engine
from app.models import user, property, contract
from app.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_tags=[
        {"name": "Users", "description": "User management operations with role-based access"},
        {"name": "Properties", "description": "Property management with AR viewing and new fields"},
        {"name": "Contracts", "description": "Contract management with AI analysis"},
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
user.Base.metadata.create_all(bind=engine)
property.Base.metadata.create_all(bind=engine)
contract.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(property_routes.router, prefix="/api/v1/properties", tags=["Properties"])
app.include_router(contract_routes.router, prefix="/api/v1/contracts", tags=["Contracts"])

@app.get("/")
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}
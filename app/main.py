"""
Atuna API - Real Estate Management System
FastAPI application with Supabase PostgreSQL integration
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.database.database import engine, get_db
from app.database.init_db import init_database
from app.views import (
    user_routes, 
    property_routes, 
    contract_routes, 
    payment_routes, 
    chat_routes
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    print("🚀 Starting Atuna API...")
    await init_database()
    print("✅ Database initialized successfully")
    
    yield
    
    print("🛑 Shutting down Atuna API...")

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Users", "description": "User management operations with role-based access"},
        {"name": "Properties", "description": "Property management with AR viewing and enhanced features"},
        {"name": "Contracts", "description": "Contract management operations"},
        {"name": "Payments", "description": "Payment processing with PayFusion QR Ph"},
        {"name": "Chats", "description": "Chatroom and messaging with emoji reactions"},
        {"name": "Analytics", "description": "Analytics and reporting endpoints"},
        {"name": "Events", "description": "Event scheduling and management"},
        {"name": "System", "description": "System health and utilities"}
    ]
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(property_routes.router, prefix="/api/v1/properties", tags=["Properties"])
app.include_router(contract_routes.router, prefix="/api/v1/contracts", tags=["Contracts"])
app.include_router(payment_routes.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(chat_routes.router, prefix="/api/v1/chats", tags=["Chats"])

# Root endpoint
@app.get("/", summary="API Root", tags=["System"])
async def read_root():
    """API root endpoint with basic information"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health", summary="Health Check", tags=["System"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity"""
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.APP_VERSION
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Seed data endpoint
@app.post("/seed", summary="Seed Database", tags=["System"])
async def seed_database(db: Session = Depends(get_db)):
    """Seed the database with sample data from SQL file"""
    try:
        with open("seed_data.sql", "r") as f:
            sql_commands = f.read()
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        for command in commands:
            if command:
                db.execute(command)
        db.commit()
        return {
            "message": "Database seeded successfully",
            "commands_executed": len(commands)
        }
    except Exception as e:
        db.rollback()
        return {
            "error": f"Failed to seed database: {str(e)}",
            "message": "Database seeding failed"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
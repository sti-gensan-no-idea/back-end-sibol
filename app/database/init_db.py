"""
Database initialization module
Handles database setup, migrations, and seeding
"""
import asyncio
import logging
from typing import Optional
from pathlib import Path

from app.database.database import (
    check_database_connection,
    create_database_tables,
    execute_sql_file,
    get_database_info
)
from app.config.settings import settings

logger = logging.getLogger(__name__)


async def init_database() -> bool:
    """
    Initialize the database with proper error handling
    """
    try:
        logger.info("🔧 Initializing database...")
        
        # Check database connection
        if not await check_database_connection():
            logger.error("❌ Database connection failed during initialization")
            return False
        
        # Create tables if they don't exist
        if not create_database_tables():
            logger.error("❌ Failed to create database tables")
            return False
        
        # Log database information
        db_info = get_database_info()
        if "error" not in db_info:
            logger.info(f"📊 Database Info: {db_info['database_name']} - {db_info['active_connections']} active connections")
        
        logger.info("✅ Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


async def seed_database_from_file(file_path: Optional[str] = None) -> bool:
    """
    Seed database from SQL file
    """
    try:
        if file_path is None:
            file_path = "seed_data.sql"
        
        if not Path(file_path).exists():
            logger.warning(f"⚠️ Seed file {file_path} not found, skipping seeding")
            return True
        
        logger.info(f"🌱 Seeding database from {file_path}...")
        
        if execute_sql_file(file_path):
            logger.info("✅ Database seeding completed successfully")
            return True
        else:
            logger.error("❌ Database seeding failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during database seeding: {e}")
        return False


async def reset_database() -> bool:
    """
    Reset database (development only)
    """
    if settings.is_production:
        logger.error("❌ Database reset not allowed in production")
        return False
    
    try:
        logger.warning("⚠️ Resetting database...")
        
        # This would typically involve dropping and recreating tables
        # For now, we'll just recreate tables
        if create_database_tables():
            logger.info("✅ Database reset completed")
            return True
        else:
            logger.error("❌ Database reset failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during database reset: {e}")
        return False


def verify_database_schema() -> dict:
    """
    Verify database schema and return status
    """
    try:
        from app.database.database import get_db_context
        from sqlalchemy import text
        
        with get_db_context() as db:
            # Check if required tables exist
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            result = db.execute(tables_query)
            existing_tables = [row[0] for row in result.fetchall()]
            
            # Expected tables based on your models
            expected_tables = [
                'users', 'balances', 'properties', 'contracts', 
                'payments', 'chatrooms', 'messages', 'transactions',
                'property_listings', 'events', 'upcoming_events',
                'agent_performances', 'property_analytics', 'automation_workflows'
            ]
            
            missing_tables = set(expected_tables) - set(existing_tables)
            extra_tables = set(existing_tables) - set(expected_tables)
            
            return {
                "status": "healthy" if not missing_tables else "incomplete",
                "existing_tables": existing_tables,
                "expected_tables": expected_tables,
                "missing_tables": list(missing_tables),
                "extra_tables": list(extra_tables),
                "total_tables": len(existing_tables)
            }
            
    except Exception as e:
        logger.error(f"Error verifying database schema: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def health_check() -> dict:
    """
    Comprehensive database health check
    """
    try:
        # Connection test
        connection_healthy = await check_database_connection()
        
        # Schema verification
        schema_info = verify_database_schema()
        
        # Database info
        db_info = get_database_info()
        
        overall_status = (
            "healthy" if connection_healthy and schema_info["status"] == "healthy"
            else "unhealthy"
        )
        
        return {
            "status": overall_status,
            "connection": "connected" if connection_healthy else "disconnected",
            "schema": schema_info,
            "database_info": db_info,
            "environment": settings.ENVIRONMENT
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

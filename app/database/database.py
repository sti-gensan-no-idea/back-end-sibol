"""
Database configuration and session management for Supabase PostgreSQL
Enhanced with connection pooling, error handling, and monitoring
"""
from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging
import time

from app.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL configuration
DATABASE_URL = settings.database_url

# Enhanced engine configuration for Supabase
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
    connect_args={
        "sslmode": "require",
        "options": "-c timezone=UTC",
        "connect_timeout": 10,
        "command_timeout": 30,
    },
    echo=settings.DEBUG,
    echo_pool=settings.DEBUG,
    future=True
)

# Session configuration
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# Base class for models
Base = declarative_base()

# Connection monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Log database connections"""
    logger.info("New database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkouts"""
    connection_record.info['checkout_time'] = time.time()

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkins with duration"""
    checkout_time = connection_record.info.get('checkout_time')
    if checkout_time:
        duration = time.time() - checkout_time
        logger.debug(f"Connection checked in after {duration:.2f} seconds")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session with enhanced error handling
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error in context: {e}")
        raise
    finally:
        db.close()


async def check_database_connection() -> bool:
    """
    Async function to check database connectivity
    """
    try:
        with get_db_context() as db:
            result = db.execute(text("SELECT version()")).scalar()
            logger.info(f"✅ Database connection successful - {result}")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def test_database_connection() -> bool:
    """
    Synchronous function to test database connectivity
    """
    try:
        with get_db_context() as db:
            result = db.execute(text("SELECT 1")).scalar()
            return result == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def create_database_tables() -> bool:
    """
    Create all database tables with error handling
    """
    try:
        # Import all models to ensure they're registered with Base
        from app.models import (
            user, property, contract, payment, chat
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        return False


def drop_all_tables() -> bool:
    """
    Drop all database tables (use with caution!)
    """
    if settings.is_production:
        logger.error("❌ Cannot drop tables in production environment")
        return False
        
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("⚠️ All database tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Error dropping database tables: {e}")
        return False


def get_database_info() -> dict:
    """
    Get database connection information
    """
    try:
        with get_db_context() as db:
            # Get database version
            version_result = db.execute(text("SELECT version()")).scalar()
            
            # Get current database name
            db_name_result = db.execute(text("SELECT current_database()")).scalar()
            
            # Get connection count
            conn_count_result = db.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            ).scalar()
            
            return {
                "version": version_result,
                "database_name": db_name_result,
                "active_connections": conn_count_result,
                "pool_size": engine.pool.size(),
                "checked_out_connections": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"error": str(e)}


def execute_sql_file(file_path: str) -> bool:
    """
    Execute SQL commands from a file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by semicolon and execute each command
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        with get_db_context() as db:
            for command in commands:
                if command and not command.startswith('--'):
                    db.execute(text(command))
        
        logger.info(f"✅ Successfully executed {len(commands)} SQL commands from {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error executing SQL file {file_path}: {e}")
        return False

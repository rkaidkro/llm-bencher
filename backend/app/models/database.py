"""
Database configuration and session management.

This module provides the database engine, session factory, and base model
for llm-bencher.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from ..utils.config import get_database_url

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine
def create_database_engine():
    """Create and configure the database engine."""
    database_url = get_database_url()
    
    # Configure engine based on database type
    if database_url.startswith("sqlite"):
        # SQLite configuration for development
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False  # Set to True for SQL query logging
        )
        logger.info("Using SQLite database engine")
    else:
        # PostgreSQL configuration for production
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        logger.info("Using PostgreSQL database engine")
    
    return engine


# Create engine instance
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: Database session instance
        
    Example:
        ```python
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize the database by creating all tables."""
    try:
        # Import all models to ensure they are registered
        from . import schemas  # noqa: F401
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def close_db():
    """Close the database engine."""
    try:
        engine.dispose()
        logger.info("Database engine closed successfully")
    except Exception as e:
        logger.error(f"Failed to close database engine: {e}")
        raise

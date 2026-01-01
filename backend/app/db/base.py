"""
Database Usage and Connection
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config import settings
import os

# Create engine
# If DATABASE_URL is not set (local dev without DB), use SQLite fallback
DATABASE_URL = settings.database_url or "sqlite:///./quant.db"

# Handle special case for Railway/Postgres URL that might start with postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,
    # Additional pool settings for production could go here
    # pool_size=5,
    # max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

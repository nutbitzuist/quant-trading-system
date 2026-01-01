"""
Initialize Database
Creates tables and initial superuser
"""

from sqlalchemy.orm import Session
from app.db.base import engine, Base, SessionLocal
from app.db.models import User
from app.core.auth import get_password_hash

def init_db(db: Session) -> None:
    """Create tables and initial user."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if admin exists
    user = db.query(User).filter(User.email == "admin@quant.local").first()
    if not user:
        user = User(
            email="admin@quant.local",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Superuser created: admin@quant.local")
    else:
        print("Superuser already exists.")

def main():
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating database tables...")
    main()
    print("Database initialization complete.")

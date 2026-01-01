"""
Authentication API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash, 
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.db.base import get_db
from app.db.models import User

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = None


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str = None
    is_active: bool
    is_superuser: bool


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    Returns access token.
    """
    user = await authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register new user.
    """
    # Check if user exists
    db_user = db.query(User).filter(User.email == request.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    new_user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user info.
    """
    return current_user

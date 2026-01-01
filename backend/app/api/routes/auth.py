"""
Authentication API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.auth import AuthService, User, Token

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool


async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """Dependency to get current authenticated user."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = parts[1]
    user = AuthService.get_current_user(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user


@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """
    Login with email and password.
    
    Returns access token.
    """
    user = AuthService.authenticate(request.email, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = AuthService.create_token(user)
    
    return Token(
        access_token=token.access_token,
        expires_in=token.expires_in
    )


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """
    Register new user.
    """
    # Check if user exists
    if request.email in AuthService._users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = AuthService.create_user(request.email, request.password)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """
    Get current user info.
    """
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active
    )


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout (invalidate token).
    """
    if authorization:
        parts = authorization.split()
        if len(parts) == 2:
            token = parts[1]
            if token in AuthService._tokens:
                del AuthService._tokens[token]
    
    return {"message": "Logged out successfully"}

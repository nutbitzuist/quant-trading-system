"""
Authentication module
Simple JWT-based authentication
"""

from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import secrets


@dataclass
class User:
    """User model."""
    id: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: str = ""


@dataclass
class Token:
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class AuthService:
    """
    Simple authentication service.
    
    For production, use proper JWT library and database.
    """
    
    SECRET_KEY = "your-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    
    # In-memory user store (replace with database)
    _users: dict = {}
    _tokens: dict = {}
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password."""
        return hashlib.sha256((password + cls.SECRET_KEY).encode()).hexdigest()
    
    @classmethod
    def verify_password(cls, password: str, hashed: str) -> bool:
        """Verify password."""
        return cls.hash_password(password) == hashed
    
    @classmethod
    def create_user(cls, email: str, password: str) -> User:
        """Create new user."""
        user_id = secrets.token_hex(16)
        user = User(
            id=user_id,
            email=email,
            hashed_password=cls.hash_password(password),
            created_at=datetime.now().isoformat()
        )
        cls._users[email] = user
        return user
    
    @classmethod
    def authenticate(cls, email: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = cls._users.get(email)
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        return user
    
    @classmethod
    def create_token(cls, user: User) -> Token:
        """Create access token."""
        token = secrets.token_hex(32)
        expires = datetime.now() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        cls._tokens[token] = {
            "user_id": user.id,
            "email": user.email,
            "expires": expires.isoformat()
        }
        
        return Token(
            access_token=token,
            expires_in=cls.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @classmethod
    def verify_token(cls, token: str) -> Optional[dict]:
        """Verify access token."""
        token_data = cls._tokens.get(token)
        if not token_data:
            return None
        
        expires = datetime.fromisoformat(token_data["expires"])
        if datetime.now() > expires:
            del cls._tokens[token]
            return None
        
        return token_data
    
    @classmethod
    def get_current_user(cls, token: str) -> Optional[User]:
        """Get current user from token."""
        token_data = cls.verify_token(token)
        if not token_data:
            return None
        
        return cls._users.get(token_data["email"])


# Create a default admin user
def init_default_users():
    """Initialize default users."""
    if "admin@quant.local" not in AuthService._users:
        AuthService.create_user("admin@quant.local", "admin123")


init_default_users()

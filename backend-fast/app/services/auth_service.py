import logging
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate
from typing import Optional

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=UserRole(user_data.role)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user_preferences(db: Session, user: User, preferences: dict) -> User:
        """Update user preferences"""
        current_preferences = user.preferences or {}
        current_preferences.update(preferences)
        user.preferences = current_preferences
        db.commit()
        db.refresh(user)
        return user

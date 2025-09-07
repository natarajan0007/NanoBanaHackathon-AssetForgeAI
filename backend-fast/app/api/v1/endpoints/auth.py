import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_refresh_token
)
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    PasswordResetRequest, 
    UserPreferencesUpdate, 
    UserResponse,
    RefreshTokenRequest,
    RefreshTokenResponse
)
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """User login endpoint. Returns both access and refresh tokens."""
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    token_data={"sub": user.username, "role": user.role.value}

    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return LoginResponse(
        accessToken=access_token,
        refreshToken=refresh_token
    )

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh an expired access token."""
    username = verify_refresh_token(request.refreshToken)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    new_access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    return RefreshTokenResponse(accessToken=new_access_token)


@router.post("/logout", status_code=204)
async def logout(current_user: User = Depends(get_current_user)):
    """User logout endpoint - JWT is stateless, so this is mainly for client-side cleanup."""
    return None


@router.post("/password-reset-request", status_code=202)
async def password_reset_request(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset - sends reset email."""
    user = db.query(User).filter(User.email == reset_data.email).first()
    if user:
        print(f"Password reset requested for user: {user.username}")
    return {"message": "If the email exists, a reset link has been sent"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        preferences=current_user.preferences or {}
    )


@router.put("/me/preferences", response_model=UserResponse)
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences."""
    current_preferences = current_user.preferences or {}
    
    if preferences_update.theme is not None:
        current_preferences["theme"] = preferences_update.theme
    
    current_user.preferences = current_preferences
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        preferences=current_user.preferences or {}
    )
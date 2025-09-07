import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# ... (rest of the imports)

logger = logging.getLogger(__name__)
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.schemas.auth import UserResponse
from app.schemas.admin import ManualEditingRule
from app.api.dependencies import get_current_user, get_admin_user
from app.services.admin_service import AdminService
from typing import List

router = APIRouter()


@router.get("/me/preferences", response_model=UserResponse)
async def get_user_preferences(current_user: User = Depends(get_current_user)):
    """Get current user preferences - alternative endpoint for UI compatibility"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        preferences=current_user.preferences or {}
    )


@router.get("/me/editing-rules", response_model=ManualEditingRule)
async def get_my_editing_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the manual editing rules applicable to the current user's organization."""
    return AdminService.get_manual_editing_rules(db, current_user)


@router.put("/me/preferences", response_model=UserResponse)
async def update_user_preferences_alt(
    preferences_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences - alternative endpoint for UI compatibility"""
    # Update preferences
    current_preferences = current_user.preferences or {}
    current_preferences.update(preferences_update)
    
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


@router.post("/", response_model=UserSchema)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Create a new user (admin only)"""
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    organization_id = admin_user.organization_id
    if user_data.organizationName:
        # If organization name is provided, create a new one
        new_organization = Organization(name=user_data.organizationName)
        db.add(new_organization)
        db.flush() # To get the new organization's ID
        organization_id = new_organization.id

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=UserRole(user_data.role),
        organization_id=organization_id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/", response_model=List[UserSchema])
async def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """List all users (admin only)"""
    users = db.query(User).filter(User.organization_id == admin_user.organization_id).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get user by ID (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.preferences is not None:
        user.preferences = user_update.preferences
    
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/deactivate", status_code=204)
async def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Deactivate a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    return None

@router.put("/{user_id}/activate", status_code=204)
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Activate a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    return None


@router.post("/register", response_model=UserSchema)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """User self-registration"""
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create or get the organization
    if user_data.organizationName:
        organization = Organization(name=user_data.organizationName)
        db.add(organization)
        db.flush()
    else:
        organization = db.query(Organization).filter(Organization.name == "Default Organization").first()
        if not organization:
            organization = Organization(name="Default Organization")
            db.add(organization)
            db.flush()

    # Create new user with default 'user' role
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=UserRole.USER,  # Default role
        organization_id=organization.id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.admin import (
    AIBehaviorRule,
    AdaptationRule,
    UploadModerationRule,
    TextStyleSetResponse
)
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/rules/ai-behavior", response_model=AIBehaviorRule)
async def get_user_ai_behavior_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the AI Behavior Controls applicable to the current user's organization."""
    return AdminService.get_ai_behavior_rules(db, current_user)


@router.get("/rules/adaptation", response_model=AdaptationRule)
async def get_user_adaptation_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the Image Template Rules and Adaptation Settings for the current user's organization."""
    return AdminService.get_adaptation_rules(db, current_user)


@router.get("/rules/upload-moderation", response_model=UploadModerationRule)
async def get_user_upload_moderation_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the Content Moderation and Upload Rules for the current user's organization."""
    return AdminService.get_upload_moderation_rules(db, current_user)


@router.get("/text-style-sets", response_model=List[TextStyleSetResponse])
async def get_user_text_style_sets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the Text Style Sets for the current user's organization."""
    style_sets = AdminService.get_text_style_sets(db, current_user)
    return [
        TextStyleSetResponse(
            id=str(style_set.id),
            name=style_set.name,
            styles=style_set.styles,
            is_active=style_set.is_active
        )
        for style_set in style_sets
    ]

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.dependencies import get_admin_user
from app.models.user import User
from app.models.project import Project
from app.models.generated_asset import GeneratedAsset
from app.models.generation_job import GenerationJob
from app.schemas.admin import (
    PlatformCreate, PlatformUpdate, PlatformResponse,
    AssetFormatCreate, AssetFormatUpdate, AssetFormatResponse,
    TextStyleSetCreate, TextStyleSetUpdate, TextStyleSetResponse,
    AdaptationRule, AIBehaviorRule, UploadModerationRule, ManualEditingRule
)
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get statistics for the admin dashboard"""
    total_users = db.query(User).filter(User.organization_id == admin_user.organization_id).count()
    total_projects = db.query(Project).filter(Project.organization_id == admin_user.organization_id).count()
    total_generated_assets = db.query(GeneratedAsset).join(GenerationJob).join(Project).filter(Project.organization_id == admin_user.organization_id).count()

    return {
        "totalUsers": total_users,
        "totalProjects": total_projects,
        "totalGeneratedAssets": total_generated_assets,
        "activeWorkers": 4 # Mock data for now
    }


# Platform Management
@router.get("/platforms", response_model=List[PlatformResponse])
async def list_platforms(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """List all repurposing platforms for the admin's organization"""
    platforms = AdminService.get_platforms(db, admin_user)
    return [
        PlatformResponse(
            id=str(platform.id),
            name=platform.name,
            is_active=platform.is_active,
            created_at=platform.created_at.isoformat()
        )
        for platform in platforms
    ]


@router.post("/platforms", response_model=PlatformResponse)
async def create_platform(
    platform_data: PlatformCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Add a new repurposing platform"""
    try:
        platform = AdminService.create_platform(db, platform_data, admin_user)
        return PlatformResponse(
            id=str(platform.id),
            name=platform.name,
            is_active=platform.is_active,
            created_at=platform.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating platform: {str(e)}"
        )


@router.put("/platforms/{platform_id}", response_model=PlatformResponse)
async def update_platform(
    platform_id: str,
    platform_data: PlatformUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update a platform's name"""
    platform = AdminService.get_platform_by_id(db, platform_id, admin_user)
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found"
        )
    
    try:
        updated_platform = AdminService.update_platform(db, platform, platform_data.name)
        return PlatformResponse(
            id=str(updated_platform.id),
            name=updated_platform.name,
            is_active=updated_platform.is_active,
            created_at=updated_platform.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating platform: {str(e)}"
        )


@router.delete("/platforms/{platform_id}", status_code=204)
async def delete_platform(
    platform_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete a platform"""
    platform = AdminService.get_platform_by_id(db, platform_id, admin_user)
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found"
        )
    
    try:
        AdminService.delete_platform(db, platform)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting platform: {str(e)}"
        )


# Format Management
@router.get("/formats", response_model=List[AssetFormatResponse])
async def list_formats(
    type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """List all asset formats for the admin's organization"""
    formats = AdminService.get_formats(db, admin_user, type, category)
    return [
        AssetFormatResponse(
            id=str(format_obj.id),
            name=format_obj.name,
            type=format_obj.type.value,
            platformId=str(format_obj.platform_id) if format_obj.platform_id else None,
            category=format_obj.category,
            width=format_obj.width,
            height=format_obj.height,
            is_active=format_obj.is_active
        )
        for format_obj in formats
    ]


@router.post("/formats", response_model=AssetFormatResponse)
async def create_format(
    format_data: AssetFormatCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Create a new asset format"""
    try:
        asset_format = AdminService.create_format(db, format_data, admin_user)
        return AssetFormatResponse(
            id=str(asset_format.id),
            name=asset_format.name,
            type=asset_format.type.value,
            platformId=str(asset_format.platform_id) if asset_format.platform_id else None,
            category=asset_format.category,
            width=asset_format.width,
            height=asset_format.height,
            is_active=asset_format.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating format: {str(e)}"
        )


@router.put("/formats/{format_id}", response_model=AssetFormatResponse)
async def update_format(
    format_id: str,
    format_data: AssetFormatUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update an asset format"""
    asset_format = AdminService.get_format_by_id(db, format_id, admin_user)
    if not asset_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Format not found"
        )
    
    try:
        update_data = format_data.dict(exclude_unset=True)
        updated_format = AdminService.update_format(db, asset_format, update_data)
        return AssetFormatResponse(
            id=str(updated_format.id),
            name=updated_format.name,
            type=updated_format.type.value,
            platformId=str(updated_format.platform_id) if updated_format.platform_id else None,
            category=updated_format.category,
            width=updated_format.width,
            height=updated_format.height,
            is_active=updated_format.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating format: {str(e)}"
        )


@router.delete("/formats/{format_id}", status_code=204)
async def delete_format(
    format_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete an asset format"""
    asset_format = AdminService.get_format_by_id(db, format_id, admin_user)
    if not asset_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Format not found"
        )
    
    try:
        AdminService.delete_format(db, asset_format)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting format: {str(e)}"
        )


# Text Style Set Management
@router.get("/text-style-sets", response_model=List[TextStyleSetResponse])
async def list_text_style_sets(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """List all text style sets for the admin's organization"""
    style_sets = AdminService.get_text_style_sets(db, admin_user)
    return [
        TextStyleSetResponse(
            id=str(style_set.id),
            name=style_set.name,
            styles=style_set.styles,
            is_active=style_set.is_active
        )
        for style_set in style_sets
    ]


@router.post("/text-style-sets", response_model=TextStyleSetResponse)
async def create_text_style_set(
    style_data: TextStyleSetCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Create a new text style set"""
    try:
        style_set = AdminService.create_text_style_set(db, style_data, admin_user)
        return TextStyleSetResponse(
            id=str(style_set.id),
            name=style_set.name,
            styles=style_set.styles,
            is_active=style_set.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating text style set: {str(e)}"
        )


@router.put("/text-style-sets/{set_id}", response_model=TextStyleSetResponse)
async def update_text_style_set(
    set_id: str,
    style_data: TextStyleSetUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update a text style set"""
    style_set = AdminService.get_text_style_set_by_id(db, set_id, admin_user)
    if not style_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Text style set not found"
        )
    
    try:
        update_data = style_data.dict(exclude_unset=True)
        updated_style_set = AdminService.update_text_style_set(db, style_set, update_data)
        return TextStyleSetResponse(
            id=str(updated_style_set.id),
            name=updated_style_set.name,
            styles=updated_style_set.styles,
            is_active=updated_style_set.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating text style set: {str(e)}"
        )


@router.delete("/text-style-sets/{set_id}", status_code=204)
async def delete_text_style_set(
    set_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete a text style set"""
    style_set = AdminService.get_text_style_set_by_id(db, set_id, admin_user)
    if not style_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Text style set not found"
        )
    
    try:
        AdminService.delete_text_style_set(db, style_set)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting text style set: {str(e)}"
        )


# Rules Management
@router.get("/rules/adaptation", response_model=AdaptationRule)
async def get_adaptation_rules(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get Image Template Rules and Adaptation Settings for the admin's organization"""
    return AdminService.get_adaptation_rules(db, admin_user)


@router.put("/rules/adaptation", response_model=AdaptationRule)
async def update_adaptation_rules(
    rules: AdaptationRule,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update Image Template Rules and Adaptation Settings"""
    try:
        rule_value = {
            "logic": rules.focalPointLogic,
            "layoutGuidance": rules.layoutGuidance
        }
        AdminService.update_rule(
            db, 
            "focal_point_logic", 
            rule_value,
            admin_user,
            "Focal point detection logic and layout guidance for image adaptation"
        )
        return rules
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating adaptation rules: {str(e)}"
        )


@router.get("/rules/ai-behavior", response_model=AIBehaviorRule)
async def get_ai_behavior_rules(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get AI Behavior Controls for the admin's organization"""
    return AdminService.get_ai_behavior_rules(db, admin_user)


@router.put("/rules/ai-behavior", response_model=AIBehaviorRule)
async def update_ai_behavior_rules(
    rules: AIBehaviorRule,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update AI Behavior Controls"""
    try:
        rule_value = {
            "strategy": rules.adaptationStrategy,
            "imageQuality": rules.imageQuality
        }
        AdminService.update_rule(
            db,
            "ai_adaptation_strategy",
            rule_value,
            admin_user,
            "AI adaptation strategy and image quality settings"
        )
        return rules
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating AI behavior rules: {str(e)}"
        )


@router.get("/rules/upload-moderation", response_model=UploadModerationRule)
async def get_upload_moderation_rules(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get Content Moderation and Upload Rules for the admin's organization"""
    return AdminService.get_upload_moderation_rules(db, admin_user)


@router.put("/rules/upload-moderation", response_model=UploadModerationRule)
async def update_upload_moderation_rules(
    rules: UploadModerationRule,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update Content Moderation and Upload Rules"""
    try:
        AdminService.update_rule(
            db,
            "upload_moderation",
            rules.dict(),
            admin_user,
            "Upload and content moderation settings"
        )
        return rules
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating upload moderation rules: {str(e)}"
        )


@router.get("/rules/manual-editing", response_model=ManualEditingRule)
async def get_manual_editing_rules(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get Manual Editing Rules for Users in the admin's organization"""
    return AdminService.get_manual_editing_rules(db, admin_user)


@router.put("/rules/manual-editing", response_model=ManualEditingRule)
async def update_manual_editing_rules(
    rules: ManualEditingRule,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update Manual Editing Rules for Users"""
    try:
        AdminService.update_rule(
            db,
            "manual_editing",
            rules.dict(),
            admin_user,
            "Manual editing capabilities and restrictions for users"
        )
        return rules
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating manual editing rules: {str(e)}"
        )

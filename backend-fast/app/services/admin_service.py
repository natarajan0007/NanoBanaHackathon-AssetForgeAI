import logging
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.models.repurposing_platform import RepurposingPlatform
from app.models.asset_format import AssetFormat, FormatType
from app.models.text_style_set import TextStyleSet
from app.models.app_setting import AppSetting
from app.models.user import User
from app.schemas.admin import (
    PlatformCreate, AssetFormatCreate, TextStyleSetCreate,
    AdaptationRule, AIBehaviorRule, UploadModerationRule, ManualEditingRule
)

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin operations"""
    
    # Platform Management
    @staticmethod
    def create_platform(db: Session, platform_data: PlatformCreate, admin_user: User) -> RepurposingPlatform:
        """Create a new repurposing platform"""
        platform = RepurposingPlatform(
            name=platform_data.name,
            organization_id=admin_user.organization_id,
            created_by_admin_id=admin_user.id
        )
        db.add(platform)
        db.commit()
        db.refresh(platform)
        return platform
    
    @staticmethod
    def get_platforms(db: Session, admin_user: User) -> List[RepurposingPlatform]:
        """Get all platforms for the admin's organization"""
        return db.query(RepurposingPlatform).filter(
            RepurposingPlatform.organization_id == admin_user.organization_id
        ).all()
    
    @staticmethod
    def get_platform_by_id(db: Session, platform_id: str, admin_user: User) -> Optional[RepurposingPlatform]:
        """Get platform by ID from the admin's organization"""
        return db.query(RepurposingPlatform).filter(
            RepurposingPlatform.id == platform_id,
            RepurposingPlatform.organization_id == admin_user.organization_id
        ).first()
    
    @staticmethod
    def update_platform(db: Session, platform: RepurposingPlatform, name: str) -> RepurposingPlatform:
        """Update platform name"""
        platform.name = name
        db.commit()
        db.refresh(platform)
        return platform
    
    @staticmethod
    def delete_platform(db: Session, platform: RepurposingPlatform) -> None:
        """Delete platform"""
        db.delete(platform)
        db.commit()
    
    # Format Management
    @staticmethod
    def create_format(db: Session, format_data: AssetFormatCreate, admin_user: User) -> AssetFormat:
        """Create a new asset format"""
        asset_format = AssetFormat(
            name=format_data.name,
            type=FormatType(format_data.type),
            platform_id=format_data.platformId if format_data.platformId else None,
            category=format_data.category,
            width=format_data.width,
            height=format_data.height,
            organization_id=admin_user.organization_id,
            created_by_admin_id=admin_user.id
        )
        db.add(asset_format)
        db.commit()
        db.refresh(asset_format)
        return asset_format
    
    @staticmethod
    def get_formats(
        db: Session, 
        admin_user: User,
        format_type: Optional[str] = None, 
        category: Optional[str] = None
    ) -> List[AssetFormat]:
        """Get asset formats for the admin's organization with optional filtering"""
        query = db.query(AssetFormat).filter(AssetFormat.organization_id == admin_user.organization_id)
        
        if format_type:
            query = query.filter(AssetFormat.type == FormatType(format_type))
        if category:
            query = query.filter(AssetFormat.category == category)
        
        return query.all()
    
    @staticmethod
    def get_format_by_id(db: Session, format_id: str, admin_user: User) -> Optional[AssetFormat]:
        """Get format by ID from the admin's organization"""
        return db.query(AssetFormat).filter(
            AssetFormat.id == format_id,
            AssetFormat.organization_id == admin_user.organization_id
        ).first()
    
    @staticmethod
    def update_format(db: Session, asset_format: AssetFormat, update_data: dict) -> AssetFormat:
        """Update asset format"""
        for field, value in update_data.items():
            if value is not None:
                if field == "type":
                    setattr(asset_format, field, FormatType(value))
                else:
                    setattr(asset_format, field, value)
        
        db.commit()
        db.refresh(asset_format)
        return asset_format
    
    @staticmethod
    def delete_format(db: Session, asset_format: AssetFormat) -> None:
        """Delete asset format"""
        db.delete(asset_format)
        db.commit()
    
    # Text Style Set Management
    @staticmethod
    def create_text_style_set(db: Session, style_data: TextStyleSetCreate, admin_user: User) -> TextStyleSet:
        """Create a new text style set"""
        style_set = TextStyleSet(
            name=style_data.name,
            styles=style_data.styles,
            organization_id=admin_user.organization_id,
            created_by_admin_id=admin_user.id
        )
        db.add(style_set)
        db.commit()
        db.refresh(style_set)
        return style_set
    
    @staticmethod
    def get_text_style_sets(db: Session, admin_user: User) -> List[TextStyleSet]:
        """Get all text style sets for the admin's organization"""
        return db.query(TextStyleSet).filter(
            TextStyleSet.organization_id == admin_user.organization_id
        ).all()
    
    @staticmethod
    def get_text_style_set_by_id(db: Session, set_id: str, admin_user: User) -> Optional[TextStyleSet]:
        """Get text style set by ID from the admin's organization"""
        return db.query(TextStyleSet).filter(
            TextStyleSet.id == set_id,
            TextStyleSet.organization_id == admin_user.organization_id
        ).first()
    
    @staticmethod
    def update_text_style_set(db: Session, style_set: TextStyleSet, update_data: dict) -> TextStyleSet:
        """Update text style set"""
        for field, value in update_data.items():
            if value is not None:
                setattr(style_set, field, value)
        
        db.commit()
        db.refresh(style_set)
        return style_set
    
    @staticmethod
    def delete_text_style_set(db: Session, style_set: TextStyleSet) -> None:
        """Delete text style set"""
        db.delete(style_set)
        db.commit()
    
    # Rules Management
    @staticmethod
    def get_rule(db: Session, rule_key: str, admin_user: User) -> Optional[AppSetting]:
        """Get rule by key for the admin's organization"""
        return db.query(AppSetting).filter(
            AppSetting.rule_key == rule_key,
            AppSetting.organization_id == admin_user.organization_id
        ).first()
    
    @staticmethod
    def update_rule(db: Session, rule_key: str, rule_value: dict, admin_user: User, description: str = None) -> AppSetting:
        """Update or create rule for the admin's organization"""
        setting = db.query(AppSetting).filter(
            AppSetting.rule_key == rule_key,
            AppSetting.organization_id == admin_user.organization_id
        ).first()
        
        if setting:
            setting.rule_value = rule_value
            if description:
                setting.description = description
        else:
            setting = AppSetting(
                rule_key=rule_key,
                rule_value=rule_value,
                organization_id=admin_user.organization_id,
                description=description
            )
            db.add(setting)
        
        db.commit()
        db.refresh(setting)
        return setting
    
    @staticmethod
    def get_adaptation_rules(db: Session, admin_user: User) -> AdaptationRule:
        """Get adaptation rules for the admin's organization"""
        setting = AdminService.get_rule(db, "focal_point_logic", admin_user)
        focal_logic = "face-centric"
        layout_guidance = None
        
        if setting and setting.rule_value:
            focal_logic = setting.rule_value.get("logic", "face-centric")
            layout_guidance = setting.rule_value.get("layoutGuidance")
        
        return AdaptationRule(
            focalPointLogic=focal_logic,
            layoutGuidance=layout_guidance
        )
    
    @staticmethod
    def get_ai_behavior_rules(db: Session, admin_user: User) -> AIBehaviorRule:
        """Get AI behavior rules for the admin's organization"""
        setting = AdminService.get_rule(db, "ai_adaptation_strategy", admin_user)
        strategy = "crop"
        quality = "high"
        
        if setting and setting.rule_value:
            strategy = setting.rule_value.get("strategy", "crop")
            quality = setting.rule_value.get("imageQuality", "high")
        
        return AIBehaviorRule(
            adaptationStrategy=strategy,
            imageQuality=quality
        )
    
    @staticmethod
    def get_upload_moderation_rules(db: Session, admin_user: User) -> UploadModerationRule:
        """Get upload moderation rules for the admin's organization"""
        setting = AdminService.get_rule(db, "upload_moderation", admin_user)
        
        if setting and setting.rule_value:
            return UploadModerationRule(**setting.rule_value)
        
        # Default values
        return UploadModerationRule(
            allowedImageTypes=["jpeg", "png", "psd"],
            maxFileSizeMb=50,
            nsfwAlertsActive=True
        )
    
    @staticmethod
    def get_manual_editing_rules(db: Session, admin_user: User) -> ManualEditingRule:
        """Get manual editing rules for the admin's organization"""
        setting = AdminService.get_rule(db, "manual_editing", admin_user)
        
        if setting and setting.rule_value:
            return ManualEditingRule(**setting.rule_value)
        
        # Default values
        return ManualEditingRule(
            editingEnabled=True,
            croppingEnabled=True,
            saturationEnabled=True,
            addTextOrLogoEnabled=True,
            allowedLogoSources={
                "types": ["jpeg", "png", "ai"],
                "maxSizeMb": 5
            }
        )

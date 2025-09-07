#!/usr/bin/env python3
"""
Initialize the database with tables and sample data
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from app.core.config import settings
from app.models import Base, User, RepurposingPlatform, AssetFormat, TextStyleSet, AppSetting, Organization
from app.core.security import get_password_hash
from app.models.user import UserRole
from app.models.asset_format import FormatType


def init_database():
    """Initialize database with tables and sample data"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create a default organization if not exists
        default_org = db.query(Organization).filter(Organization.name == "Default Organization").first()
        if not default_org:
            default_org = Organization(name="Default Organization")
            db.add(default_org)
            db.commit()
            db.refresh(default_org)
            print("Created Default Organization")

        # Create admin user if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@aicreat.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                organization_id=default_org.id
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Created admin user: admin / admin123")
        
        # Create sample platforms
        platforms_data = [
            {"name": "Instagram"},
            {"name": "Facebook"},
            {"name": "Twitter"},
            {"name": "LinkedIn"},
        ]
        
        for platform_data in platforms_data:
            existing = db.query(RepurposingPlatform).filter(
                RepurposingPlatform.name == platform_data["name"],
                RepurposingPlatform.organization_id == default_org.id
            ).first()
            if not existing:
                platform = RepurposingPlatform(
                    name=platform_data["name"],
                    organization_id=default_org.id,
                    created_by_admin_id=admin_user.id
                )
                db.add(platform)
        
        db.commit()
        
        # Create sample asset formats
        instagram = db.query(RepurposingPlatform).filter(RepurposingPlatform.name == "Instagram", RepurposingPlatform.organization_id == default_org.id).first()
        facebook = db.query(RepurposingPlatform).filter(RepurposingPlatform.name == "Facebook", RepurposingPlatform.organization_id == default_org.id).first()
        
        formats_data = [
            # Resizing formats
            {"name": "Mobile Banner", "type": FormatType.RESIZING, "category": "Mobile", "width": 320, "height": 100},
            {"name": "Desktop Banner", "type": FormatType.RESIZING, "category": "Web", "width": 1200, "height": 400},
            {"name": "Square Thumbnail", "type": FormatType.RESIZING, "category": "Thumbnail", "width": 300, "height": 300},
            
            # Repurposing formats
            {"name": "Instagram Post", "type": FormatType.REPURPOSING, "platform_id": instagram.id if instagram else None, "width": 1080, "height": 1080},
            {"name": "Instagram Story", "type": FormatType.REPURPOSING, "platform_id": instagram.id if instagram else None, "width": 1080, "height": 1920},
            {"name": "Facebook Post", "type": FormatType.REPURPOSING, "platform_id": facebook.id if facebook else None, "width": 1200, "height": 630},
        ]
        
        for format_data in formats_data:
            existing = db.query(AssetFormat).filter(
                AssetFormat.name == format_data["name"],
                AssetFormat.organization_id == default_org.id
            ).first()
            if not existing:
                asset_format = AssetFormat(
                    name=format_data["name"],
                    type=format_data["type"],
                    platform_id=format_data.get("platform_id"),
                    category=format_data.get("category"),
                    width=format_data["width"],
                    height=format_data["height"],
                    organization_id=default_org.id,
                    created_by_admin_id=admin_user.id
                )
                db.add(asset_format)
        
        db.commit()
        
        # Create sample text style sets
        style_sets_data = [
            {
                "name": "Modern Brand Kit",
                "styles": {
                    "title": {"fontFamily": "Inter", "fontSize": 48, "fontWeight": "bold", "color": "#000000"},
                    "subtitle": {"fontFamily": "Inter", "fontSize": 24, "fontWeight": "medium", "color": "#666666"},
                    "content": {"fontFamily": "Inter", "fontSize": 16, "fontWeight": "normal", "color": "#333333"}
                }
            },
            {
                "name": "Elegant Style",
                "styles": {
                    "title": {"fontFamily": "Playfair Display", "fontSize": 52, "fontWeight": "bold", "color": "#1a1a1a"},
                    "subtitle": {"fontFamily": "Source Sans Pro", "fontSize": 20, "fontWeight": "medium", "color": "#555555"},
                    "content": {"fontFamily": "Source Sans Pro", "fontSize": 14, "fontWeight": "normal", "color": "#777777"}
                }
            }
        ]
        
        for style_data in style_sets_data:
            existing = db.query(TextStyleSet).filter(
                TextStyleSet.name == style_data["name"],
                TextStyleSet.organization_id == default_org.id
            ).first()
            if not existing:
                style_set = TextStyleSet(
                    name=style_data["name"],
                    styles=style_data["styles"],
                    organization_id=default_org.id,
                    created_by_admin_id=admin_user.id
                )
                db.add(style_set)
        
        db.commit()
        
        # Create default app settings
        settings_data = [
            {
                "rule_key": "focal_point_logic",
                "rule_value": {"logic": "face-centric"},
                "description": "Focal point detection logic for image adaptation"
            },
            {
                "rule_key": "ai_adaptation_strategy",
                "rule_value": {"strategy": "crop"},
                "description": "AI adaptation strategy for image processing"
            },
            {
                "rule_key": "upload_moderation",
                "rule_value": {
                    "allowedImageTypes": ["jpeg", "png", "psd"],
                    "maxFileSizeMb": 50,
                    "nsfwAlertsActive": True
                },
                "description": "Upload and content moderation settings"
            },
            {
                "rule_key": "manual_editing",
                "rule_value": {
                    "editingEnabled": True,
                    "croppingEnabled": True,
                    "saturationEnabled": True,
                    "addTextOrLogoEnabled": True,
                    "allowedLogoSources": {
                        "types": ["jpeg", "png", "ai"],
                        "maxSizeMb": 5
                    }
                },
                "description": "Manual editing capabilities for users"
            }
        ]
        
        for setting_data in settings_data:
            existing = db.query(AppSetting).filter(
                AppSetting.rule_key == setting_data["rule_key"],
                AppSetting.organization_id == default_org.id
            ).first()
            if not existing:
                setting = AppSetting(
                    rule_key=setting_data["rule_key"],
                    rule_value=setting_data["rule_value"],
                    organization_id=default_org.id,
                    description=setting_data["description"]
                )
                db.add(setting)
        
        db.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

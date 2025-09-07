from app.core.database import Base
from .organization import Organization
from .user import User
from .project import Project
from .asset import Asset
from .generation_job import GenerationJob
from .repurposing_platform import RepurposingPlatform
from .asset_format import AssetFormat
from .generated_asset import GeneratedAsset
from .text_style_set import TextStyleSet
from .app_setting import AppSetting
from sqlalchemy.orm import relationship

# Define relationships that might not be explicitly defined in the models
# This ensures SQLAlchemy understands the full object model
User.projects = relationship("Project", back_populates="user")
User.generation_jobs = relationship("GenerationJob", back_populates="user")

__all__ = [
    "Base",
    "Organization",
    "User",
    "Project", 
    "Asset",
    "GenerationJob",
    "RepurposingPlatform",
    "AssetFormat",
    "GeneratedAsset",
    "TextStyleSet",
    "AppSetting"
]

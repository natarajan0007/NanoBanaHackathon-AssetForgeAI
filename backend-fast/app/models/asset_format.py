from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base


class FormatType(str, enum.Enum):
    RESIZING = "resizing"
    REPURPOSING = "repurposing"


class AssetFormat(Base):
    __tablename__ = "asset_formats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(FormatType), nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("repurposing_platforms.id", ondelete="CASCADE"))
    category = Column(String(50))  # 'Mobile', 'Web', etc. Only for 'resizing' type
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="asset_formats")
    platform = relationship("RepurposingPlatform", back_populates="asset_formats")
    created_by_admin = relationship("User")
    generated_assets = relationship("GeneratedAsset", back_populates="asset_format")

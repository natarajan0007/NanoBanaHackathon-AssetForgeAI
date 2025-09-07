from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False)
    original_asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    asset_format_id = Column(UUID(as_uuid=True), ForeignKey("asset_formats.id", ondelete="SET NULL"))
    storage_path = Column(String, nullable=False)
    file_type = Column(String(10), nullable=False)
    dimensions = Column(JSONB, nullable=False)  # {"width": 1080, "height": 1080}
    is_nsfw = Column(Boolean, default=False)
    # JSONB to store current state of manual edits
    # Example: {"crop": {"x":0,"y":0,"w":1080,"h":1080}, "saturation": 1.1, "textOverlays": [...]}
    manual_edits = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("GenerationJob", back_populates="generated_assets")
    original_asset = relationship("Asset", back_populates="generated_assets")
    asset_format = relationship("AssetFormat", back_populates="generated_assets")

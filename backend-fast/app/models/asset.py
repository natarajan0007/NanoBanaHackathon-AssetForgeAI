from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String, nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    dimensions = Column(JSONB)  # {"width": 1920, "height": 1080}
    dpi = Column(Integer)
    ai_metadata = Column(JSONB)  # {"product": [...], "text": [...], "faces": [...]}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="assets")
    generated_assets = relationship("GeneratedAsset", back_populates="original_asset")

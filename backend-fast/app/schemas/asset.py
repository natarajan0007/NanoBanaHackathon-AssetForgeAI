from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class AssetBase(BaseModel):
    original_filename: str
    file_type: str
    file_size_bytes: int


class AssetCreate(AssetBase):
    project_id: str
    storage_path: str
    dimensions: Optional[Dict[str, int]] = None
    dpi: Optional[int] = None


class AssetResponse(BaseModel):
    id: str
    project_id: str
    original_filename: str
    storage_path: str
    file_type: str
    file_size_bytes: int
    dimensions: Optional[Dict[str, int]]
    dpi: Optional[int]
    ai_metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class AssetMetadata(BaseModel):
    layers: Optional[int] = None
    width: int
    height: int
    dpi: Optional[int] = None
    detectedElements: List[str] = []

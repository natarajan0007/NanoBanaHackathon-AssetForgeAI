from pydantic import BaseModel, UUID4
from typing import List, Optional, Dict, Any
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CustomResize(BaseModel):
    width: int
    height: int


class GenerationRequest(BaseModel):
    projectId: UUID4
    formatIds: List[UUID4]
    customResizes: Optional[List[CustomResize]] = []
    prompt: Optional[str] = None


class GenerationResponse(BaseModel):
    jobId: str


class PromptEditRequest(BaseModel):
    originalAssetId: UUID4
    prompt: str
    jobId: Optional[UUID4] = None # Optional: to group edits under a single job


class PromptEditResponse(BaseModel):
    newAssetId: UUID4




class GenerationStatusResponse(BaseModel):
    status: JobStatus
    progress: int


class TextOverlay(BaseModel):
    content: str
    textStyleSetId: str
    styleType: str  # title, subtitle, content
    position: Dict[str, float]  # {"x": 0.5, "y": 0.5}


class LogoOverlay(BaseModel):
    logoUrl: str
    position: Dict[str, float]
    size: float  # Size as percentage of canvas width


class ManualEdits(BaseModel):
    crop: Optional[Dict[str, float]] = None  # {"x": 0, "y": 0, "width": 1, "height": 1}
    saturation: Optional[float] = None  # 0.0 to 2.0
    textOverlays: Optional[List[TextOverlay]] = []
    logoOverlay: Optional[LogoOverlay] = None


class GeneratedAssetResponse(BaseModel):
    id: str
    originalAssetId: str
    filename: str
    assetUrl: str
    platformName: Optional[str] = None
    formatName: str
    dimensions: Dict[str, int]
    isNsfw: bool
    manualEdits: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DownloadRequest(BaseModel):
    assetIds: List[UUID4]
    format: str  # jpeg, png
    quality: str  # high, medium, low
    grouping: str  # individual, batch, category


class DownloadResponse(BaseModel):
    downloadUrl: str

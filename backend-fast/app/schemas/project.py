from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY_FOR_REVIEW = "ready_for_review"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectCreate(BaseModel):
    name: str


class ProjectUploadResponse(BaseModel):
    projectId: str


class ProjectStatusResponse(BaseModel):
    status: ProjectStatus
    progress: int


class AssetPreview(BaseModel):
    id: str
    filename: str
    previewUrl: str
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: str
    name: str
    status: str
    submitDate: datetime
    fileCounts: Dict[str, int]
    assets: List[AssetPreview]

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    pageSize: int

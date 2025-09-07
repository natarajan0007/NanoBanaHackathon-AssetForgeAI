from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class PlatformCreate(BaseModel):
    name: str


class PlatformUpdate(BaseModel):
    name: str


class PlatformResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class AssetFormatCreate(BaseModel):
    name: str
    type: str  # resizing, repurposing
    platformId: Optional[str] = None
    category: Optional[str] = None
    width: int
    height: int


class AssetFormatUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    platformId: Optional[str] = None
    category: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class AssetFormatResponse(BaseModel):
    id: str
    name: str
    type: str
    platformId: Optional[str] = None
    category: Optional[str] = None
    width: int
    height: int
    is_active: bool

    class Config:
        from_attributes = True


class TextStyleDefinition(BaseModel):
    fontFamily: str
    fontSize: int
    fontWeight: str
    color: str


class TextStyleSetCreate(BaseModel):
    name: str
    styles: Dict[str, TextStyleDefinition]  # title, subtitle, content


class TextStyleSetUpdate(BaseModel):
    name: Optional[str] = None
    styles: Optional[Dict[str, TextStyleDefinition]] = None


class TextStyleSetResponse(BaseModel):
    id: str
    name: str
    styles: Dict[str, Any]
    is_active: bool

    class Config:
        from_attributes = True


class AdaptationRule(BaseModel):
    focalPointLogic: str
    layoutGuidance: Optional[Dict[str, Any]] = None


class AIBehaviorRule(BaseModel):
    adaptationStrategy: str
    imageQuality: str


class UploadModerationRule(BaseModel):
    allowedImageTypes: List[str]
    maxFileSizeMb: int
    nsfwAlertsActive: bool


class ManualEditingRule(BaseModel):
    editingEnabled: bool
    croppingEnabled: bool
    saturationEnabled: bool
    addTextOrLogoEnabled: bool
    allowedLogoSources: Dict[str, Any]

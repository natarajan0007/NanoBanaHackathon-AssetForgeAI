from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.asset_format import AssetFormat, FormatType
from app.models.repurposing_platform import RepurposingPlatform
from app.schemas.format import FormatResponse

router = APIRouter()


@router.get("", response_model=Dict[str, List[FormatResponse]])
async def get_formats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available asset formats for users"""
    # Get all active formats
    formats = db.query(AssetFormat).filter(AssetFormat.is_active == True).all()
    
    # Separate by type
    resizing_formats = []
    repurposing_formats = []
    
    for format_obj in formats:
        format_response = FormatResponse(
            id=str(format_obj.id),
            name=format_obj.name,
            type=format_obj.type.value,
            platformId=str(format_obj.platform_id) if format_obj.platform_id else None,
            category=format_obj.category,
            width=format_obj.width,
            height=format_obj.height
        )
        
        if format_obj.type == FormatType.RESIZING:
            resizing_formats.append(format_response)
        else:
            repurposing_formats.append(format_response)
    
    return {
        "resizing": resizing_formats,
        "repurposing": repurposing_formats
    }

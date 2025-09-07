from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.generated_asset import GeneratedAsset
from app.models.asset import Asset
from app.schemas.generation import GeneratedAssetResponse
from app.services.generation_service import GenerationService

router = APIRouter()

@router.get("/{original_asset_id}/generated", response_model=List[GeneratedAssetResponse])
async def get_generated_assets_for_original(
    original_asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all generated assets for a specific original asset.
    """
    # Verify that the original asset belongs to the user's organization
    original_asset = db.query(Asset).filter(Asset.id == original_asset_id).first()
    if not original_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original asset not found"
        )
    
    if original_asset.project.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this asset."
        )

    generated_assets = db.query(GeneratedAsset).filter(
        GeneratedAsset.original_asset_id == original_asset_id
    ).order_by(GeneratedAsset.created_at.desc()).all()

    if not generated_assets:
        return []

    return [GenerationService.convert_to_response(asset) for asset in generated_assets]


@router.get("/{asset_id}/prompt-suggestions", response_model=List[str])
async def get_prompt_suggestions(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate dynamic prompt suggestions for editing an asset."""
    try:
        suggestions = await GenerationService.get_prompt_suggestions(db, asset_id, current_user)
        return suggestions
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating prompt suggestions: {str(e)}"
        )

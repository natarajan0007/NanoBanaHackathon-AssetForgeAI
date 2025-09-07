from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, List
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.generated_asset import GeneratedAsset
from app.schemas.generation import (
    GenerationRequest,
    GenerationResponse,
    GenerationStatusResponse,
    GeneratedAssetResponse,
    ManualEdits,
    DownloadRequest,
    DownloadResponse,
    PromptEditRequest
)
from app.services.generation_service import GenerationService
from app.tasks.generation_tasks import process_generation_job
import tempfile
import zipfile
import os
import shutil
from starlette.background import BackgroundTask
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=GenerationResponse)
async def start_generation(
    request: GenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new generation job"""
    try:
        # Create generation job
        job = GenerationService.create_generation_job(db, request, current_user)
        
        # Queue background task
        process_generation_job.delay(str(job.id), request.dict())
        
        return GenerationResponse(jobId=str(job.id))
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting generation: {str(e)}"
        )


@router.post("/prompt-edit", status_code=status.HTTP_202_ACCEPTED)
async def prompt_edit(
    request: PromptEditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accepts a prompt to edit a single asset."""
    try:
        task_id = GenerationService.dispatch_prompt_edit_task(db, request, current_user)
        return {"taskId": task_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error dispatching prompt edit task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error dispatching prompt edit task: {str(e)}"
        )


@router.get("/{job_id}/status", response_model=GenerationStatusResponse)
async def get_generation_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get generation job status"""
    job = GenerationService.get_job_by_id(db, job_id, current_user)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job not found"
        )
    
    return GenerationStatusResponse(
        status=job.status,
        progress=job.progress
    )


@router.get("/{job_id}/results", response_model=Dict[str, List[GeneratedAssetResponse]])
async def get_generation_results(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get generation job results"""
    job = GenerationService.get_job_by_id(db, job_id, current_user)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job not found"
        )
    
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generation job is not completed yet"
        )
    
    return GenerationService.get_job_results(db, job)


@router.get("/generated-assets/{asset_id}", response_model=GeneratedAssetResponse)
async def get_generated_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single generated asset"""
    asset = db.query(GeneratedAsset).filter(GeneratedAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated asset not found"
        )
    
    # Verify user owns the asset through the job
    if asset.job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return GenerationService.convert_to_response(asset)


@router.put("/generated-assets/{asset_id}", response_model=GeneratedAssetResponse)
async def update_generated_asset(
    asset_id: str,
    edits: ManualEdits,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply manual edits to a generated asset"""
    asset = db.query(GeneratedAsset).filter(GeneratedAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated asset not found"
        )
    
    # Verify user owns the asset
    if asset.job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Apply manual edits
        updated_asset = GenerationService.apply_manual_edits(
            db, asset, edits.dict(exclude_unset=True)
        )
        
        return GenerationService.convert_to_response(updated_asset)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying edits: {str(e)}"
        )


@router.post("/download")
async def create_download(
    request: DownloadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a zip file of selected assets and returns it directly."""
    logger.info(f"Download request: {request}")
    
    # Query assets
    assets = db.query(GeneratedAsset).filter(
        GeneratedAsset.id.in_(request.assetIds)
    ).all()
    
    if not assets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assets found"
        )
    
    logger.info(f"Found {len(assets)} assets")
    
    # Verify user owns all assets
    for asset in assets:
        if asset.job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to one or more assets"
            )
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temp directory: {temp_dir}")
    
    try:
        zip_filename = f"AssetForge_Assets_{len(assets)}_items.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        # Track files added to zip for debugging
        files_added = []
        files_missing = []
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, asset in enumerate(assets):
                # Get the absolute path to the file
                file_on_disk = os.path.abspath(os.path.join("uploads", asset.storage_path))
                
                logger.info(f"Processing asset {i+1}: {str(asset.id)}")  # Convert UUID to string
                logger.info(f"Storage path: {asset.storage_path}")
                logger.info(f"Full file path: {file_on_disk}")
                logger.info(f"File exists: {os.path.exists(file_on_disk)}")
                
                if os.path.exists(file_on_disk):
                    # Get file size for debugging
                    file_size = os.path.getsize(file_on_disk)
                    logger.info(f"File size: {file_size} bytes")
                    
                    # Create a descriptive name for the file inside the zip
                    try:
                        platform_name = asset.asset_format.platform.name if asset.asset_format and asset.asset_format.platform else "Unknown_Platform"
                        format_name = asset.asset_format.name if asset.asset_format else "untitled"
                    except AttributeError:
                        platform_name = "Unknown_Platform"
                        format_name = "untitled"
                    
                    # Clean filename to avoid path issues
                    platform_name = "".join(c for c in platform_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    format_name = "".join(c for c in format_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    
                    file_type = asset.file_type or "unknown"
                    if '/' in file_type:
                        file_extension = file_type.split('/')[-1]
                    else:
                        file_extension = file_type
                    asset_id_short = str(asset.id)[:8]  # Convert UUID to string first
                    zip_internal_path = f"{platform_name}/{format_name}_{asset_id_short}.{file_extension}"
                    
                    # Add file to zip
                    zip_file.write(file_on_disk, zip_internal_path)
                    files_added.append({
                        "asset_id": str(asset.id),  # Convert UUID to string
                        "original_path": file_on_disk,
                        "zip_path": zip_internal_path,
                        "size": file_size
                    })
                    logger.info(f"Added to zip: {zip_internal_path}")
                else:
                    files_missing.append({
                        "asset_id": str(asset.id),  # Convert UUID to string
                        "expected_path": file_on_disk
                    })
                    logger.warning(f"File not found: {file_on_disk}")
        
        # Check if zip file was created successfully
        if not os.path.exists(zip_path):
            raise Exception("Zip file was not created")
        
        zip_size = os.path.getsize(zip_path)
        logger.info(f"Zip file created successfully: {zip_path}")
        logger.info(f"Zip file size: {zip_size} bytes")
        logger.info(f"Files added: {len(files_added)}")
        logger.info(f"Files missing: {len(files_missing)}")
        
        if zip_size == 0:
            raise Exception("Zip file is empty")
        
        if len(files_added) == 0:
            raise Exception("No files were added to the zip")
        
        # Return the zip file with proper cleanup
        def cleanup_temp_dir():
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")
        
        return FileResponse(
            path=zip_path,
            media_type='application/zip',
            filename=zip_filename,
            headers={
                "Content-Disposition": f"attachment; filename=\"{zip_filename}\"",
                "Content-Length": str(zip_size)
            },
            background=BackgroundTask(cleanup_temp_dir)
        )
        
    except Exception as e:
        # Clean up temp directory on error
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        logger.error(f"Error creating download: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating download: {str(e)}"
        )
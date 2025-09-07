import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.asset import Asset
from app.models.generation_job import GenerationJob
from app.schemas.activity import Activity
from app.schemas.project import (
    ProjectUploadResponse, 
    ProjectStatusResponse, 
    ProjectResponse,
    ProjectListResponse,
    AssetPreview
)
from app.services.project_service import ProjectService
from app.services.file_service import FileService
from app.tasks.asset_processing import process_uploaded_assets

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
    sort: str = "desc",
    status: Optional[str] = None
):
    """Get user's projects with pagination"""
    projects = ProjectService.get_user_projects(
        db, current_user, skip=offset, limit=limit, sort=sort, status=status
    )
    
    # Convert to response format
    project_responses = []
    for project in projects:
        assets = ProjectService.get_project_assets(db, project)
        project_response = ProjectService.convert_to_response(project, assets)
        project_responses.append(project_response)
    
    # Get total count for pagination
    total = db.query(Project).filter(Project.user_id == current_user.id).count()
    
    return ProjectListResponse(
        projects=project_responses,
        total=total,
        page=offset // limit + 1,
        pageSize=limit
    )


@router.post("/upload", response_model=ProjectUploadResponse)
async def upload_project_assets(
    projectName: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create project and upload assets"""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Validate all files first
    for file in files:
        FileService.validate_file(file)
    
    # Create project
    from app.schemas.project import ProjectCreate
    project_data = ProjectCreate(name=projectName)
    project = ProjectService.create_project(db, project_data, current_user)
    
    try:
        # Save files and create asset records
        assets_created = []
        for file in files:
            # Save file
            storage_path, file_size, checksum = await FileService.save_file(
                file, str(project.id)
            )
            
            # Extract basic metadata
            metadata = FileService.extract_image_metadata(storage_path)
            
            # Create asset record
            asset = Asset(
                project_id=project.id,
                original_filename=file.filename,
                storage_path=storage_path,
                file_type=file.content_type.split('/')[-1],
                file_size_bytes=file_size,
                dimensions={"width": metadata.get("width"), "height": metadata.get("height")} if metadata.get("width") else None,
                dpi=metadata.get("dpi")
            )
            db.add(asset)
            assets_created.append(asset)
        
        db.commit()
        
        # Update project status to processing
        ProjectService.update_project_status(db, project, ProjectStatus.PROCESSING)
        
        # Queue background task for AI processing
        process_uploaded_assets.delay(str(project.id))
        
        return ProjectUploadResponse(projectId=str(project.id))
        
    except Exception as e:
        # Rollback and cleanup files on error
        db.rollback()
        for asset in assets_created:
            if hasattr(asset, 'storage_path'):
                FileService.delete_file(asset.storage_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing upload: {str(e)}"
        )

@router.get("/recent-activity", response_model=List[Activity])
async def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 5
):
    """Get recent generation jobs for the user."""
    recent_jobs = (
        db.query(GenerationJob)
        .filter(GenerationJob.user_id == current_user.id)
        .order_by(GenerationJob.created_at.desc())
        .limit(limit)
        .all()
    )

    activities = []
    for job in recent_jobs:
        activities.append(
            Activity(
                id=job.id,
                projectName=job.project.name,
                status=job.status.value,
                createdAt=job.created_at
            )
        )
    return activities

@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_project_status(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project status for polling"""
    project = ProjectService.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    progress = ProjectService.calculate_processing_progress(project)
    
    return ProjectStatusResponse(
        status=project.status,
        progress=progress
    )


@router.get("/{project_id}/preview", response_model=List[AssetPreview])
async def get_project_preview(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI analysis preview of assets"""
    project = ProjectService.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.status not in [ProjectStatus.READY_FOR_REVIEW, ProjectStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not ready for preview"
        )
    
    assets = ProjectService.get_project_assets(db, project)
    
    # Convert to preview format
    previews = []
    for asset in assets:
        preview_url = FileService.get_file_url(asset.storage_path)
        
        # Prepare metadata for preview
        metadata = {
            "layers": None,  # Would be extracted from PSD
            "width": asset.dimensions.get("width") if asset.dimensions else None,
            "height": asset.dimensions.get("height") if asset.dimensions else None,
            "dpi": asset.dpi,
            "detectedElements": []
        }
        
        # Add AI metadata if available
        if asset.ai_metadata:
            metadata["detectedElements"] = asset.ai_metadata.get("detected_elements", [])
        
        preview = AssetPreview(
            id=str(asset.id),
            filename=asset.original_filename,
            previewUrl=preview_url,
            metadata=metadata
        )
        previews.append(preview)
    
    return previews


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details"""
    project = ProjectService.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    assets = ProjectService.get_project_assets(db, project)
    return ProjectService.convert_to_response(project, assets)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete project and all associated assets"""
    project = ProjectService.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Delete associated files
    assets = ProjectService.get_project_assets(db, project)
    for asset in assets:
        FileService.delete_file(asset.storage_path)
    
    # Delete project (cascade will handle assets)
    db.delete(project)
    db.commit()
    
    return None

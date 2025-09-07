import logging
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.models.project import Project, ProjectStatus
from app.models.asset import Asset
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.file_service import FileService

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for project operations"""
    
    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate, user: User) -> Project:
        """Create a new project"""
        project = Project(
            name=project_data.name,
            user_id=user.id,
            organization_id=user.organization_id,
            status=ProjectStatus.UPLOADING
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def get_user_projects(
        db: Session, 
        user: User, 
        skip: int = 0, 
        limit: int = 10,
        sort: str = "desc",
        status: Optional[str] = None
    ) -> List[Project]:
        """Get projects for the user's organization with pagination"""
        query = db.query(Project).filter(Project.organization_id == user.organization_id)
        
        if status:
            query = query.filter(Project.status == status)
        
        if sort == "desc":
            query = query.order_by(Project.created_at.desc())
        else:
            query = query.order_by(Project.created_at.asc())
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: str, user: User) -> Optional[Project]:
        """Get project by ID (must belong to the user's organization)"""
        return db.query(Project).filter(
            Project.id == project_id,
            Project.organization_id == user.organization_id
        ).first()
    
    @staticmethod
    def update_project_status(
        db: Session, 
        project: Project, 
        status: ProjectStatus,
        progress: Optional[int] = None
    ) -> Project:
        """Update project status and progress"""
        project.status = status
        if progress is not None:
            # Store progress in a metadata field if needed
            pass
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def get_project_assets(db: Session, project: Project) -> List[Asset]:
        """Get all assets for a project"""
        return db.query(Asset).filter(Asset.project_id == project.id).all()
    
    @staticmethod
    def convert_to_response(project: Project, assets: List[Asset] = None) -> ProjectResponse:
        """Convert project model to response schema"""
        if assets is None:
            assets = project.assets
        
        file_counts = FileService.get_file_counts_by_type(assets)
        
        asset_previews = [
            {
                "id": str(asset.id),
                "filename": asset.original_filename,
                "previewUrl": FileService.get_file_url(asset.storage_path),
                "metadata": asset.ai_metadata or {}
            }
            for asset in assets
        ]

        return ProjectResponse(
            id=str(project.id),
            name=project.name,
            status=project.status.value,
            submitDate=project.created_at,
            fileCounts=file_counts,
            assets=asset_previews
        )
    
    @staticmethod
    def calculate_processing_progress(project: Project) -> int:
        """Calculate processing progress based on project status"""
        status_progress = {
            ProjectStatus.UPLOADING: 10,
            ProjectStatus.PROCESSING: 50,
            ProjectStatus.READY_FOR_REVIEW: 80,
            ProjectStatus.GENERATING: 90,
            ProjectStatus.COMPLETED: 100,
            ProjectStatus.FAILED: 0
        }
        return status_progress.get(project.status, 0)

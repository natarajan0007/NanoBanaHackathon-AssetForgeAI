from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.dependencies import get_admin_user
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.generated_asset import GeneratedAsset
from app.models.asset_format import AssetFormat
from typing import List

router = APIRouter()

@router.get("/user-growth")
async def get_user_growth(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get user growth data for the admin's organization."""
    user_growth = (
        db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count")
        )
        .filter(User.organization_id == admin_user.organization_id)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )
    return [{"date": str(date), "count": count} for date, count in user_growth]

@router.get("/project-status")
async def get_project_status_distribution(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get the distribution of projects by status."""
    status_distribution = (
        db.query(
            Project.status,
            func.count(Project.id).label("count")
        )
        .filter(Project.organization_id == admin_user.organization_id)
        .group_by(Project.status)
        .all()
    )
    return [{"status": status.value, "count": count} for status, count in status_distribution]

@router.get("/generation-by-format")
async def get_generation_by_format(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get the count of generated assets by format."""
    generation_by_format = (
        db.query(
            AssetFormat.name,
            func.count(GeneratedAsset.id).label("count")
        )
        .join(GeneratedAsset, GeneratedAsset.asset_format_id == AssetFormat.id)
        .join(Project, AssetFormat.organization_id == Project.organization_id)
        .filter(Project.organization_id == admin_user.organization_id)
        .group_by(AssetFormat.name)
        .all()
    )
    return [{"name": name, "count": count} for name, count in generation_by_format]

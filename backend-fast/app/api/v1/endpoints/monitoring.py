from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
from typing import Dict, Any

from app.core.database import get_db
from app.core.config import settings
from app.api.dependencies import get_admin_user
from app.models.user import User
from app.services.celery_service import CeleryService

router = APIRouter()


@router.get("/celery/workers", response_model=Dict[str, Any])
async def get_worker_stats(admin_user: User = Depends(get_admin_user)):
    """Get Celery worker statistics (admin only)"""
    try:
        stats = CeleryService.get_worker_stats()
        active_tasks = CeleryService.get_active_tasks()
        
        return {
            "workers": stats,
            "active_tasks": active_tasks,
            "total_workers": len(stats),
            "total_active_tasks": sum(len(tasks) for tasks in active_tasks.values())
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting worker stats: {str(e)}"
        )


@router.get("/celery/task/{task_id}", response_model=Dict[str, Any])
async def get_task_status(
    task_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Get status of a specific Celery task (admin only)"""
    try:
        return CeleryService.get_task_status(task_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting task status: {str(e)}"
        )


@router.post("/celery/task/{task_id}/cancel", response_model=Dict[str, Any])
async def cancel_task(
    task_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Cancel a running Celery task (admin only)"""
    try:
        success = CeleryService.cancel_task(task_id)
        return {
            "task_id": task_id,
            "cancelled": success,
            "message": "Task cancelled successfully" if success else "Failed to cancel task"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling task: {str(e)}"
        )


@router.post("/maintenance/cleanup", response_model=Dict[str, Any])
async def trigger_maintenance(admin_user: User = Depends(get_admin_user)):
    """Trigger maintenance tasks (admin only)"""
    try:
        CeleryService.schedule_maintenance_tasks()
        return {
            "message": "Maintenance tasks scheduled successfully",
            "tasks": ["cleanup_failed_jobs", "cleanup_orphaned_files", "health_check"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling maintenance: {str(e)}"
        )

@router.get("/health-check")
async def get_system_health(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Perform a health check on all system components."""
    
    # Database check
    try:
        db.execute(text('SELECT 1'))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    # Redis check
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        redis_status = "ok"
    except Exception as e:
        redis_status = f"error: {e}"

    # Celery workers check
    try:
        worker_stats = CeleryService.get_worker_stats()
        if worker_stats:
            celery_status = "ok"
            celery_details = f"{len(worker_stats)} workers online"
        else:
            celery_status = "error"
            celery_details = "No workers found"
    except Exception as e:
        celery_status = "error"
        celery_details = str(e)

    return {
        "database": {"status": db_status},
        "redis": {"status": redis_status},
        "celery": {"status": celery_status, "details": celery_details}
    }

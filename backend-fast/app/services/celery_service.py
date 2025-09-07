import logging
from celery.result import AsyncResult
from app.celery_app import celery_app
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CeleryService:
    """Service for managing Celery tasks and monitoring"""
    
    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get status of a Celery task"""
        result = AsyncResult(task_id, app=celery_app)
        
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None,
            'info': result.info,
            'traceback': result.traceback if result.failed() else None
        }
    
    @staticmethod
    def cancel_task(task_id: str) -> bool:
        """Cancel a running task"""
        try:
            celery_app.control.revoke(task_id, terminate=True)
            return True
        except Exception as e:
            print(f"Error canceling task {task_id}: {e}")
            return False
    
    @staticmethod
    def get_active_tasks() -> Dict[str, Any]:
        """Get list of active tasks"""
        try:
            inspect = celery_app.control.inspect()
            active_tasks = inspect.active()
            return active_tasks or {}
        except Exception as e:
            print(f"Error getting active tasks: {e}")
            return {}
    
    @staticmethod
    def get_worker_stats() -> Dict[str, Any]:
        """Get worker statistics"""
        try:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            return stats or {}
        except Exception as e:
            print(f"Error getting worker stats: {e}")
            return {}
    
    @staticmethod
    def purge_queue(queue_name: str) -> int:
        """Purge all tasks from a queue"""
        try:
            return celery_app.control.purge()
        except Exception as e:
            print(f"Error purging queue {queue_name}: {e}")
            return 0
    
    @staticmethod
    def schedule_maintenance_tasks():
        """Schedule periodic maintenance tasks"""
        from app.tasks.maintenance import cleanup_failed_jobs, cleanup_orphaned_files, health_check
        
        # Schedule cleanup tasks
        cleanup_failed_jobs.apply_async(countdown=60)  # Run in 1 minute
        cleanup_orphaned_files.apply_async(countdown=300)  # Run in 5 minutes
        health_check.apply_async(countdown=10)  # Run in 10 seconds

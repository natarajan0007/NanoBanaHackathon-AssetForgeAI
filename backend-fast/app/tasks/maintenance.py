from celery import current_task
from sqlalchemy.orm import sessionmaker
from app.celery_app import celery_app
from app.core.database import engine
from app.models.generation_job import GenerationJob, JobStatus
from app.models.project import Project, ProjectStatus
from app.services.file_service import FileService
import os
import time
from datetime import datetime, timedelta

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(bind=True)
def cleanup_failed_jobs(self):
    """Clean up failed jobs older than 24 hours"""
    db = SessionLocal()
    
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Find failed jobs older than 24 hours
        failed_jobs = db.query(GenerationJob).filter(
            GenerationJob.status == JobStatus.FAILED,
            GenerationJob.created_at < cutoff_time
        ).all()
        
        cleaned_count = 0
        for job in failed_jobs:
            # Clean up any generated assets
            for asset in job.generated_assets:
                FileService.delete_file(asset.storage_path)
            
            # Delete the job (cascade will handle generated assets)
            db.delete(job)
            cleaned_count += 1
        
        db.commit()
        
        return {
            'status': 'completed',
            'cleaned_jobs': cleaned_count
        }
        
    except Exception as e:
        db.rollback()
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise e
        
    finally:
        db.close()


@celery_app.task(bind=True)
def cleanup_orphaned_files(self):
    """Clean up orphaned files in upload directory"""
    try:
        upload_dir = FileService.UPLOAD_DIR
        cleaned_files = []
        
        # Get all files in upload directory
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, upload_dir)
                
                # Check if file is referenced in database
                db = SessionLocal()
                try:
                    from app.models.asset import Asset
                    from app.models.generated_asset import GeneratedAsset
                    
                    asset_exists = db.query(Asset).filter(
                        Asset.storage_path == relative_path
                    ).first()
                    
                    generated_asset_exists = db.query(GeneratedAsset).filter(
                        GeneratedAsset.storage_path == relative_path
                    ).first()
                    
                    # If file is not referenced and older than 1 hour, delete it
                    if not asset_exists and not generated_asset_exists:
                        file_age = time.time() - os.path.getctime(file_path)
                        if file_age > 3600:  # 1 hour
                            os.remove(file_path)
                            cleaned_files.append(relative_path)
                
                finally:
                    db.close()
        
        return {
            'status': 'completed',
            'cleaned_files': len(cleaned_files),
            'files': cleaned_files[:10]  # Return first 10 for logging
        }
        
    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise e


@celery_app.task(bind=True)
def health_check(self):
    """Health check task for monitoring worker status"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        # Test file system access
        test_file = os.path.join(FileService.UPLOAD_DIR, '.health_check')
        with open(test_file, 'w') as f:
            f.write('health_check')
        os.remove(test_file)
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'worker_id': current_task.request.hostname
        }
        
    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise e

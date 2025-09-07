from celery import current_task
from sqlalchemy.orm import sessionmaker
from app.celery_app import celery_app
from app.core.database import engine
from app.models.project import Project, ProjectStatus
from app.models.asset import Asset
from app.services.file_service import FileService
from app.ai.factory import get_ai_provider
from app.core.config import settings
import os
import time
import asyncio
import logging

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_uploaded_assets(self, project_id: str):
    """Background task to process uploaded assets with AI analysis"""
    db = SessionLocal()
    
    try:
        # Get project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception(f"Project {project_id} not found")
        
        # Get assets
        assets = db.query(Asset).filter(Asset.project_id == project_id).all()
        if not assets:
            raise Exception(f"No assets found for project {project_id}")
        
        # Update progress
        current_task.update_state(state='PROGRESS', meta={'progress': 10})
        
        # Initialize AI provider
        ai_provider = get_ai_provider()
        
        total_assets = len(assets)
        processed_assets = 0
        
        for asset in assets:
            # Get full file path
            file_path = os.path.join(settings.UPLOAD_DIR, asset.storage_path)
            
            # Skip PSD files for AI analysis (would need conversion first)
            logger.info(f"Processing asset {asset.id} at path: {file_path}")

            if asset.storage_path.lower().endswith('.psd'):
                asset.ai_metadata = {
                    "detected_elements": ["psd_file"],
                    "analysis_skipped": True,
                    "reason": "PSD files require conversion for AI analysis"
                }
                logger.info("Skipping AI analysis for PSD file.")
            else:
                ai_metadata = {}
                
                # --- Face Detection ---
                try:
                    logger.info(f"Detecting faces for asset {asset.id}...")
                    faces = asyncio.run(ai_provider.detect_faces(file_path))
                    ai_metadata["faces"] = faces
                    logger.info(f"Face detection result for asset {asset.id}: {faces}")
                except Exception as e:
                    logger.error(f"Error during face detection for asset {asset.id}: {e}")
                    ai_metadata["faces"] = []

                # --- Object Detection ---
                try:
                    logger.info(f"Detecting objects for asset {asset.id}...")
                    objects = asyncio.run(ai_provider.detect_objects(file_path))
                    ai_metadata["objects"] = objects
                    logger.info(f"Object detection result for asset {asset.id}: {objects}")
                except Exception as e:
                    logger.error(f"Error during object detection for asset {asset.id}: {e}")
                    ai_metadata["objects"] = []

                # --- NSFW Detection ---
                try:
                    logger.info(f"Detecting NSFW content for asset {asset.id}...")
                    is_nsfw = asyncio.run(ai_provider.detect_nsfw(file_path))
                    ai_metadata["is_nsfw"] = is_nsfw
                    logger.info(f"NSFW detection result for asset {asset.id}: {is_nsfw}")
                except Exception as e:
                    logger.error(f"Error during NSFW detection for asset {asset.id}: {e}")
                    ai_metadata["is_nsfw"] = False
                
                # Compile detected elements for UI
                detected_elements = []
                if ai_metadata.get("faces"):
                    detected_elements.append("faces")
                if ai_metadata.get("objects"):
                    detected_elements.extend([obj.get("label", "object") for obj in ai_metadata["objects"]])
                
                ai_metadata["detected_elements"] = detected_elements
                asset.ai_metadata = ai_metadata
                logger.info(f"Final AI metadata for asset {asset.id}: {ai_metadata}")
            
            processed_assets += 1
            progress = 10 + (processed_assets / total_assets) * 70  # 10-80% for processing
            current_task.update_state(state='PROGRESS', meta={'progress': int(progress)})
            
            # Simulate processing time
            time.sleep(1)
        
        # Save all changes
        db.commit()
        
        # Update project status to ready for review
        project.status = ProjectStatus.READY_FOR_REVIEW
        db.commit()
        
        current_task.update_state(state='SUCCESS', meta={'progress': 100})
        
        return {
            'status': 'completed',
            'processed_assets': processed_assets,
            'total_assets': total_assets
        }
        
    except Exception as e:
        try:
            # Retry with exponential backoff. Max retries: 5.
            # Countdown will be 1, 2, 4, 8, 16 seconds.
            self.retry(exc=e, countdown=2**self.request.retries, max_retries=5)
        except Exception as retry_exc:
            # This is executed when max_retries is exceeded.
            # Update project status to failed
            if 'project' in locals() and project:
                db.rollback()
                project.status = ProjectStatus.FAILED
                db.commit()
            
            # Re-raise a new, simple exception with the stringified original error
            # to ensure it can be serialized by Celery.
            raise Exception(str(e))
        
    finally:
        db.close()
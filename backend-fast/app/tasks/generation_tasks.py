from celery import current_task
from sqlalchemy.orm import sessionmaker
from app.celery_app import celery_app
from app.core.database import engine
from app.models.generation_job import GenerationJob, JobStatus
from app.models.generated_asset import GeneratedAsset
from app.models.asset_format import AssetFormat
from app.models.asset import Asset
from app.models.user import User
from app.services.generation_service import GenerationService
from app.services.file_service import FileService
from app.ai.factory import get_ai_provider
from app.core.config import settings
import os
import time
import logging
import asyncio
from PIL import Image

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_generation_job(self, job_id: str, request_data: dict):
    """Background task to process generation job"""
    db = SessionLocal()
    job = None  # Ensure job is defined in case of early exception
    try:
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            raise Exception(f"Generation job {job_id} not found")

        logger.info(f"Starting generation job {job.id} for project {job.project_id}")

        user = db.query(User).filter(User.id == job.user_id).first()
        if not user:
            raise Exception(f"User {job.user_id} not found for job {job_id}")
        
        GenerationService.update_job_progress(db, job, JobStatus.PROCESSING, 10)
        
        assets = db.query(Asset).filter(Asset.project_id == job.project_id).all()
        if not assets:
            raise Exception("No assets found for project")
        
        format_ids = request_data.get("formatIds", [])
        custom_resizes = request_data.get("customResizes", [])
        prompt = request_data.get("prompt")
        
        formats = []
        if format_ids:
            formats = db.query(AssetFormat).filter(AssetFormat.id.in_(format_ids)).all()
        
        total_operations = len(assets) * (len(formats) + len(custom_resizes))
        completed_operations = 0
        
        for asset in assets:
            source_path = os.path.join(settings.UPLOAD_DIR, asset.storage_path)
            logger.info(f"Processing asset {asset.id} from path: {source_path}")
            
            if asset.storage_path.lower().endswith('.psd'):
                logger.warning(f"Skipping PSD asset {asset.id} as it cannot be resized directly.")
                completed_operations += len(formats) + len(custom_resizes)
                continue
            
            for format_obj in formats:
                logger.info(f"Generating format '{format_obj.name}' ({format_obj.width}x{format_obj.height}) for asset {asset.id}")
                try:
                    resized_path = GenerationService.resize_image(
                        db, user, source_path, 
                        format_obj.width, format_obj.height,
                        asset.ai_metadata, prompt
                    )
                    logger.info(f"Asset {asset.id} resized to '{resized_path}' for format '{format_obj.name}'")
                    
                    generated_asset = GeneratedAsset(
                        job_id=job.id,
                        original_asset_id=asset.id,
                        asset_format_id=format_obj.id,
                        storage_path=os.path.relpath(resized_path, settings.UPLOAD_DIR),
                        file_type=asset.file_type,
                        dimensions={"width": format_obj.width, "height": format_obj.height},
                        is_nsfw=False,
                        manual_edits={"prompt": prompt} if prompt else None
                    )
                    db.add(generated_asset)
                    completed_operations += 1
                except Exception as e:
                    logger.error(f"Error processing format {format_obj.name} for asset {asset.id}: {e}", exc_info=True)
                    completed_operations += 1
            
            for custom_resize in custom_resizes:
                logger.info(f"Generating custom resize {custom_resize['width']}x{custom_resize['height']} for asset {asset.id}")
                try:
                    resized_path = GenerationService.resize_image(
                        db, user, source_path,
                        custom_resize["width"], custom_resize["height"],
                        asset.ai_metadata, prompt
                    )
                    logger.info(f"Asset {asset.id} resized to '{resized_path}' for custom size")

                    generated_asset = GeneratedAsset(
                        job_id=job.id,
                        original_asset_id=asset.id,
                        asset_format_id=None,
                        storage_path=os.path.relpath(resized_path, settings.UPLOAD_DIR),
                        file_type=asset.file_type,
                        dimensions={"width": custom_resize["width"], "height": custom_resize["height"]},
                        is_nsfw=False,
                        manual_edits={"prompt": prompt} if prompt else None
                    )
                    db.add(generated_asset)
                    completed_operations += 1
                except Exception as e:
                    logger.error(f"Error processing custom resize for asset {asset.id}: {e}", exc_info=True)
                    completed_operations += 1

            progress = 10 + (completed_operations / total_operations) * 80 if total_operations > 0 else 90
            current_task.update_state(state='PROGRESS', meta={'progress': int(progress)})

        logger.info(f"Committing {completed_operations} generated assets to the database for job {job.id}")
        db.commit()
        
        GenerationService.update_job_progress(db, job, JobStatus.COMPLETED, 100)
        logger.info(f"Generation job {job.id} completed successfully.")
        
        return {
            'status': 'completed',
            'generated_assets': completed_operations
        }

    except Exception as e:
        logger.error(f"Celery task process_generation_job failed: {e}", exc_info=True)
        try:
            if job:
                db.rollback()
                GenerationService.update_job_progress(db, job, JobStatus.FAILED, 0)
            self.retry(exc=e, countdown=2**self.request.retries, max_retries=5)
        except Exception as retry_exc:
            logger.error(f"Celery task retry failed: {retry_exc}")
            raise Exception(str(e))
    finally:
        db.close()


@celery_app.task(bind=True, acks_late=True)
def process_prompt_edit_job(self, original_asset_id: str, storage_path: str, prompt: str, user_id: str, project_id: str):
    """Background task to process a single prompt-based image edit."""
    db = SessionLocal()
    job = None # Ensure job is defined
    logger.info(f"Starting prompt edit for asset {original_asset_id} with prompt: '{prompt[:80]}...'")
    
    try:
        ai_provider = get_ai_provider()
        source_path = os.path.join(settings.UPLOAD_DIR, storage_path)

        edited_image_path = asyncio.run(ai_provider.edit_image_with_prompt(source_path, prompt))

        with Image.open(edited_image_path) as img:
            new_dimensions = {"width": img.width, "height": img.height}
            file_type = img.format.lower()

        job = GenerationJob(
            project_id=project_id,
            user_id=user_id,
            status=JobStatus.PROCESSING
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        generated_asset = GeneratedAsset(
            job_id=job.id,
            original_asset_id=original_asset_id,
            asset_format_id=None,
            storage_path=os.path.relpath(edited_image_path, settings.UPLOAD_DIR),
            file_type=file_type,
            dimensions=new_dimensions,
            is_nsfw=False,
            manual_edits={"prompt": prompt}
        )
        db.add(generated_asset)
        
        job.status = JobStatus.COMPLETED
        job.progress = 100
        db.commit()
        db.refresh(generated_asset)

        logger.info(f"Successfully created new asset {generated_asset.id} from prompt edit.")
        return {"status": "completed", "new_asset_id": str(generated_asset.id)}

    except Exception as e:
        logger.error(f"Failed to process prompt edit for asset {original_asset_id}: {e}", exc_info=True)
        try:
            if job:
                db.rollback()
                job.status = JobStatus.FAILED
                db.commit()
            self.retry(exc=e, countdown=2**self.request.retries, max_retries=3)
        except Exception as retry_exc:
            logger.error(f"Celery task retry failed: {retry_exc}")
            raise Exception(str(e))
    finally:
        db.close()
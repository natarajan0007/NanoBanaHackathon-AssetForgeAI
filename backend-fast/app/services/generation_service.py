import logging
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
import os
from PIL import Image

from app.models.generation_job import GenerationJob, JobStatus
from app.models.generated_asset import GeneratedAsset
from app.models.asset_format import AssetFormat
from app.models.project import Project
from app.models.asset import Asset
from app.models.user import User
from app.schemas.generation import GenerationRequest, GeneratedAssetResponse, PromptEditRequest
from app.services.file_service import FileService
from app.services.ai_strategy_service import AIStrategyService
from app.core.config import settings
from app.ai.factory import get_ai_provider
import asyncio

logger = logging.getLogger(__name__)

class GenerationService:
    """Service for handling asset generation operations"""
    
    @staticmethod
    def create_generation_job(
        db: Session, 
        request: GenerationRequest, 
        user: User
    ) -> GenerationJob:
        """Create a new generation job"""
        project = db.query(Project).filter(
            Project.id == request.projectId,
            Project.user_id == user.id
        ).first()
        
        if not project:
            raise ValueError("Project not found or access denied")
        
        job = GenerationJob(
            project_id=project.id,
            user_id=user.id,
            status=JobStatus.PENDING
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def dispatch_prompt_edit_task(
        db: Session,
        request: PromptEditRequest,
        user: User
    ):
        """Dispatch a prompt-based editing task to Celery."""
        # 1. Validate the original asset
        original_asset = db.query(Asset).join(Project).filter(
            Asset.id == request.originalAssetId,
            Project.user_id == user.id
        ).first()

        if not original_asset:
            raise ValueError("Original asset not found or you do not have permission to access it.")

        # 2. Import and dispatch the task
        from app.tasks.generation_tasks import process_prompt_edit_job
        
        logger.info(f"Dispatching prompt edit task for asset {request.originalAssetId} with prompt: '{request.prompt[:80]}...'")
        task_result = process_prompt_edit_job.delay(
            str(original_asset.id),
            original_asset.storage_path,
            request.prompt,
            str(user.id),
            str(original_asset.project_id)
        )

        return task_result.id

    @staticmethod
    async def get_prompt_suggestions(db: Session, asset_id: str, user: User) -> List[str]:
        """Generate prompt suggestions for a given asset."""
        logger.info(f"Getting prompt suggestions for asset {asset_id}")
        asset = db.query(Asset).join(Project).filter(
            Asset.id == asset_id,
            Project.user_id == user.id
        ).first()

        if not asset:
            raise ValueError("Asset not found or you do not have permission to access it.")

        if not asset.ai_metadata or "detected_elements" not in asset.ai_metadata:
            logger.warning(f"Asset {asset_id} has no detected elements to generate prompts from.")
            return ["Make the background a solid color", "Add a festive border", "Convert to black and white"]

        detected_elements = asset.ai_metadata["detected_elements"]
        if not detected_elements:
            return ["Make the background a solid color", "Add a festive border", "Convert to black and white"]

        ai_provider = get_ai_provider()
        return await ai_provider.generate_prompt_suggestions(detected_elements)
    
    @staticmethod
    def get_job_by_id(db: Session, job_id: str, user: User) -> Optional[GenerationJob]:
        """Get generation job by ID (user must own the job)"""
        return db.query(GenerationJob).filter(
            GenerationJob.id == job_id,
            GenerationJob.user_id == user.id
        ).first()
    
    @staticmethod
    def update_job_progress(
        db: Session, 
        job: GenerationJob, 
        status: JobStatus, 
        progress: int
    ) -> GenerationJob:
        """Update job status and progress"""
        job.status = status
        job.progress = progress
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def get_job_results(db: Session, job: GenerationJob) -> Dict[str, List[GeneratedAssetResponse]]:
        """Get generation job results grouped by platform"""
        generated_assets = db.query(GeneratedAsset).filter(
            GeneratedAsset.job_id == job.id
        ).all()
        
        results = {}
        for asset in generated_assets:
            platform_name = "Custom"
            if asset.asset_format and asset.asset_format.platform:
                platform_name = asset.asset_format.platform.name
            elif asset.asset_format and asset.asset_format.category:
                platform_name = asset.asset_format.category
            
            if platform_name not in results:
                results[platform_name] = []
            
            asset_response = GenerationService.convert_to_response(asset)
            results[platform_name].append(asset_response)
        return results
    
    @staticmethod
    def convert_to_response(asset: GeneratedAsset) -> GeneratedAssetResponse:
        """Convert generated asset to response format"""
        return GeneratedAssetResponse(
            id=str(asset.id),
            originalAssetId=str(asset.original_asset_id),
            filename=os.path.basename(asset.storage_path),
            assetUrl=FileService.get_file_url(asset.storage_path),
            platformName=asset.asset_format.platform.name if asset.asset_format and asset.asset_format.platform else None,
            formatName=asset.asset_format.name if asset.asset_format else "Custom",
            dimensions=asset.dimensions,
            isNsfw=asset.is_nsfw,
            manualEdits=asset.manual_edits
        )
    
    @staticmethod
    def apply_manual_edits(
        db: Session,
        asset: GeneratedAsset,
        edits: Dict[str, Any]
    ) -> GeneratedAsset:
        """Apply manual edits to a generated asset"""
        asset.manual_edits = edits
        try:
            original_path = os.path.join(settings.UPLOAD_DIR, asset.storage_path)
            with Image.open(original_path) as img:
                edited_img = img.copy()
                if edits.get("crop"):
                    crop_data = edits["crop"]
                    width, height = img.size
                    left = int(crop_data["x"] * width)
                    top = int(crop_data["y"] * height)
                    right = int((crop_data["x"] + crop_data["width"]) * width)
                    bottom = int((crop_data["y"] + crop_data["height"]) * height)
                    edited_img = edited_img.crop((left, top, right, bottom))
                if edits.get("saturation") and edits["saturation"] != 1.0:
                    from PIL import ImageEnhance
                    enhancer = ImageEnhance.Color(edited_img)
                    edited_img = enhancer.enhance(edits["saturation"])
                edited_path = asset.storage_path.replace('.', '_edited.')
                full_edited_path = os.path.join(settings.UPLOAD_DIR, edited_path)
                edited_img.save(full_edited_path)
                asset.storage_path = edited_path
                asset.dimensions = {"width": edited_img.width, "height": edited_img.height}
        except Exception as e:
            print(f"Error applying manual edits: {e}")
        db.commit()
        db.refresh(asset)
        return asset
    
    @staticmethod
    def resize_image(
        db: Session,
        user: User,
        source_path: str, 
        target_width: int, 
        target_height: int,
        ai_metadata: Optional[Dict[str, Any]],
        prompt: Optional[str] = None
    ) -> str:
        """Resize image using the configured AI strategy with a fallback mechanism."""
        
        # Attempt to use the Gemini Image Editor first if enabled
        if settings.USE_GEMINI_IMAGE_EDITOR:
            logger.info("Attempting to resize image with Gemini Image Editor...")
            try:
                ai_provider = get_ai_provider()
                gemini_path = asyncio.run(ai_provider.resize_image_with_gemini(source_path, target_width, target_height, prompt))
                logger.info("Successfully resized with Gemini Image Editor.")
                return gemini_path
            except Exception as e:
                logger.warning(f"Gemini Image Editor failed: {e}. Falling back to local Python (Pillow) implementation.")

        # Fallback to local implementation if Gemini editor is disabled or fails
        logger.info("Using local Python (Pillow) implementation for resizing.")
        try:
            adaptation_strategy = AIStrategyService.get_adaptation_strategy(db, user)
            logger.info(f"Adaptation strategy for user {user.id}: '{adaptation_strategy}'")

            if adaptation_strategy == "crop" and ai_metadata:
                focal_strategy = AIStrategyService.get_focal_point_strategy(db, user)
                logger.info(f"Applying smart crop with focal strategy: '{focal_strategy}'")
                return AIStrategyService.apply_smart_crop(
                    source_path, 
                    target_width, 
                    target_height, 
                    ai_metadata,
                    focal_strategy
                )
            elif adaptation_strategy == "extend":
                logger.info(f"Applying 'extend' strategy for target {target_width}x{target_height}")
                with Image.open(source_path) as img:
                    new_img = Image.new('RGB', (target_width, target_height), (255, 255, 255))
                    x = (target_width - img.width) // 2
                    y = (target_height - img.height) // 2
                    new_img.paste(img, (x, y))
                    output_path = source_path.replace('.', f'_{target_width}x{target_height}_extended.')
                    new_img.save(output_path)
                    logger.info(f"Saved extended image to '{output_path}'")
                    return output_path
            else:
                if adaptation_strategy == "crop" and not ai_metadata:
                    logger.warning("AI metadata not found for smart crop, falling back to center crop.")
                else:
                    logger.info("No specific strategy matched, falling back to center crop.")
                return AIStrategyService._center_crop(source_path, target_width, target_height)
        except Exception as e:
            logger.error(f"Error resizing image '{source_path}' with local implementation: {e}", exc_info=True)
            logger.warning("Falling back to center crop due to error.")
            return AIStrategyService._center_crop(source_path, target_width, target_height)
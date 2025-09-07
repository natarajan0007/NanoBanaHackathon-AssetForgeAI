import logging
from typing import Dict, Any, List
from app.ai.factory import get_ai_provider
from app.models.app_setting import AppSetting
from app.models.user import User
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)


class AIStrategyService:
    """Service for AI-driven image adaptation strategies"""
    
    @staticmethod
    def get_focal_point_strategy(db: Session, user: User) -> str:
        """Get the configured focal point detection strategy for the user's organization"""
        setting = db.query(AppSetting).filter(
            AppSetting.rule_key == "focal_point_logic",
            AppSetting.organization_id == user.organization_id
        ).first()
        
        if setting and setting.rule_value:
            return setting.rule_value.get("logic", "face-centric")
        
        return "face-centric"
    
    @staticmethod
    def get_adaptation_strategy(db: Session, user: User) -> str:
        """Get the configured AI adaptation strategy for the user's organization"""
        setting = db.query(AppSetting).filter(
            AppSetting.rule_key == "ai_adaptation_strategy",
            AppSetting.organization_id == user.organization_id
        ).first()
        
        if setting and setting.rule_value:
            return setting.rule_value.get("strategy", "crop")
        
        return "crop"
    
    @staticmethod
    def apply_smart_crop(
        image_path: str,
        target_width: int,
        target_height: int,
        ai_metadata: Dict[str, Any],
        focal_strategy: str = "face-centric"
    ) -> str:
        """Apply smart cropping based on focal point strategy using pre-existing AI metadata."""
        try:
            logger.info(f"Attempting smart crop with strategy: '{focal_strategy}'")
            if focal_strategy == "face-centric":
                faces = ai_metadata.get("faces", [])
                if faces:
                    logger.info(f"Found {len(faces)} faces. Finding the largest one.")
                    primary_face = max(faces, key=lambda f: f.get("width", 0) * f.get("height", 0))
                    # Center of the face is x + width/2
                    focal_x = primary_face.get("x", 50) + (primary_face.get("width", 0) / 2)
                    focal_y = primary_face.get("y", 50) + (primary_face.get("height", 0) / 2)
                    logger.info(f"Identified primary face as focal point at ({focal_x:.2f}%, {focal_y:.2f}%)")
                    return AIStrategyService._crop_around_point(
                        image_path, target_width, target_height, focal_x, focal_y
                    )
                else:
                    logger.warning("Face-centric strategy chosen, but no faces found in metadata.")
            
            elif focal_strategy == "product-centric":
                objects = ai_metadata.get("objects", [])
                if objects:
                    logger.info(f"Found {len(objects)} objects. Finding the most confident one.")
                    primary_object = max(objects, key=lambda o: o.get("confidence", 0))
                    # Center of the object is x + width/2
                    focal_x = primary_object.get("x", 50) + (primary_object.get("width", 0) / 2)
                    focal_y = primary_object.get("y", 50) + (primary_object.get("height", 0) / 2)
                    logger.info(f"Identified primary object '{primary_object.get('label')}' as focal point at ({focal_x:.2f}%, {focal_y:.2f}%)")
                    return AIStrategyService._crop_around_point(
                        image_path, target_width, target_height, focal_x, focal_y
                    )
                else:
                    logger.warning("Product-centric strategy chosen, but no objects found in metadata.")
            
            # Fallback to center crop if no focal point is found or strategy is different
            logger.warning("No focal point found for smart crop. Falling back to center crop.")
            return AIStrategyService._center_crop(image_path, target_width, target_height)
            
        except Exception as e:
            logger.error(f"Smart crop failed: {e}", exc_info=True)
            return AIStrategyService._center_crop(image_path, target_width, target_height)
    
    @staticmethod
    def _crop_around_point(
        image_path: str,
        target_width: int,
        target_height: int,
        focal_x: float,
        focal_y: float
    ) -> str:
        """Crop image around a specific focal point"""
        from PIL import Image
        
        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                logger.info(f"Cropping around point for image size {img_width}x{img_height}")
                
                # Convert percentage coordinates to pixels
                focal_x_px = int(focal_x * img_width / 100)
                focal_y_px = int(focal_y * img_height / 100)
                logger.info(f"Focal point in pixels: ({focal_x_px}, {focal_y_px})")
                
                # Calculate crop area based on target aspect ratio
                target_aspect_ratio = target_width / target_height
                current_aspect_ratio = img_width / img_height

                if current_aspect_ratio > target_aspect_ratio:
                    # Original is wider than target, so height is the constraint
                    crop_height = img_height
                    crop_width = int(crop_height * target_aspect_ratio)
                else:
                    # Original is taller or same ratio, so width is the constraint
                    crop_width = img_width
                    crop_height = int(crop_width / target_aspect_ratio)

                logger.info(f"Calculated crop box size: {crop_width}x{crop_height}")

                # Center crop area around focal point
                left = max(0, focal_x_px - crop_width // 2)
                top = max(0, focal_y_px - crop_height // 2)
                
                # Ensure the crop box does not go out of bounds
                if left + crop_width > img_width:
                    left = img_width - crop_width
                if top + crop_height > img_height:
                    top = img_height - crop_height
                
                right = left + crop_width
                bottom = top + crop_height
                
                logger.info(f"Final crop coordinates (L,T,R,B): ({left}, {top}, {right}, {bottom})")

                # Crop and resize
                cropped = img.crop((left, top, right, bottom))
                resized = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Save result
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_smart_crop{ext}"
                resized.save(output_path)
                logger.info(f"Saved smart-cropped image to '{output_path}'")
                
                return output_path
                
        except Exception as e:
            logger.error(f"Focal point crop failed: {e}", exc_info=True)
            return AIStrategyService._center_crop(image_path, target_width, target_height)
    
    @staticmethod
    def _center_crop(image_path: str, target_width: int, target_height: int) -> str:
        """Simple center crop as fallback"""
        from PIL import Image
        
        logger.info(f"Performing center crop for target {target_width}x{target_height}")
        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                
                # Calculate crop dimensions
                img_ratio = img_width / img_height
                target_ratio = target_width / target_height
                
                if img_ratio > target_ratio:
                    # Image is wider, crop width
                    new_width = int(img_height * target_ratio)
                    left = (img_width - new_width) // 2
                    cropped = img.crop((left, 0, left + new_width, img_height))
                else:
                    # Image is taller, crop height
                    new_height = int(img_width / target_ratio)
                    top = (img_height - new_height) // 2
                    cropped = img.crop((0, top, img_width, top + new_height))
                
                # Resize to target dimensions
                resized = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Save result
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_center_crop{ext}"
                resized.save(output_path)
                logger.info(f"Saved center-cropped image to '{output_path}'")
                
                return output_path
                
        except Exception as e:
            logger.error(f"Center crop failed: {e}", exc_info=True)
            return image_path

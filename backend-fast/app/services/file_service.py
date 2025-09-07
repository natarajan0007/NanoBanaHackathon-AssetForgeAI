import logging
import os
import uuid
import hashlib
from typing import Tuple, Dict, Any, Optional
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling file operations"""
    
    ALLOWED_MIME_TYPES = {
        "image/jpeg": "jpg",
        "image/png": "png", 
        "image/x-photoshop": "psd",
        "application/photoshop": "psd"
    }
    
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check file type
        if file.content_type not in FileService.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed. Allowed types: {list(FileService.ALLOWED_MIME_TYPES.keys())}"
            )
        
        # Check file size (this is approximate, actual size checked during read)
        if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
    
    @staticmethod
    async def save_file(file: UploadFile, project_id: str) -> Tuple[str, int, str]:
        """Save uploaded file and return storage path, file size, and checksum"""
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIR, "projects", project_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = FileService.ALLOWED_MIME_TYPES[file.content_type]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Read and save file
        content = await file.read()
        file_size = len(content)
        
        # Check actual file size
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size {file_size} exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Calculate checksum
        checksum = hashlib.md5(content).hexdigest()
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return relative path for storage
        storage_path = os.path.join("projects", project_id, unique_filename)
        return storage_path, file_size, checksum
    
    @staticmethod
    def extract_image_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from image file."""
        try:
            full_path = os.path.join(settings.UPLOAD_DIR, file_path)
            
            if file_path.lower().endswith('.psd'):
                # Basic info for PSD files
                return {"width": None, "height": None, "dpi": None}
            
            with Image.open(full_path) as img:
                width, height = img.size
                dpi = None
                
                # Robustly extract and convert DPI info
                if hasattr(img, 'info') and 'dpi' in img.info:
                    dpi_val = img.info['dpi']
                    if isinstance(dpi_val, tuple) and len(dpi_val) > 0:
                        dpi = int(dpi_val[0])
                    elif dpi_val: # Handles int, float, and IFDRational
                        try:
                            dpi = int(dpi_val)
                        except (TypeError, ValueError):
                            print(f"Could not convert DPI value '{dpi_val}' to int.")
                            dpi = None
                
                return {
                    "width": width,
                    "height": height,
                    "dpi": dpi,
                    "format": img.format,
                    "mode": img.mode
                }
                
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return {}
    
    @staticmethod
    def get_file_url(storage_path: str) -> str:
        """Generate URL for accessing file"""
        # In production, this would generate a pre-signed URL for S3
        # For local storage, return a relative path
        return f"/uploads/{storage_path}"
    
    @staticmethod
    def delete_file(storage_path: str) -> bool:
        """Delete file from storage"""
        try:
            full_path = os.path.join(settings.UPLOAD_DIR, storage_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {storage_path}: {e}")
            return False
    
    @staticmethod
    def get_file_counts_by_type(assets: list) -> Dict[str, int]:
        """Count files by type for project summary"""
        counts = {"psd": 0, "jpg": 0, "png": 0}
        
        for asset in assets:
            file_type = asset.file_type.lower()
            if file_type in ["image/jpeg", "jpeg", "jpg"]:
                counts["jpg"] += 1
            elif file_type in ["image/png", "png"]:
                counts["png"] += 1
            elif file_type in ["image/x-photoshop", "application/photoshop", "psd"]:
                counts["psd"] += 1
        
        return counts

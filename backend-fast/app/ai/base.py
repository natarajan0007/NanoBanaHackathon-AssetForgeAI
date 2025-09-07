from abc import ABC, abstractmethod
from typing import Dict, Any, List
from PIL import Image


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def detect_nsfw(self, image_path: str) -> bool:
        """Detect if image contains NSFW content"""
        pass
    
    @abstractmethod
    async def detect_faces(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect faces in image and return bounding boxes"""
        pass
    
    @abstractmethod
    async def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects/products in image"""
        pass
    
    @abstractmethod
    async def extend_background(self, image_path: str, target_width: int, target_height: int) -> str:
        """Extend image background using AI"""
        pass
    
    @abstractmethod
    async def generate_text_overlay(self, prompt: str) -> str:
        """Generate text overlay suggestions"""
        pass

    @abstractmethod
    async def resize_image_with_gemini(self, image_path: str, target_width: int, target_height: int) -> str:
        """Resize image using a generative model"""
        pass

    @abstractmethod
    async def edit_image_with_prompt(self, image_path: str, prompt: str) -> str:
        """Edit image using a text prompt"""
        pass

    @abstractmethod
    async def generate_prompt_suggestions(self, elements: List[str]) -> List[str]:
        """Generate prompt suggestions based on detected elements"""
        pass

import google.generativeai as genai
from google.generativeai import types
from typing import Dict, Any, List
from PIL import Image
import os
import json
import re
import mimetypes
import logging

from .base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    """Google Gemini implementation of AI provider - Compatible with both 1.5 and 2.5 models"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_ANALYSIS_MODEL)
        self.text_model = genai.GenerativeModel(settings.GEMINI_TEXT_MODEL)
    
    def _get_response_text(self, response) -> str:
        """Helper method to safely extract text from Gemini response (works for both 1.5 and 2.5)"""
        try:
            # Try the quick accessor first (works for 1.5 models and simple 2.5 responses)
            return response.text
        except AttributeError:
            # Handle multi-part responses for Gemini 2.5 Pro
            try:
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        # Get the first text part
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                return part.text
                return ""
            except (AttributeError, IndexError):
                return ""
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Helper method to extract JSON from model response"""
        try:
            # Remove markdown code blocks
            clean_text = re.sub(r'```json\s*', '', text)
            clean_text = re.sub(r'```\s*', '', clean_text)
            clean_text = clean_text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # If no JSON found, try to parse the whole response
                return json.loads(clean_text)
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Attempting to parse: {text[:200]}...")
            return {}
    
    async def detect_nsfw(self, image_path: str) -> bool:
        """Detect if image contains NSFW content"""
        try:
            img = Image.open(image_path)
            
            # Use synchronous method instead of async
            response = self.model.generate_content([
                "Analyze this image for NSFW or inappropriate content. Respond with only 'YES' if NSFW/inappropriate or 'NO' if safe. Do not include any other text.",
                img
            ])
            
            print(f"Raw NSFW detection response: {self._get_response_text(response)}")
            result = self._get_response_text(response).strip().upper()
            return "YES" in result or "TRUE" in result
            
        except Exception as e:
            print(f"NSFW detection failed: {e}")
            return False
    
    async def detect_faces(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect faces in image"""
        try:
            img = Image.open(image_path)
            
            prompt = """
            Look at this image and identify any human faces. For each face you find:
            1. Estimate the bounding box as percentages of image dimensions (0-100)
            2. Estimate confidence level (0.0 to 1.0)
            
            Return ONLY a JSON response in this exact format:
            {"faces": [{"x": 25, "y": 30, "width": 20, "height": 25, "confidence": 0.95}]}
            
            If no faces are found, return: {"faces": []}
            """
            
            response = self.model.generate_content([prompt, img])
            
            print(f"Raw face detection response: {self._get_response_text(response)}")
            
            result = self._extract_json_from_response(self._get_response_text(response))
            return result.get("faces", [])
                
        except Exception as e:
            print(f"Face detection failed: {e}")
            return []
    
    async def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects/products in image"""
        try:
            img = Image.open(image_path)
            
            prompt = """
            Analyze this image and identify the main physical objects or products, ignoring any text overlays or backgrounds.
            For each significant object:
            1. Provide a descriptive label
            2. Estimate bounding box as percentages (0-100)
            3. Estimate confidence (0.0 to 1.0)
            
            Return ONLY a JSON response in this exact format:
            {"objects": [{"label": "product_name", "confidence": 0.95, "x": 45, "y": 55, "width": 15, "height": 30}]}
            
            If no clear objects are visible, return: {"objects": []}
            """
            
            response = self.model.generate_content([prompt, img])
            
            print(f"Raw object detection response: {self._get_response_text(response)}")
            
            result = self._extract_json_from_response(self._get_response_text(response))
            return result.get("objects", [])
                
        except Exception as e:
            print(f"Object detection failed: {e}")
            return []
    
    async def extend_background(self, image_path: str, target_width: int, target_height: int) -> str:
        """Extend image background - simplified implementation"""
        try:
            with Image.open(image_path) as img:
                current_width, current_height = img.size
                
                # Don't extend if target is smaller
                if target_width <= current_width and target_height <= current_height:
                    return image_path
                
                # Create new image with target dimensions
                new_img = Image.new('RGB', (target_width, target_height), (255, 255, 255))
                
                # Calculate position to center original image
                x = max(0, (target_width - current_width) // 2)
                y = max(0, (target_height - current_height) // 2)
                
                # Paste original image
                new_img.paste(img, (x, y))
                
                # Save extended image
                base_name, ext = os.path.splitext(image_path)
                output_path = f"{base_name}_extended{ext}"
                new_img.save(output_path)
                
                return output_path
                
        except Exception as e:
            print(f"Background extension failed: {e}")
            return image_path
    
    async def generate_text_overlay(self, prompt: str) -> str:
        """Generate text overlay suggestions"""
        try:
            full_prompt = f"""
            Create compelling marketing text for: {prompt}
            
            Requirements:
            - Keep it concise (under 10 words)
            - Make it impactful and attention-grabbing
            - Suitable for advertising overlay
            - Return only the text, no quotes or additional formatting
            """
            
            response = self.text_model.generate_content(full_prompt)
            
            # Clean the response using the safe text extractor
            result = self._get_response_text(response).strip()
            # Remove quotes if present
            result = result.strip('"\'')
            
            return result if result else "Your Message Here"
            
        except Exception as e:
            print(f"Text generation failed: {e}")
            return "Your Message Here"

    async def resize_image_with_gemini(self, image_path: str, target_width: int, target_height: int, prompt: str = None) -> str:
        """Resize and optionally edit an image using the Gemini 2.5 Flash Image model."""
        logger.info(f"Using Gemini Image Editor ('{settings.GEMINI_IMAGE_EDITOR_MODEL}') for resizing.")
        
        try:
            image_edit_model = genai.GenerativeModel(settings.GEMINI_IMAGE_EDITOR_MODEL)

            source_image = Image.open(image_path)
            
            # Base prompt for resizing
            base_prompt = f"""Using the provided image, resize it to exactly {target_width}x{target_height} pixels.
Preserve the entire original image content by intelligently extending the background or adding padding if necessary.
Do not crop or remove any part of the original image.
The final output must have the exact dimensions {target_width}x{target_height}.
Maintain the original style and lighting."""

            # Add the creative prompt if it exists
            if prompt:
                final_prompt = f"{base_prompt}\n\nAdditionally, apply the following creative edit: {prompt}"
            else:
                final_prompt = base_prompt
            
            contents = [final_prompt, source_image]

            logger.info(f"Sending request to Gemini Image Editor for image {image_path} with target size {target_width}x{target_height} and prompt: '{prompt[:80] if prompt else 'None'}...'")
            response = image_edit_model.generate_content(contents, stream=True)

            for chunk in response:
                if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                    part = chunk.candidates[0].content.parts[0]
                    if part.inline_data and part.inline_data.data:
                        base, orig_ext = os.path.splitext(image_path)
                        # Use the mime type from the response to get the correct extension
                        file_extension = mimetypes.guess_extension(part.inline_data.mime_type) or orig_ext
                        output_path = f"{base}_gemini_edited{file_extension}"
                        
                        with open(output_path, "wb") as f:
                            f.write(part.inline_data.data)
                        
                        logger.info(f"Successfully generated image with Gemini and saved to {output_path}")
                        return output_path
            
            raise Exception("Gemini Image Editor did not return an image.")

        except Exception as e:
            logger.error(f"Gemini Image Editor failed: {e}", exc_info=True)
            raise

    async def edit_image_with_prompt(self, image_path: str, prompt: str) -> str:
        """Edit an image using a text prompt with the Gemini Image Editor model."""
        logger.info(f"Using Gemini Image Editor ('{settings.GEMINI_IMAGE_EDITOR_MODEL}') for prompt-based editing.")
        
        try:
            image_edit_model = genai.GenerativeModel(settings.GEMINI_IMAGE_EDITOR_MODEL)

            source_image = Image.open(image_path)
            
            # The prompt now comes directly from the user
            contents = [prompt, source_image]

            logger.info(f"Sending request to Gemini Image Editor for image {image_path} with prompt: '{prompt[:80]}...'")
            response = image_edit_model.generate_content(contents, stream=True)

            for chunk in response:
                if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                    part = chunk.candidates[0].content.parts[0]
                    if part.inline_data and part.inline_data.data:
                        base, orig_ext = os.path.splitext(image_path)
                        file_extension = mimetypes.guess_extension(part.inline_data.mime_type) or orig_ext
                        output_path = f"{base}_prompt_edited{file_extension}"
                        
                        with open(output_path, "wb") as f:
                            f.write(part.inline_data.data)
                        
                        logger.info(f"Successfully edited image with prompt and saved to {output_path}")
                        return output_path
            
            raise Exception("Gemini Image Editor did not return an image for the prompt-based edit.")

        except Exception as e:
            logger.error(f"Gemini prompt-based edit failed: {e}", exc_info=True)
            raise

    async def generate_prompt_suggestions(self, elements: List[str]) -> List[str]:
        """Generate prompt suggestions based on detected elements."""
        logger.info(f"Generating prompt suggestions for elements: {elements}")
        try:
            elements_str = ", ".join(elements)
            prompt = f"""Based on the following elements detected in an image, generate 3 short, creative editing prompts. The prompts should be things a user might ask for to edit the image. Return ONLY a JSON array of strings.

Detected elements: {elements_str}

Example output:
["Change the {elements[0]} to a different color", "Add a futuristic city background", "Make the lighting more dramatic"]"""

            response = self.text_model.generate_content(prompt)
            response_text = self._get_response_text(response)
            
            # The response might be a markdown code block
            clean_text = re.sub(r'```json\s*', '', response_text)
            clean_text = re.sub(r'```\s*', '', clean_text)
            clean_text = clean_text.strip()

            suggestions = json.loads(clean_text)
            if isinstance(suggestions, list):
                return suggestions
            else:
                logger.warning(f"Could not parse prompt suggestions, received non-list JSON: {suggestions}")
                return []

        except Exception as e:
            logger.error(f"Failed to generate prompt suggestions: {e}", exc_info=True)
            return []
#!/usr/bin/env python3
"""
Google Media Generator for Brand Deconstruction Station
Integrates Google Imagen for images and Google Veo for videos
Handles generation, storage, and retrieval of media files
"""

import os
import json
import base64
import hashlib
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import time
import uuid

# Import Google AI libraries
try:
    from google.cloud import aiplatform
    from vertexai.preview.vision_models import ImageGenerationModel
    import vertexai
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning("Vertex AI SDK not available. Media generation will use mock mode.")

# Import image processing libraries
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import imageio
    MEDIA_LIBS_AVAILABLE = True
except ImportError:
    MEDIA_LIBS_AVAILABLE = False
    logging.warning("PIL/imageio not available. Media processing will be limited.")

from style_modifiers import StyleModifierEngine, StylePreset, MediaType
from image_enhancement import (
    ImageModel, ImagePurpose, AspectRatio,
    SmartModelSelector, EnhancedPromptTemplates,
    PromptEnhancer, ImageGenerationOrchestrator,
    BatchGenerator, PromptCache
)


class GenerationStatus(Enum):
    """Status of media generation job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class MediaGenerationJob:
    """Represents a media generation job"""
    job_id: str
    media_type: MediaType
    prompt: str
    status: GenerationStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None
    progress: int = 0


class GoogleMediaGenerator:
    """
    Handles media generation using Google's Imagen and Veo APIs
    Provides both real and mock generation capabilities
    """

    def __init__(self, google_api_key: Optional[str] = None):
        """
        Initialize the Google Media Generator

        Args:
            google_api_key: Optional - not used for Vertex AI (uses ADC)
        """
        self.mock_mode = False
        self.jobs = {}  # Track generation jobs
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

        # Initialize Vertex AI client
        try:
            aiplatform.init(project=self.project_id, location=self.location)
            logging.info(f"✅ Vertex AI initialized: project={self.project_id}, location={self.location}")
        except Exception as e:
            logging.warning(f"⚠️ Vertex AI initialization failed: {e}")
            logging.warning("📋 Enabling mock mode for media generation")
            self.mock_mode = True

        # Initialize Gemini native client for Nano Banana models
        self.genai_client = None
        try:
            import google.generativeai as genai
            self.genai_client = genai.Client()
            logging.info("✅ Gemini native client initialized (Nano Banana support)")
        except Exception as e:
            logging.warning(f"⚠️ Gemini native client unavailable: {e}")
            logging.info("💡 Install google-generativeai package for Gemini native image generation")

        # Initialize orchestrator for smart model selection
        self.image_orchestrator = ImageGenerationOrchestrator()
        self.style_engine = StyleModifierEngine()
        self.prompt_cache = PromptCache()

        # Test connection if not in mock mode
        if not self.mock_mode:
            try:
                # Quick validation that we can access Imagen
                logging.info("🔍 Validating Imagen API access...")
                # We don't actually call the API here, just verify setup
                logging.info("✅ Google Media Generator ready (Live mode)")
            except Exception as e:
                logging.warning(f"⚠️ API validation warning: {e}")
        else:
            logging.info("🎭 Google Media Generator ready (Mock mode)")

        # Set up storage directories
        self.base_dir = Path(__file__).parent
        self.static_dir = self.base_dir / "static" / "generated"
        self.static_dir.mkdir(parents=True, exist_ok=True)

        # Job tracking
        self.active_jobs: Dict[str, MediaGenerationJob] = {}

        # Veo video operation tracking {job_id: operation_name}
        self.veo_operations: Dict[str, str] = {}

        # Store API key for video/image generation
        self.google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

    async def generate_image(
        self,
        prompt: str,
        style_preset: StylePreset = StylePreset.PHOTOREALISTIC,
        custom_modifiers: Optional[Dict] = None,
        reference_images: Optional[List[str]] = None,
        purpose: ImagePurpose = ImagePurpose.PHOTOREALISTIC,
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
        quality: str = "standard",
        use_smart_selection: bool = True,
        needs_editing: bool = False
    ) -> Dict[str, Any]:
        """
        Generate an image using Google Imagen, Gemini, or mock generation

        Args:
            prompt: Base prompt for image generation
            style_preset: Style to apply
            custom_modifiers: Additional modifiers to apply
            reference_images: Optional reference images for consistency
            purpose: Purpose of the image (affects model selection)
            aspect_ratio: Desired aspect ratio
            quality: Quality level ("ultra", "standard", "fast")
            use_smart_selection: Whether to use smart model selection
            needs_editing: Whether image will need editing capabilities

        Returns:
            Dictionary with image data and metadata
        """
        # Use smart model selection if enabled
        if use_smart_selection:
            # Prepare generation with orchestrator
            generation_config = self.image_orchestrator.prepare_generation(
                prompt=prompt,
                purpose=purpose,
                aspect_ratio=aspect_ratio,
                quality=quality,
                style=style_preset.value if style_preset else None,
                needs_editing=needs_editing
            )

            enhanced_prompt = generation_config["enhanced_prompt"]
            selected_model = generation_config["model"]

            # Check cache for similar prompts
            cached_result = self.prompt_cache.get_cached(enhanced_prompt, selected_model.value)
            if cached_result:
                logging.info(f"Using cached result for similar prompt")
                return json.loads(cached_result)
        else:
            # Traditional enhancement
            enhanced_prompt = self.style_engine.apply_modifiers(
                prompt,
                style_preset,
                MediaType.IMAGE,
                custom_modifiers
            )
            selected_model = ImageModel.IMAGEN_4_STANDARD

        # Create job
        job_id = str(uuid.uuid4())
        job = MediaGenerationJob(
            job_id=job_id,
            media_type=MediaType.IMAGE,
            prompt=enhanced_prompt,
            status=GenerationStatus.PROCESSING,
            created_at=datetime.now(),
            metadata={
                "style_preset": style_preset.value,
                "original_prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "purpose": purpose.value if purpose else "general",
                "aspect_ratio": aspect_ratio.value,
                "quality": quality,
                "model": selected_model.value if use_smart_selection else "default"
            }
        )
        self.active_jobs[job_id] = job

        try:
            if self.mock_mode:
                # Generate mock image
                result = await self._generate_mock_image(enhanced_prompt, style_preset)
            else:
                # Generate real image with selected model
                result = await self._generate_real_image(
                    enhanced_prompt,
                    reference_images,
                    aspect_ratio=aspect_ratio,
                    model=selected_model if use_smart_selection else None
                )

            # Update job
            job.status = GenerationStatus.COMPLETE
            job.completed_at = datetime.now()
            job.media_url = result["url"]
            job.thumbnail_url = result.get("thumbnail_url", result["url"])
            job.progress = 100

            generation_result = {
                "job_id": job_id,
                "status": "complete",
                "image_url": result["url"],
                "image_data": result.get("base64"),
                "metadata": {
                    **job.metadata,
                    "generation_time": (job.completed_at - job.created_at).total_seconds(),
                    "model": result.get("model", "mock"),
                    "actual_model_used": result.get("actual_model", selected_model.value if use_smart_selection else "default")
                }
            }

            # Cache the result if smart selection was used
            if use_smart_selection and not self.mock_mode:
                self.prompt_cache.add_to_cache(
                    enhanced_prompt,
                    selected_model.value,
                    json.dumps(generation_result)
                )

            return generation_result

        except Exception as e:
            # Handle generation failure
            job.status = GenerationStatus.FAILED
            job.error_message = str(e)
            job.progress = 0
            logging.error(f"Image generation failed: {e}")

            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }

    async def generate_video(
        self,
        prompt: str,
        style_preset: StylePreset = StylePreset.CINEMATIC,
        duration: int = 6,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
        shot_number: int = 1,
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a video using Google Veo or mock generation

        Args:
            prompt: Base prompt for video generation
            style_preset: Style to apply
            duration: Video duration in seconds (4, 6, or 8)
            aspect_ratio: "16:9" or "9:16"
            resolution: "720p" or "1080p"
            shot_number: Shot number in sequence
            reference_images: Optional reference images for consistency

        Returns:
            Dictionary with video job information
        """
        # Generate Veo-formatted prompt
        veo_prompt_data = self.style_engine.generate_veo_prompt(
            subject=prompt,
            action="",  # Will be extracted from prompt
            style_preset=style_preset,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            shot_number=shot_number
        )

        # Create job
        job_id = str(uuid.uuid4())
        job = MediaGenerationJob(
            job_id=job_id,
            media_type=MediaType.VIDEO,
            prompt=veo_prompt_data["full_text"],
            status=GenerationStatus.PENDING,
            created_at=datetime.now(),
            metadata={
                "style_preset": style_preset.value,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "shot_number": shot_number,
                "veo_prompt": veo_prompt_data
            }
        )
        self.active_jobs[job_id] = job

        # Start async generation
        asyncio.create_task(self._process_video_generation(job, reference_images))

        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Video generation started",
            "estimated_time": duration * 10,  # Rough estimate
            "poll_url": f"/api/video-status/{job_id}"
        }

    async def _process_video_generation(
        self,
        job: MediaGenerationJob,
        reference_images: Optional[List[str]] = None
    ):
        """
        Process video generation asynchronously

        Args:
            job: The media generation job
            reference_images: Optional reference images
        """
        try:
            job.status = GenerationStatus.PROCESSING

            if self.mock_mode:
                # Generate mock video
                result = await self._generate_mock_video(
                    job.prompt,
                    job.metadata["duration"],
                    job.metadata["aspect_ratio"]
                )

                # Mock mode completes immediately
                job.status = GenerationStatus.COMPLETE
                job.completed_at = datetime.now()
                job.media_url = result["url"]
                job.thumbnail_url = result.get("thumbnail_url")
                job.progress = 100
            else:
                # Generate real video with Google Veo - pass the existing job
                result = await self._generate_real_video(
                    job.prompt,
                    job.metadata,
                    reference_images,
                    existing_job_id=job.job_id  # Use the existing job ID
                )

                # Veo returns job info (video still processing) or error
                if result.get("status") == "processing":
                    # Video generation started, but not complete yet
                    # Job status already set to PROCESSING above
                    # The check_video_status method will poll and update when complete
                    job.metadata["veo_result"] = result
                    logging.info(f"Veo video generation in progress for job {job.job_id}")
                elif "url" in result:
                    # Immediate completion (unlikely with Veo, but handle it)
                    job.status = GenerationStatus.COMPLETE
                    job.completed_at = datetime.now()
                    job.media_url = result["url"]
                    job.thumbnail_url = result.get("thumbnail_url")
                    job.progress = 100
                else:
                    # Error or unexpected result
                    raise Exception(f"Unexpected video generation result: {result}")

        except Exception as e:
            job.status = GenerationStatus.FAILED
            job.error_message = str(e)
            job.progress = 0
            logging.error(f"Video generation failed: {e}")

    async def _generate_mock_image(
        self,
        prompt: str,
        style_preset: StylePreset
    ) -> Dict[str, Any]:
        """
        Generate a mock image for testing

        Args:
            prompt: Enhanced prompt
            style_preset: Style preset used

        Returns:
            Dictionary with mock image data
        """
        if not MEDIA_LIBS_AVAILABLE:
            raise ImportError("PIL not available for mock image generation")

        # Create a stylized mock image based on the preset
        width, height = 1024, 1024

        # Define colors based on style preset
        color_schemes = {
            StylePreset.CYBERPUNK: ((0, 255, 255), (255, 0, 255), (0, 0, 0)),
            StylePreset.VINTAGE: ((139, 69, 19), (255, 228, 196), (245, 222, 179)),
            StylePreset.EDITORIAL: ((255, 255, 255), (200, 200, 200), (50, 50, 50)),
            StylePreset.SATIRICAL: ((255, 0, 0), (255, 255, 0), (0, 0, 255)),
            StylePreset.CINEMATIC: ((0, 128, 128), (255, 140, 0), (25, 25, 25)),
            StylePreset.DOCUMENTARY: ((100, 100, 100), (150, 150, 150), (200, 200, 200)),
            StylePreset.PHOTOREALISTIC: ((150, 150, 150), (200, 200, 200), (100, 100, 100))
        }

        colors = color_schemes.get(style_preset, color_schemes[StylePreset.PHOTOREALISTIC])

        # Create image
        img = Image.new('RGB', (width, height), colors[0])
        draw = ImageDraw.Draw(img)

        # Add some geometric patterns based on style
        for i in range(10):
            x = (i * 100) % width
            y = (i * 150) % height
            size = 50 + (i * 20)
            draw.ellipse([x, y, x + size, y + size], fill=colors[1], outline=colors[2], width=3)

        # Add text overlay
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        except:
            font = ImageFont.load_default()

        text_lines = [
            f"Mock {style_preset.value.upper()} Image",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Prompt: {prompt[:50]}..."
        ]

        y_offset = height - 200
        for line in text_lines:
            draw.text((50, y_offset), line, fill=colors[2], font=font)
            y_offset += 60

        # Apply filter based on style
        if style_preset == StylePreset.VINTAGE:
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
        elif style_preset == StylePreset.CYBERPUNK:
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

        # Save image
        filename = f"mock_image_{uuid.uuid4().hex[:8]}.png"
        filepath = self.static_dir / filename
        img.save(filepath)

        # Convert to base64
        with open(filepath, "rb") as f:
            base64_data = base64.b64encode(f.read()).decode()

        return {
            "url": f"/static/generated/{filename}",
            "base64": f"data:image/png;base64,{base64_data}",
            "model": "mock",
            "width": width,
            "height": height
        }

    async def _generate_with_gemini_native(
        self,
        prompt: str,
        model: ImageModel,
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE
    ) -> Dict[str, Any]:
        """
        Generate image using Gemini native API (Nano Banana)
        
        Args:
            prompt: Enhanced prompt
            model: GEMINI_NATIVE_FLASH or GEMINI_NATIVE_PRO
            aspect_ratio: Desired aspect ratio
        
        Returns:
            Dictionary with image data
        """
        try:
            from google import genai
            from google.genai import types
            
            logging.info(f"🍌 Using Gemini Native API ({model.value}) for image generation")
            
            # Map our aspect ratio enum to string format for Gemini native API
            aspect_ratio_str = aspect_ratio.value  # e.g., "16:9"
            
            # Use the actual model name for Gemini native (strip -native suffix if present)
            model_name = model.value.replace("-native", "")
            
            # Generate image using Gemini native API
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['Image'],  # Only return images
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio_str
                    )
                )
            )
            
            # Extract image from response
            for part in response.parts:
                if part.inline_data is not None:
                    # Get image as PIL Image
                    image = part.as_image()
                    
                    # Save the generated image
                    timestamp = int(time.time())
                    model_suffix = "flash" if "flash" in model.value else "pro"
                    filename = f"gemini_native_{model_suffix}_{timestamp}.png"
                    filepath = self.static_dir / filename
                    
                    image.save(filepath)
                    
                    # Read and encode to base64
                    with open(filepath, "rb") as f:
                        image_bytes = f.read()
                        base64_data = base64.b64encode(image_bytes).decode('utf-8')
                    
                    logging.info(f"✅ Successfully generated image with Gemini Native ({model.value}): {filename}")
                    
                    return {
                        "url": f"/static/generated/{filename}",
                        "base64": f"data:image/png;base64,{base64_data}",
                        "model": model_name,
                        "actual_model": model.value,
                        "aspect_ratio": aspect_ratio_str,
                        "api": "gemini_native"
                    }
            
            raise Exception("No image generated in Gemini native response")
            
        except Exception as e:
            logging.error(f"Gemini native generation failed: {e}, falling back to mock")
            return await self._generate_mock_image(prompt, StylePreset.PHOTOREALISTIC)

    async def _generate_mock_video(
        self,
        prompt: str,
        duration: int,
        aspect_ratio: str
    ) -> Dict[str, Any]:
        """
        Generate a mock video for testing

        Args:
            prompt: Enhanced Veo prompt
            duration: Video duration
            aspect_ratio: Video aspect ratio

        Returns:
            Dictionary with mock video data
        """
        if not MEDIA_LIBS_AVAILABLE:
            raise ImportError("imageio not available for mock video generation")

        # Simulate processing time
        for i in range(5):
            await asyncio.sleep(1)
            if self.active_jobs:
                job_id = list(self.active_jobs.keys())[0]
                if job_id in self.active_jobs:
                    self.active_jobs[job_id].progress = (i + 1) * 20

        # Define dimensions based on aspect ratio
        if aspect_ratio == "16:9":
            width, height = 1920, 1080
        else:  # 9:16
            width, height = 1080, 1920

        # Create a simple animated video
        fps = 24
        frames = []
        total_frames = duration * fps

        for frame_num in range(total_frames):
            # Create frame
            img = Image.new('RGB', (width, height), (0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Animated element
            progress = frame_num / total_frames
            x = int(width * progress)
            y = height // 2
            radius = 50 + int(20 * np.sin(progress * 2 * np.pi * 3))

            # Draw animated circle
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill=(0, 255, int(255 * progress)),
                outline=(255, 255, 255),
                width=2
            )

            # Add text
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except:
                font = ImageFont.load_default()

            draw.text(
                (50, 50),
                f"Mock Veo Video - Frame {frame_num + 1}/{total_frames}",
                fill=(255, 255, 255),
                font=font
            )

            # Convert to numpy array for imageio
            import numpy as np
            frames.append(np.array(img))

        # Save video
        filename = f"mock_video_{uuid.uuid4().hex[:8]}.mp4"
        filepath = self.static_dir / filename

        imageio.mimwrite(filepath, frames, fps=fps)

        # Create thumbnail
        thumbnail = Image.fromarray(frames[len(frames) // 2])
        thumbnail_filename = f"thumb_{filename.replace('.mp4', '.jpg')}"
        thumbnail_path = self.static_dir / thumbnail_filename
        thumbnail.save(thumbnail_path)

        return {
            "url": f"/static/generated/{filename}",
            "thumbnail_url": f"/static/generated/{thumbnail_filename}",
            "model": "mock",
            "duration": duration,
            "fps": fps,
            "resolution": f"{width}x{height}"
        }

    async def _generate_real_image(
        self,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
        model: Optional[ImageModel] = None
    ) -> Dict[str, Any]:
        """
        Generate a real image using Google Imagen or Gemini Flash Image

        Args:
            prompt: Enhanced prompt
            reference_images: Optional reference images
            aspect_ratio: Desired aspect ratio
            model: The model to use (if None, defaults to Imagen 4.0)

        Returns:
            Dictionary with real image data
        """
        try:
            from google import genai
            from google.genai import types

            # Configure API
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                logging.warning("No API key found for image generation")
                return await self._generate_mock_image(prompt, StylePreset.PHOTOREALISTIC)

            # Create client
            client = genai.Client(api_key=api_key)

            # Determine which model to use
            if model is None:
                model = ImageModel.IMAGEN_4_STANDARD

            logging.info(f"Generating image with {model.value}: {prompt[:100]}...")

            # Check if this is a Gemini native model (Nano Banana)
            if model in [ImageModel.GEMINI_NATIVE_FLASH, ImageModel.GEMINI_NATIVE_PRO]:
                if not self.genai_client:
                    logging.warning("Gemini native client not available, falling back to Imagen")
                    model = ImageModel.IMAGEN_4_STANDARD
                else:
                    return await self._generate_with_gemini_native(prompt, model, aspect_ratio)

            # Generate with Gemini Flash Image for editing capabilities
            if model == ImageModel.GEMINI_FLASH_IMAGE:
                # Use Gemini for generation (supports editing and composition)
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=prompt
                )

                # Extract image from response
                for part in response.parts:
                    if part.inline_data is not None:
                        image = part.as_image()

                        # Save the generated image
                        timestamp = int(time.time())
                        filename = f"gemini_{timestamp}.png"
                        filepath = self.static_dir / filename

                        image.save(filepath)

                        # Read and encode to base64
                        with open(filepath, "rb") as f:
                            image_bytes = f.read()
                            base64_data = base64.b64encode(image_bytes).decode('utf-8')

                        logging.info(f"Successfully generated image with Gemini Flash Image: {filename}")

                        return {
                            "url": f"/static/generated/{filename}",
                            "base64": f"data:image/png;base64,{base64_data}",
                            "model": "gemini-2.5-flash-image",
                            "actual_model": model.value
                        }

                raise Exception("No image generated in Gemini response")

            else:
                # Use Imagen models for photorealistic generation
                # Map AspectRatio enum to Imagen's supported values
                aspect_ratio_map = {
                    AspectRatio.SQUARE: "1:1",
                    AspectRatio.LANDSCAPE: "16:9",
                    AspectRatio.PORTRAIT: "9:16",
                    AspectRatio.FOUR_THREE: "4:3",
                    AspectRatio.THREE_FOUR: "3:4",
                    # Imagen doesn't support all ratios, so map to closest
                    AspectRatio.THREE_TWO: "3:2",
                    AspectRatio.TWO_THREE: "2:3",
                    AspectRatio.FOUR_FIVE: "4:5",
                    AspectRatio.FIVE_FOUR: "5:4",
                    AspectRatio.ULTRA_WIDE: "21:9"  # May default to 16:9 if not supported
                }

                mapped_ratio = aspect_ratio_map.get(aspect_ratio, "16:9")

                # Generate image using selected Imagen model
                result = client.models.generate_images(
                    model=model.value,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio=mapped_ratio
                    )
                )

                # Extract generated image
                if result.generated_images:
                    generated_image = result.generated_images[0]

                    # Save the generated image
                    timestamp = int(time.time())
                    filename = f"imagen_{timestamp}.png"
                    filepath = self.static_dir / filename

                    # Write image bytes to file
                    with open(filepath, "wb") as f:
                        f.write(generated_image.image.image_bytes)

                    # Read and encode to base64
                    base64_data = base64.b64encode(generated_image.image.image_bytes).decode('utf-8')

                    logging.info(f"Successfully generated image with {model.value}: {filename}")

                    return {
                        "url": f"/static/generated/{filename}",
                        "base64": f"data:image/png;base64,{base64_data}",
                        "model": model.value,
                        "actual_model": model.value,
                        "aspect_ratio": mapped_ratio
                    }
                else:
                    raise Exception("No images generated in response")

        except ImportError as e:
            logging.error(f"google-genai library not installed: {e}")
            logging.info("Install with: pip install -U google-genai")
            return await self._generate_mock_image(prompt, StylePreset.PHOTOREALISTIC)
        except Exception as e:
            logging.error(f"Imagen generation failed: {e}, falling back to mock generation")
            return await self._generate_mock_image(prompt, StylePreset.PHOTOREALISTIC)

    async def _generate_real_video(
        self,
        prompt: str,
        metadata: Dict,
        reference_images: Optional[List[str]] = None,
        existing_job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a real video using Google Veo API

        Args:
            prompt: Veo-formatted prompt
            metadata: Video metadata
            reference_images: Optional reference images

        Returns:
            Dictionary with real video data
        """
        try:
            from google import genai
            from google.genai import types

            # Configure API
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                logging.warning("No API key found for Veo video generation")
                return await self._generate_mock_video(
                    prompt,
                    metadata["duration"],
                    metadata["aspect_ratio"]
                )

            # Create client
            client = genai.Client(api_key=api_key)

            # Check if Veo models are available
            try:
                models = client.models.list()
                veo_models = [m for m in models if 'veo' in m.name.lower()]

                if veo_models:
                    logging.info(f"Found Veo models: {[m.name for m in veo_models]}")

                    # Use the latest Veo model
                    model_name = "veo-3.1-generate-preview"

                    # Veo parameters per official API documentation
                    # IMPORTANT: 1080p requires 8 seconds duration
                    duration = int(metadata.get("duration", 8))
                    resolution = metadata.get("resolution", "1080p")
                    aspect_ratio = metadata.get("aspect_ratio", "16:9")

                    # Adjust for resolution constraints
                    if resolution == "1080p" and duration != 8:
                        logging.info(f"Adjusting duration from {duration} to 8 seconds for 1080p resolution")
                        duration = 8

                    # Try using the SDK's generate_videos method first
                    try:
                        logging.info(f"Attempting Veo video generation with SDK: {model_name}")

                        # Generate video using SDK
                        operation = client.models.generate_videos(
                            model=model_name,
                            prompt=prompt,
                            config=types.GenerateVideosConfig(
                                duration_seconds=duration,
                                aspect_ratio=aspect_ratio,
                                resolution=resolution
                            )
                        )

                        operation_name = operation.name
                        logging.info(f"Video generation started! Operation: {operation_name}")

                        # Use existing job ID if provided, otherwise create new one
                        job_id = existing_job_id or str(uuid.uuid4())

                        # Store operation for polling
                        self.veo_operations[job_id] = operation_name
                        logging.info(f"Stored Veo operation for job {job_id}: {operation_name}")

                        # Only create job tracking entry if we created a new job_id
                        if not existing_job_id:
                            self.active_jobs[job_id] = MediaGenerationJob(
                                job_id=job_id,
                                media_type=MediaType.VIDEO,
                                prompt=prompt,
                                status=GenerationStatus.PROCESSING,
                                created_at=datetime.now(),
                                metadata={"operation_name": operation_name, **metadata},
                                progress=10
                            )

                        return {
                            "job_id": job_id,
                            "status": "processing",
                            "operation_name": operation_name,
                            "message": "Video generation in progress - poll /api/video-status for updates"
                        }

                    except (AttributeError, Exception) as sdk_error:
                        # Fallback to REST API if SDK method fails
                        logging.info(f"SDK method failed ({sdk_error}), falling back to REST API")
                        import requests

                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:predictLongRunning"

                        headers = {
                            "Content-Type": "application/json",
                            "x-goog-api-key": api_key
                        }

                        body = {
                            "instances": [
                                {
                                    "prompt": prompt
                                }
                            ],
                            "parameters": {
                                "durationSeconds": duration,
                                "aspectRatio": aspect_ratio,
                                "resolution": resolution
                            }
                        }

                        logging.info(f"Attempting Veo video generation with REST API: {model_name}")
                        response = requests.post(url, headers=headers, json=body, timeout=30)

                        if response.status_code == 200:
                            operation = response.json()
                            operation_name = operation.get('name')
                            logging.info(f"Video generation started! Operation: {operation_name}")

                            # Use existing job ID if provided, otherwise create new one
                            job_id = existing_job_id or str(uuid.uuid4())

                            # Store operation for polling
                            self.veo_operations[job_id] = operation_name
                            logging.info(f"Stored Veo operation for job {job_id}: {operation_name}")

                            # Only create job tracking entry if we created a new job_id
                            # (if existing_job_id was passed, the job already exists)
                            if not existing_job_id:
                                self.active_jobs[job_id] = MediaGenerationJob(
                                    job_id=job_id,
                                    media_type=MediaType.VIDEO,
                                    prompt=prompt,
                                    status=GenerationStatus.PROCESSING,
                                    created_at=datetime.now(),
                                    metadata={"operation_name": operation_name, **metadata},
                                    progress=10  # Operation started
                                )
                                logging.info(f"Veo video generation job created: {job_id}")
                            else:
                                logging.info(f"Using existing job {job_id} for Veo operation")

                            logging.info("Video will be available via polling endpoint")

                            # Return job info for client-side polling
                            return {
                                "job_id": job_id,
                                "status": "processing",
                                "operation_name": operation_name,
                                "message": "Video generation in progress - poll /api/video-status for updates"
                            }

                        elif response.status_code == 403:
                            error_data = response.json()
                            error_msg = error_data.get('error', {}).get('message', 'Unknown error')

                            if 'leaked' in error_msg.lower():
                                logging.error("API key issue detected - please use a valid API key")
                            elif 'permission' in error_msg.lower():
                                logging.warning("Veo access not available - may require allowlist")
                            else:
                                logging.error(f"Access denied: {error_msg}")

                        elif response.status_code == 404:
                            logging.warning("Veo model not found - using enhanced mock generation")

                        else:
                            logging.error(f"Veo API error {response.status_code}: {response.text}")

                else:
                    logging.info("No Veo models available - using enhanced mock generation")

            except Exception as e:
                logging.warning(f"Veo availability check failed: {e}")

            # Fall back to enhanced mock generation
            logging.info("Using enhanced mock video generation with cyberpunk styling")
            return await self._generate_mock_video(
                prompt,
                metadata["duration"],
                metadata["aspect_ratio"]
            )

        except ImportError:
            logging.warning("google-genai not installed for video generation")
            return await self._generate_mock_video(
                prompt,
                metadata["duration"],
                metadata["aspect_ratio"]
            )
        except Exception as e:
            logging.error(f"Video generation failed: {e}")
            return await self._generate_mock_video(
                prompt,
                metadata["duration"],
                metadata["aspect_ratio"]
            )

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a generation job

        Args:
            job_id: The job ID to check

        Returns:
            Job status dictionary
        """
        if job_id not in self.active_jobs:
            return {"error": "Job not found"}

        job = self.active_jobs[job_id]

        result = {
            "job_id": job_id,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "media_type": job.media_type.value
        }

        if job.status == GenerationStatus.COMPLETE:
            result.update({
                "media_url": job.media_url,
                "thumbnail_url": job.thumbnail_url,
                "completed_at": job.completed_at.isoformat(),
                "metadata": job.metadata
            })
        elif job.status == GenerationStatus.FAILED:
            result["error"] = job.error_message

        return result

    async def edit_image(
        self,
        image_url: str,
        edit_instruction: str,
        style_preset: StylePreset = StylePreset.PHOTOREALISTIC
    ) -> Dict[str, Any]:
        """
        Edit an existing image using Gemini's mask-free editing capabilities

        Args:
            image_url: URL or path to the image to edit
            edit_instruction: Natural language instruction for editing
            style_preset: Style to apply to the edit

        Returns:
            Dictionary with edited image data
        """
        try:
            from google import genai
            from PIL import Image

            # Configure API
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                return {"error": "No API key found for image editing"}

            # Create client
            client = genai.Client(api_key=api_key)

            # Load the image
            if image_url.startswith("/static/"):
                # Local file
                image_path = self.base_dir / image_url.lstrip("/")
            else:
                # Assume it's a full path
                image_path = Path(image_url)

            if not image_path.exists():
                return {"error": f"Image not found: {image_url}"}

            # Open image with PIL
            input_image = Image.open(image_path)

            # Create enhanced edit instruction
            enhanced_instruction = f"{edit_instruction}. Maintain {style_preset.value} style."

            logging.info(f"Editing image with Gemini: {enhanced_instruction[:100]}...")

            # Edit using Gemini Flash Image
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[enhanced_instruction, input_image]
            )

            # Extract edited image
            for part in response.parts:
                if part.inline_data is not None:
                    edited_image = part.as_image()

                    # Save the edited image
                    timestamp = int(time.time())
                    filename = f"edited_gemini_{timestamp}.png"
                    filepath = self.static_dir / filename

                    edited_image.save(filepath)

                    # Read and encode to base64
                    with open(filepath, "rb") as f:
                        image_bytes = f.read()
                        base64_data = base64.b64encode(image_bytes).decode('utf-8')

                    logging.info(f"Successfully edited image with Gemini: {filename}")

                    return {
                        "status": "complete",
                        "original_url": image_url,
                        "edited_url": f"/static/generated/{filename}",
                        "base64": f"data:image/png;base64,{base64_data}",
                        "model": "gemini-2.5-flash-image",
                        "edit_instruction": edit_instruction
                    }

            return {"error": "No edited image in response"}

        except Exception as e:
            logging.error(f"Image editing failed: {e}")
            return {"error": str(e)}

    async def generate_image_batch(
        self,
        prompts: List[str],
        purpose: ImagePurpose = ImagePurpose.PHOTOREALISTIC,
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
        quality: str = "standard"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images in batch

        Args:
            prompts: List of prompts
            purpose: Purpose of all images
            aspect_ratio: Aspect ratio for all images
            quality: Quality level

        Returns:
            List of generation results
        """
        results = []

        # Process each prompt
        for prompt in prompts[:4]:  # Limit to 4 for safety
            result = await self.generate_image(
                prompt=prompt,
                purpose=purpose,
                aspect_ratio=aspect_ratio,
                quality=quality,
                use_smart_selection=True
            )
            results.append(result)

        return results

    async def check_video_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job and poll Veo operations

        Args:
            job_id: The job ID to check

        Returns:
            Job status dictionary with video data when complete
        """
        try:
            # Check if job exists
            if job_id not in self.active_jobs:
                return {"error": "Job not found", "status": "failed"}

            job = self.active_jobs[job_id]

            # If already complete or failed, return cached status
            if job.status in [GenerationStatus.COMPLETE, GenerationStatus.FAILED]:
                return {
                    "status": job.status.value,
                    "url": job.media_url,
                    "thumbnail_url": job.thumbnail_url,
                    "error": job.error_message,
                    "progress": job.progress
                }

            # If processing, poll the Veo operation
            if job_id in self.veo_operations:
                operation_name = self.veo_operations[job_id]

                logging.info(f"Polling Veo operation for job {job_id}: {operation_name}")

                try:
                    from google import genai
                    from google.genai import types

                    if not self.google_api_key:
                        raise Exception("No API key available for polling")

                    # Create client (official API docs pattern)
                    client = genai.Client(api_key=self.google_api_key)

                    logging.info(f"Fetching operation status from Google...")
                    # Create operation object and get status (correct API pattern)
                    operation_obj = types.GenerateVideosOperation(name=operation_name)
                    operation = client.operations.get(operation_obj)

                    # Check if operation is done
                    if operation.done:
                        logging.info(f"Veo operation complete: {operation_name}")

                        # Extract result from response (official docs)
                        if operation.response and hasattr(operation.response, 'generated_videos') and operation.response.generated_videos:
                            generated_video = operation.response.generated_videos[0]

                            # Download video using client.files.download()
                            video_data = client.files.download(file=generated_video.video)

                            # Save video file
                            timestamp = int(time.time())
                            filename = f"veo_video_{timestamp}.mp4"
                            filepath = self.static_dir / filename

                            with open(filepath, "wb") as f:
                                f.write(video_data)

                            logging.info(f"Video saved: {filename}")

                            # Update job status
                            job.status = GenerationStatus.COMPLETE
                            job.completed_at = datetime.now()
                            job.media_url = f"/static/generated/{filename}"
                            job.progress = 100

                            # Clean up operation tracking
                            del self.veo_operations[job_id]

                            return {
                                "status": "complete",
                                "url": job.media_url,
                                "progress": 100,
                                "model": "veo-3.1"
                            }
                        else:
                            # Operation done but no video
                            raise Exception("Operation completed but no video generated")
                    else:
                        # Still processing - update progress estimate
                        # Veo typically takes 2-5 minutes, estimate based on elapsed time
                        PROGRESS_MIN = 10  # Minimum progress when processing starts
                        PROGRESS_MAX = 90  # Maximum progress before completion
                        VEO_ESTIMATED_TIME = 180  # Estimated time in seconds (3 minutes)
                        elapsed = (datetime.now() - job.created_at).total_seconds()
                        progress_range = PROGRESS_MAX - PROGRESS_MIN
                        estimated_progress = min(int(PROGRESS_MIN + (elapsed / VEO_ESTIMATED_TIME) * progress_range), PROGRESS_MAX)
                        job.progress = estimated_progress

                        logging.info(f"Veo operation still processing: {operation_name}, progress: {estimated_progress}%")

                        return {
                            "status": "processing",
                            "progress": estimated_progress,
                            "message": "Video generation in progress..."
                        }

                except ImportError:
                    logging.error("google-genai not installed for operation polling")
                    job.status = GenerationStatus.FAILED
                    job.error_message = "google-genai library not available"
                    return {"status": "failed", "error": job.error_message}

                except Exception as e:
                    logging.error(f"Failed to poll Veo operation: {e}")
                    # Don't fail immediately - might be transient error
                    return {
                        "status": "processing",
                        "progress": job.progress,
                        "message": f"Polling error (will retry): {str(e)}"
                    }

            # No Veo operation - check if we lost it or it never existed
            logging.warning(f"No Veo operation found for job {job_id}")
            logging.warning(f"Active veo_operations: {list(self.veo_operations.keys())}")

            # Still update progress estimate even without operation tracking
            if job.status == GenerationStatus.PROCESSING:
                elapsed = (datetime.now() - job.created_at).total_seconds()
                estimated_progress = min(int(10 + (elapsed / 180) * 80), 90)
                job.progress = estimated_progress
                logging.info(f"Job {job_id} progress estimate: {estimated_progress}% (elapsed: {int(elapsed)}s)")

            return self.get_job_status(job_id)

        except Exception as e:
            logging.error(f"Error checking video status: {e}")
            return {"status": "failed", "error": str(e)}

    def cleanup_old_media(self, max_age_hours: int = 24):
        """
        Clean up old generated media files

        Args:
            max_age_hours: Maximum age of files to keep
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for filepath in self.static_dir.glob("*"):
            if filepath.is_file():
                file_age = current_time - filepath.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        filepath.unlink()
                        logging.info(f"Deleted old media file: {filepath}")
                    except Exception as e:
                        logging.error(f"Failed to delete {filepath}: {e}")


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    import numpy as np  # For mock video generation

    async def test_generator():
        # Initialize generator
        generator = GoogleMediaGenerator(google_api_key=os.getenv("GOOGLE_API_KEY"))

        # Test image generation
        print("Testing image generation...")
        image_result = await generator.generate_image(
            prompt="A corporate executive in a glass office tower",
            style_preset=StylePreset.SATIRICAL
        )
        print(f"Image result: {image_result['status']}")
        if image_result['status'] == 'complete':
            print(f"Image URL: {image_result['image_url']}")

        # Test video generation
        print("\nTesting video generation...")
        video_result = await generator.generate_video(
            prompt="Corporate lobby with employees walking",
            style_preset=StylePreset.CYBERPUNK,
            duration=6,
            aspect_ratio="16:9"
        )
        print(f"Video job started: {video_result['job_id']}")

        # Wait and check status
        await asyncio.sleep(7)
        status = generator.get_job_status(video_result['job_id'])
        print(f"Video status: {status}")

    # Run the test
    asyncio.run(test_generator())
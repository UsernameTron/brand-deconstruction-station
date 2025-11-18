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
        self.style_engine = StyleModifierEngine()
        
        # Check for Vertex AI availability and credentials
        self.mock_mode = not VERTEX_AI_AVAILABLE
        
        # Set up storage directories
        self.base_dir = Path(__file__).parent
        self.static_dir = self.base_dir / "static" / "generated"
        self.static_dir.mkdir(parents=True, exist_ok=True)

        # Job tracking
        self.active_jobs: Dict[str, MediaGenerationJob] = {}

        # Test Vertex AI configuration if available
        if not self.mock_mode:
            try:
                # Test initialization with project
                project = os.getenv('GOOGLE_CLOUD_PROJECT', 'avatar-449218')
                location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
                vertexai.init(project=project, location=location)
                logging.info(f"Vertex AI configured successfully - Project: {project}")
                self.mock_mode = False
            except Exception as e:
                logging.error(f"Failed to configure Vertex AI: {e}")
                logging.info("Check if GOOGLE_APPLICATION_CREDENTIALS is set or run: gcloud auth application-default login")
                self.mock_mode = True

        if self.mock_mode:
            logging.info("Running in mock mode - will generate placeholder media")

    async def generate_image(
        self,
        prompt: str,
        style_preset: StylePreset = StylePreset.PHOTOREALISTIC,
        custom_modifiers: Optional[Dict] = None,
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate an image using Google Imagen or mock generation

        Args:
            prompt: Base prompt for image generation
            style_preset: Style to apply
            custom_modifiers: Additional modifiers to apply
            reference_images: Optional reference images for consistency

        Returns:
            Dictionary with image data and metadata
        """
        # Apply style modifiers
        enhanced_prompt = self.style_engine.apply_modifiers(
            prompt,
            style_preset,
            MediaType.IMAGE,
            custom_modifiers
        )

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
                "enhanced_prompt": enhanced_prompt
            }
        )
        self.active_jobs[job_id] = job

        try:
            if self.mock_mode:
                # Generate mock image
                result = await self._generate_mock_image(enhanced_prompt, style_preset)
            else:
                # Generate real image with Google Imagen
                result = await self._generate_real_image(enhanced_prompt, reference_images)

            # Update job
            job.status = GenerationStatus.COMPLETE
            job.completed_at = datetime.now()
            job.media_url = result["url"]
            job.thumbnail_url = result.get("thumbnail_url", result["url"])
            job.progress = 100

            return {
                "job_id": job_id,
                "status": "complete",
                "image_url": result["url"],
                "image_data": result.get("base64"),
                "metadata": {
                    **job.metadata,
                    "generation_time": (job.completed_at - job.created_at).total_seconds(),
                    "model": result.get("model", "mock")
                }
            }

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
            else:
                # Generate real video with Google Veo
                result = await self._generate_real_video(
                    job.prompt,
                    job.metadata,
                    reference_images
                )

            # Update job
            job.status = GenerationStatus.COMPLETE
            job.completed_at = datetime.now()
            job.media_url = result["url"]
            job.thumbnail_url = result.get("thumbnail_url")
            job.progress = 100

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
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a real image using Google Vertex AI Imagen

        Args:
            prompt: Enhanced prompt
            reference_images: Optional reference images

        Returns:
            Dictionary with real image data
        """
        try:
            # Get project and location from environment or use defaults
            project = os.getenv('GOOGLE_CLOUD_PROJECT', 'avatar-449218')
            location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

            logging.info(f"Initializing Vertex AI - Project: {project}, Location: {location}")

            # Initialize Vertex AI
            vertexai.init(project=project, location=location)

            # Load the Imagen model
            model = ImageGenerationModel.from_pretrained("imagegeneration@006")

            logging.info(f"Generating real image with Vertex AI Imagen: {prompt[:100]}...")

            # Generate image
            images = model.generate_images(
                prompt=prompt,
                number_of_images=1
            )

            # Save the generated image
            timestamp = int(time.time())
            filename = f"imagen_{timestamp}.png"
            filepath = self.static_dir / filename

            # Save image to file
            images[0].save(location=str(filepath))

            # Read and encode to base64
            with open(filepath, "rb") as f:
                image_bytes = f.read()
                base64_data = base64.b64encode(image_bytes).decode('utf-8')

            logging.info(f"Successfully generated image: {filename}")

            return {
                "url": f"/static/generated/{filename}",
                "base64": f"data:image/png;base64,{base64_data}",
                "model": "imagen-2"
            }

        except ImportError as e:
            logging.error(f"Vertex AI libraries not installed: {e}")
            logging.info("Install with: pip install google-cloud-aiplatform")
            return await self._generate_mock_image(prompt, StylePreset.PHOTOREALISTIC)
        except Exception as e:
            logging.error(f"Vertex AI Imagen failed: {e}, falling back to mock generation")
            return await self._generate_mock_image(prompt, StylePreset.PHOTOREALISTIC)

    async def _generate_real_video(
        self,
        prompt: str,
        metadata: Dict,
        reference_images: Optional[List[str]] = None
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
        # Note: This is a placeholder for when Google Veo API becomes available
        # Veo is currently in limited access

        try:
            # Example of what the API call would look like:
            # response = self.veo_model.generate_video(
            #     prompt=prompt,
            #     duration=metadata["duration"],
            #     aspect_ratio=metadata["aspect_ratio"],
            #     resolution=metadata["resolution"],
            #     reference_images=reference_images
            # )

            # For now, fall back to mock generation
            logging.info("Google Veo not yet available, using enhanced mock generation")
            return await self._generate_mock_video(
                prompt,
                metadata["duration"],
                metadata["aspect_ratio"]
            )

        except Exception as e:
            logging.error(f"Real video generation failed: {e}")
            raise

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

    async def check_video_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job (async wrapper)

        Args:
            job_id: The job ID to check

        Returns:
            Job status dictionary
        """
        # Simply return the synchronous status check
        return self.get_job_status(job_id)

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
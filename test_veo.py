#!/usr/bin/env python3
"""
Test script for Google Veo video generation API
Tests the Veo 3.1 model for generating videos from text prompts
"""

import os
import time
import asyncio
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load API keys from Desktop keys.env if available
desktop_keys = Path.home() / "Desktop" / "keys.env"
if desktop_keys.exists():
    load_dotenv(desktop_keys, override=True)
    print(f"Loaded keys from {desktop_keys}")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def test_veo_setup():
    """Test if Veo API is properly set up"""
    try:
        # Try importing the google-generativeai library
        import google.generativeai as genai
        logger.info("✅ google.generativeai imported successfully")

        # Check for API key
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if api_key:
            logger.info("✅ API key found")
            genai.configure(api_key=api_key)
        else:
            logger.error("❌ No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
            return False

        return True

    except ImportError as e:
        logger.error(f"❌ Failed to import google.generativeai: {e}")
        logger.info("Install with: pip install google-generativeai")
        return False
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

async def test_veo_video_generation():
    """Test generating a video with Veo 3.1"""
    try:
        from google import genai
        from google.genai import types

        # Configure API
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("No API key found")
            return None

        client = genai.Client(api_key=api_key)
        logger.info("API configured successfully")

        # Test prompt for video generation
        prompt = "A cinematic video shot of a futuristic corporate office with holographic displays. The scene is filmed with wide angle lens, featuring neon lighting. The visual style includes high contrast, teal and orange. High quality, 4k, highly detailed."

        logger.info(f"Attempting to generate video with prompt: {prompt[:100]}...")

        # Attempt to generate video using the documented approach
        try:
            # Check available models
            models = client.models.list()
            video_models = [m for m in models if 'veo' in m.name.lower()]

            if video_models:
                logger.info(f"Found video models: {[m.name for m in video_models]}")
            else:
                logger.warning("No video models found in available models")

            # Use the latest Veo model
            model_name = "veo-3.1-generate-preview"
            
            logger.info(f"Generating video with model: {model_name}")

            # Generate video using SDK
            operation = client.models.generate_videos(
                model=model_name,
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    duration_seconds=8,
                    aspect_ratio="16:9",
                    resolution="1080p"
                )
            )

            logger.info(f"✅ Video generation started! Operation: {operation.name}")
            return operation

        except Exception as e:
            logger.error(f"Video generation attempt failed: {e}")
            return None

    except ImportError:
        logger.error("google-genai library not installed. Install with: pip install -U google-genai")
        return None
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return None

async def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("Google Veo Video Generation Test")
    logger.info("=" * 60)

    # Test setup
    if not test_veo_setup():
        logger.error("Setup failed. Please check requirements.")
        return

    # Test video generation
    logger.info("\n" + "=" * 60)
    logger.info("Testing Video Generation")
    logger.info("=" * 60)

    result = await test_veo_video_generation()

    if result:
        logger.info("\n✅ Test completed successfully!")
        logger.info("Video generation operation started")
    else:
        logger.warning("\n⚠️ Video generation not available")
        logger.info("This may be because:")
        logger.info("1. Veo is in limited preview and requires allowlist access")
        logger.info("2. Your API key doesn't have video generation permissions")
        logger.info("3. The feature is not available in your region")

    logger.info("\n" + "=" * 60)
    logger.info("Recommendation:")
    logger.info("For now, continue using mock video generation with enhanced prompts")
    logger.info("Monitor Google AI announcements for Veo general availability")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
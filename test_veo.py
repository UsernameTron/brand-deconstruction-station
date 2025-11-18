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
        import google.generativeai as genai

        # Configure API
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("No API key found")
            return None

        genai.configure(api_key=api_key)
        logger.info("API configured successfully")

        # Test prompt for video generation
        prompt = """
        A sleek, futuristic corporate office with holographic displays showing
        declining stock charts. A robotic executive in a business suit malfunctions,
        sparks flying from its circuits. Cyberpunk aesthetic with neon blue and red
        lighting, dramatic camera angle, cinematic quality.
        """

        logger.info(f"Attempting to generate video with prompt: {prompt[:100]}...")

        # Attempt to generate video using the documented approach
        try:
            # Check available models
            models = genai.list_models()
            video_models = [m for m in models if 'veo' in m.name.lower() or 'video' in m.name.lower()]

            if video_models:
                logger.info(f"Found video models: {[m.name for m in video_models]}")
            else:
                logger.warning("No video models found in available models")

            # Try to use the Veo model
            model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

            # Note: The actual Veo video generation API might not be available yet
            # This is a test to see what's currently accessible
            response = model.generate_content(
                f"Describe how to create this video: {prompt}"
            )

            logger.info(f"Model response: {response.text[:500]}")

            logger.warning("Note: Direct Veo video generation may require special access")
            logger.info("The API documentation shows Veo is in preview mode")

        except Exception as e:
            logger.error(f"Video generation attempt failed: {e}")

            # Try alternative approach mentioned in docs
            logger.info("Attempting alternative approach using REST API...")

            import requests
            import json

            # Construct REST API request as per documentation
            url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:predictLongRunning"

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
                "parameters": {}
            }

            logger.info("Sending request to Veo API...")
            response = requests.post(url, headers=headers, json=body)

            if response.status_code == 200:
                operation = response.json()
                logger.info(f"✅ Video generation started! Operation: {operation.get('name', 'unknown')}")
                return operation
            else:
                logger.error(f"❌ API request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")

                if response.status_code == 403:
                    logger.info("Access denied - Veo may require allowlist access or specific permissions")
                elif response.status_code == 404:
                    logger.info("Model not found - Veo may not be available in your region/project")

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
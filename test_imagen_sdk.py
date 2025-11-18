#!/usr/bin/env python3
"""
Test script for Google Imagen image generation using google-generativeai SDK
Tests the new implementation to ensure prompts are properly handled
"""

import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load API keys from Desktop keys.env if available
desktop_keys = Path.home() / "Desktop" / "keys.env"
if desktop_keys.exists():
    load_dotenv(desktop_keys, override=True)
    print(f"Loaded keys from {desktop_keys}")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def test_imagen_generation():
    """Test generating an image with the new SDK"""
    try:
        from google import genai
        from google.genai import types

        # Configure API
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("No API key found. Set GOOGLE_API_KEY environment variable")
            return False

        # Create client (NEW SDK)
        client = genai.Client(api_key=api_key)
        logger.info("✅ Client created successfully")

        # Test prompt (simple and direct)
        prompt = """A sleek corporate office with floor-to-ceiling windows overlooking a city skyline.
Modern minimalist design with glass desks and chrome accents. Photorealistic, sharp focus,
professional photography, dramatic lighting."""

        logger.info(f"Generating image with prompt: {prompt[:100]}...")

        # Generate image using Imagen 4.0 (stable model)
        result = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9"
            )
        )

        # Check if image was generated
        if result.generated_images:
            generated_image = result.generated_images[0]

            # Save test image
            output_dir = Path(__file__).parent / "static" / "generated"
            output_dir.mkdir(parents=True, exist_ok=True)

            test_filename = "test_imagen_sdk.png"
            test_filepath = output_dir / test_filename

            with open(test_filepath, "wb") as f:
                f.write(generated_image.image.image_bytes)

            logger.info(f"✅ Image generated successfully: {test_filepath}")
            logger.info(f"Image size: {len(generated_image.image.image_bytes)} bytes")
            return True
        else:
            logger.error("❌ No images generated")
            return False

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Install with: pip install -U google-genai")
        return False
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("Google Imagen SDK Test (google-generativeai)")
    logger.info("=" * 60)

    success = await test_imagen_generation()

    if success:
        logger.info("\n✅ Test completed successfully!")
        logger.info("The new SDK properly handles prompts")
    else:
        logger.warning("\n❌ Test failed")
        logger.info("Check error messages above")

    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

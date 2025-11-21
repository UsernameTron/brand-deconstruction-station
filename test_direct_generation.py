#!/usr/bin/env python3
"""
Directly test the media generator to confirm Imagen is working
"""

import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load API keys
desktop_keys = Path.home() / "Desktop" / "keys.env"
if desktop_keys.exists():
    load_dotenv(desktop_keys, override=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

async def test_direct_generation():
    """Test image generation directly with the media generator"""
    try:
        # Import the media generator
        from media_generator import GoogleMediaGenerator
        from style_modifiers import StylePreset

        # Initialize generator (this is how app.py does it)
        google_api_key = os.getenv('GOOGLE_API_KEY')
        logging.info(f"Google API Key present: {bool(google_api_key)}")

        generator = GoogleMediaGenerator(google_api_key=google_api_key)
        logging.info(f"Media generator mock_mode: {generator.mock_mode}")

        if generator.mock_mode:
            logging.warning("⚠️ Generator is in MOCK mode")
            logging.info("Checking why...")

            # Check various conditions
            try:
                from google.cloud import aiplatform
                logging.info("✅ Vertex AI SDK is installed")
            except ImportError:
                logging.warning("❌ Vertex AI SDK not installed")

            project = os.getenv('GOOGLE_CLOUD_PROJECT')
            if project:
                logging.info(f"✅ GOOGLE_CLOUD_PROJECT is set: {project}")
            else:
                logging.warning("❌ GOOGLE_CLOUD_PROJECT not set")
        else:
            logging.info("✅ Generator is in REAL mode")

        # Test image generation
        logging.info("\nGenerating test image...")
        result = await generator.generate_image(
            prompt="A modern corporate executive in a glass office building",
            style_preset=StylePreset.PHOTOREALISTIC,
            use_smart_selection=True
        )

        if result.get('status') == 'complete':
            image_url = result.get('image_url', '')
            model = result.get('metadata', {}).get('model', 'unknown')
            actual_model = result.get('metadata', {}).get('actual_model_used', 'unknown')

            if 'mock' in image_url or model == 'mock':
                logging.warning(f"⚠️ Generated MOCK image: {image_url}")
                return False
            else:
                logging.info(f"✅ Generated REAL image: {image_url}")
                logging.info(f"   Model used: {actual_model}")
                return True
        else:
            logging.error(f"❌ Generation failed: {result}")
            return False

    except Exception as e:
        logging.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    logging.info("=" * 60)
    logging.info("Direct Media Generator Test")
    logging.info("=" * 60)

    success = await test_direct_generation()

    logging.info("\n" + "=" * 60)
    if success:
        logging.info("✅ SUCCESS! The media generator is producing REAL images.")
        logging.info("The Imagen API fix is working correctly!")
        logging.info("\nIf the app still shows mock images, it may be a")
        logging.info("different issue with the web endpoints.")
    else:
        logging.info("❌ The media generator is still using mock images.")
        logging.info("Check the logs above for the reason.")
    logging.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
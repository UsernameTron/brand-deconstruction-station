#!/usr/bin/env python3
"""
Test script to verify Brand Deconstruction Station's image generation
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

async def test_brand_station_imagen():
    """Test the Brand Station's image generation directly"""
    try:
        from app import BrandAnalysisEngine

        # Initialize the Brand Analysis Engine
        engine = BrandAnalysisEngine()

        # Test if media generator is properly configured
        if engine.media_generator.mock_mode:
            logging.warning("⚠️ Media generator is in MOCK mode!")
            logging.info("This means Vertex AI isn't configured or available")
        else:
            logging.info("✅ Media generator is in REAL mode")

        # Generate a test image
        logging.info("\nGenerating test image through Brand Station...")

        # Test image generation
        image_result = await engine.media_generator.generate_image(
            prompt="Corporate executive in a modern office, looking at quarterly reports",
            use_smart_selection=True
        )

        if image_result.get("status") == "complete":
            image_url = image_result.get("image_url", "")

            # Check if it's a mock image
            if "mock" in image_url or image_result.get("metadata", {}).get("model") == "mock":
                logging.warning("⚠️ Generated a MOCK image")
                logging.info("The system fell back to mock generation")
                return False
            else:
                logging.info("✅ Generated a REAL image!")
                logging.info(f"Image URL: {image_url}")
                logging.info(f"Model used: {image_result.get('metadata', {}).get('actual_model_used')}")
                return True
        else:
            logging.error(f"❌ Image generation failed: {image_result}")
            return False

    except Exception as e:
        logging.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    logging.info("=" * 60)
    logging.info("Testing Brand Deconstruction Station Image Generation")
    logging.info("=" * 60)

    success = await test_brand_station_imagen()

    logging.info("\n" + "=" * 60)
    if success:
        logging.info("✅ SUCCESS! Brand Station is generating REAL images.")
        logging.info("The Imagen API fix is working correctly!")
    else:
        logging.info("❌ Brand Station is still using mock images.")
        logging.info("Check the logs above for details.")
    logging.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Test script to verify Imagen API fix
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

async def test_imagen_fix():
    """Test the fixed Imagen implementation"""
    try:
        # Import the fixed media generator
        from media_generator import GoogleMediaGenerator
        from style_modifiers import StylePreset

        # Initialize generator
        generator = GoogleMediaGenerator()

        # Test image generation with the fixed model names
        logging.info("Testing image generation with fixed model names...")
        result = await generator.generate_image(
            prompt="A sleek modern corporate office with glass walls",
            style_preset=StylePreset.PHOTOREALISTIC,
            use_smart_selection=True
        )

        if result.get("status") == "complete":
            logging.info("✅ Image generation successful!")
            logging.info(f"Image URL: {result.get('image_url')}")
            logging.info(f"Model used: {result.get('metadata', {}).get('actual_model_used')}")
            return True
        else:
            logging.error(f"❌ Generation failed: {result}")
            return False

    except Exception as e:
        logging.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_direct_api():
    """Test direct API call with correct model names"""
    try:
        from google import genai
        from google.genai import types

        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logging.error("No API key found")
            return False

        client = genai.Client(api_key=api_key)

        # Test with the correct standard model name
        logging.info("Testing direct API with imagen-4.0-generate-001...")
        result = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt="A modern corporate office",
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9"
            )
        )

        if result.generated_images:
            logging.info("✅ Direct API call successful!")
            return True
        else:
            logging.error("❌ No images generated")
            return False

    except Exception as e:
        logging.error(f"❌ Direct API test failed: {e}")
        return False

async def main():
    logging.info("=" * 60)
    logging.info("Testing Imagen API Fix")
    logging.info("=" * 60)

    # Test direct API first
    logging.info("\n1. Testing direct API with correct model names...")
    direct_success = await test_direct_api()

    # Test the fixed media generator
    logging.info("\n2. Testing media generator with fixed model names...")
    generator_success = await test_imagen_fix()

    # Summary
    logging.info("\n" + "=" * 60)
    if direct_success and generator_success:
        logging.info("✅ ALL TESTS PASSED! The fix is working.")
    elif direct_success and not generator_success:
        logging.info("⚠️ Direct API works but media generator has issues")
    else:
        logging.info("❌ Tests failed - check error messages above")
    logging.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
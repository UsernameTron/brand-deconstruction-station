#!/usr/bin/env python3
"""
Test the full flow: analyze a website and generate images
"""

import requests
import json
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load API keys
desktop_keys = Path.home() / "Desktop" / "keys.env"
if desktop_keys.exists():
    load_dotenv(desktop_keys, override=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def test_full_flow():
    """Test the full analysis and image generation flow"""

    base_url = "http://localhost:3000"

    # First, check if the app is running
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code != 200:
            logging.error("❌ App health check failed")
            return False
    except requests.exceptions.ConnectionError:
        logging.error("❌ App is not running. Please start it with: python3 app.py")
        return False

    # Step 1: Analyze a website
    logging.info("\n1. Starting brand analysis...")
    analysis_data = {
        "url": "https://example.com",  # Using example.com for testing
        "severity": "brutal"
    }

    analysis_response = requests.post(
        f"{base_url}/api/analyze",
        json=analysis_data,
        timeout=30
    )

    if analysis_response.status_code != 200:
        logging.error(f"❌ Analysis failed: {analysis_response.text}")
        return False

    analysis_result = analysis_response.json()
    analysis_id = analysis_result.get('analysis_id')
    logging.info(f"✅ Analysis complete. ID: {analysis_id}")

    # Wait a moment for the analysis to be stored
    time.sleep(1)

    # Step 2: Generate images based on the analysis
    logging.info("\n2. Generating images...")

    # Get the Mirror Vision concepts from the analysis
    mirror_vision_prompts = analysis_result.get('mirror_vision_prompts', [])

    if not mirror_vision_prompts:
        # Create default concepts if none were generated
        concepts = [
            {
                "concept": "Corporate Executive",
                "description": "A corporate executive in a glass office tower looking at charts"
            }
        ]
    else:
        # Use the Mirror Vision prompts as concepts
        concepts = [
            {
                "concept": prompt.get('subject', 'Corporate Scene'),
                "description": prompt.get('scene', prompt.get('subject', 'Corporate office'))
            }
            for prompt in mirror_vision_prompts[:2]  # Use first 2 prompts
        ]

    image_data = {
        "analysis_id": analysis_id,
        "concepts": concepts,
        "style": "photorealistic"
    }

    logging.info(f"Generating images for {len(concepts)} concepts...")

    image_response = requests.post(
        f"{base_url}/api/generate-images",
        json=image_data,
        timeout=60  # Give more time for image generation
    )

    if image_response.status_code != 200:
        logging.error(f"❌ Image generation failed: {image_response.text}")
        return False

    result = image_response.json()

    # Check if it's using mock mode
    mock_mode = result.get('mock_mode', True)
    if mock_mode:
        logging.warning("\n⚠️ Images generated in MOCK mode")
        logging.info("This means Vertex AI is not properly configured")
    else:
        logging.info("\n✅ Images generated in REAL mode using Google Imagen!")

    # Check generated images
    images = result.get('generated_images', [])
    real_images = 0
    mock_images = 0

    for idx, image in enumerate(images, 1):
        if 'error' in image:
            logging.error(f"  Image {idx}: ❌ Error - {image['error']}")
        else:
            image_url = image.get('image_url', '')
            model = image.get('metadata', {}).get('model', 'unknown')
            actual_model = image.get('metadata', {}).get('actual_model_used', 'unknown')

            if 'mock' in image_url.lower() or model == 'mock':
                logging.warning(f"  Image {idx}: ⚠️ Mock image")
                mock_images += 1
            else:
                logging.info(f"  Image {idx}: ✅ Real image - {image_url}")
                logging.info(f"    Model: {actual_model}")
                real_images += 1

    logging.info(f"\nSummary: {real_images} real images, {mock_images} mock images")

    return not mock_mode and real_images > 0

def main():
    logging.info("=" * 60)
    logging.info("Testing Full Brand Analysis + Image Generation Flow")
    logging.info("=" * 60)

    success = test_full_flow()

    logging.info("\n" + "=" * 60)
    if success:
        logging.info("✅ SUCCESS! The app is generating REAL images with Imagen.")
        logging.info("The fix is working correctly!")
    else:
        logging.info("⚠️ The app is still using mock images or encountered errors.")
        logging.info("Check the logs above for details.")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
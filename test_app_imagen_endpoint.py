#!/usr/bin/env python3
"""
Test the Brand Deconstruction Station's image generation endpoint
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

def test_image_endpoint():
    """Test the /api/generate-images endpoint"""

    base_url = "http://localhost:3000"

    # First, check if the app is running
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            logging.info("✅ App is running")
        else:
            logging.error("❌ App health check failed")
            return False
    except requests.exceptions.ConnectionError:
        logging.error("❌ App is not running. Please start it with: python3 app.py")
        return False
    except Exception as e:
        logging.error(f"❌ Failed to connect to app: {e}")
        return False

    # Test image generation
    try:
        # Prepare request data
        data = {
            "analysis_id": "test_" + str(int(time.time())),
            "concepts": [
                {
                    "concept": "Corporate Executive",
                    "description": "A corporate executive looking at quarterly reports in a modern glass office"
                }
            ],
            "style": "photorealistic"
        }

        logging.info("Sending image generation request...")
        logging.info(f"Payload: {json.dumps(data, indent=2)}")

        # Make the request
        response = requests.post(
            f"{base_url}/api/generate-images",
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            logging.info("✅ Request successful")

            # Check if it's using mock mode
            mock_mode = result.get('mock_mode', True)
            if mock_mode:
                logging.warning("⚠️ Images generated in MOCK mode")
            else:
                logging.info("✅ Images generated in REAL mode")

            # Check generated images
            images = result.get('generated_images', [])
            for idx, image in enumerate(images, 1):
                if 'error' in image:
                    logging.error(f"  Image {idx}: ❌ Error - {image['error']}")
                else:
                    image_url = image.get('image_url', '')
                    model = image.get('metadata', {}).get('model', 'unknown')

                    if 'mock' in image_url.lower() or model == 'mock':
                        logging.warning(f"  Image {idx}: ⚠️ Mock image - {image_url}")
                    else:
                        logging.info(f"  Image {idx}: ✅ Real image - {image_url}")
                        logging.info(f"    Model: {model}")

            return not mock_mode and all('error' not in img for img in images)
        else:
            logging.error(f"❌ Request failed with status {response.status_code}")
            logging.error(f"Response: {response.text}")
            return False

    except Exception as e:
        logging.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    logging.info("=" * 60)
    logging.info("Testing Brand Deconstruction Station Image Generation Endpoint")
    logging.info("=" * 60)

    success = test_image_endpoint()

    logging.info("\n" + "=" * 60)
    if success:
        logging.info("✅ SUCCESS! The app is generating REAL images.")
        logging.info("The Imagen API fix is working correctly!")
    else:
        logging.info("⚠️ Check the results above.")
        logging.info("If the app isn't running, start it with: python3 app.py")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
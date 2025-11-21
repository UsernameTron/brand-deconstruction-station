#!/usr/bin/env python3
"""
Debug test for Imagen API to see what error is being thrown
"""

import os
import logging
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

def test_imagen_generation():
    """Test Imagen generation and capture the exact error"""

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logging.error("No GOOGLE_API_KEY found!")
        return

    logging.info(f"API Key present: {bool(api_key)}")

    # Create client
    client = genai.Client(api_key=api_key)

    # List available models first
    logging.info("Listing available models...")
    for model in client.models.list():
        if 'imagen' in model.name.lower():
            logging.info(f"  Found Imagen model: {model.name}")

    # Try each model name
    models_to_test = [
        "imagen-4.0-generate-001",  # What we have in code
        "imagen-4.0-generate-002",  # Alternative
        "imagen-4.0-ultra-generate-001",
        "imagen-4.0-fast-generate-001",
        "imagen-3.0-generate-001",  # Maybe it's Imagen 3?
        "models/imagen-4.0-generate-001",  # With 'models/' prefix
        "models/imagen-3.0-generate-001"
    ]

    prompt = "A beautiful corporate office with glass windows"

    for model_name in models_to_test:
        logging.info(f"\nTesting model: {model_name}")
        try:
            result = client.models.generate_images(
                model=model_name,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9"
                )
            )
            logging.info(f"✅ SUCCESS with {model_name}!")
            if result.generated_images:
                logging.info(f"  Generated {len(result.generated_images)} images")
            return

        except Exception as e:
            logging.error(f"❌ Failed with {model_name}: {e}")
            continue

    logging.error("All models failed!")

if __name__ == "__main__":
    test_imagen_generation()
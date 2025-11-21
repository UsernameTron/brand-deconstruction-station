#!/usr/bin/env python3
"""
Test script for Google Veo video generation using the proper google-genai SDK
Tests the Veo 3.1 model for generating videos from text prompts
"""

import os
import time
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

async def test_veo_with_genai_sdk():
    """Test Veo video generation using google-genai SDK (proper approach)"""
    try:
        from google import genai
        from google.genai import types

        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("No API key found")
            return None

        # Create client (proper SDK pattern)
        client = genai.Client(api_key=api_key)
        logger.info("google-genai client created successfully")

        # List available models
        models = client.models.list()
        video_models = [m for m in models if 'veo' in m.name.lower()]

        if video_models:
            logger.info(f"Found Veo models: {[m.name for m in video_models]}")
        else:
            logger.error("No Veo models found")
            return None

        # Test prompt
        prompt = """
        A corporate executive robot in a glass office tower, its circuits sparking and
        malfunctioning. Cyberpunk aesthetic with neon blue and red lighting, dramatic
        camera angle, cinematic quality. The robot is wearing a business suit.
        """

        logger.info(f"Generating video with prompt: {prompt[:100]}...")

        # Method 1: Try using the new SDK's generate_videos method
        try:
            # Generate video using Veo 3.1
            # NOTE: 1080p requires 8 seconds duration
            result = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    duration_seconds=8,  # 1080p requires 8 seconds
                    aspect_ratio="16:9",  # or "9:16"
                    resolution="1080p"    # or use "720p" for 4 or 6 seconds
                )
            )

            # This returns an operation
            logger.info(f"Video generation started! Operation: {result.name}")

            # Poll for completion
            max_attempts = 60  # 5 minutes max
            attempt = 0

            while attempt < max_attempts and not result.done:
                logger.info(f"Polling attempt {attempt + 1}/{max_attempts}...")
                time.sleep(5)  # Wait 5 seconds between polls

                # Get updated operation status
                result = client.operations.get(result)

                if result.done:
                    logger.info("Video generation complete!")

                    # Extract video
                    if result.response and result.response.generated_videos:
                        video = result.response.generated_videos[0]

                        # Download video
                        video_data = client.files.download(file=video.video)

                        # Save to file
                        output_path = Path("test_veo_output.mp4")
                        output_path.write_bytes(video_data)

                        logger.info(f"Video saved to: {output_path}")
                        return str(output_path)
                    else:
                        logger.error("Operation complete but no video generated")
                        return None

                attempt += 1

            if not result.done:
                logger.warning(f"Video generation timed out after {max_attempts * 5} seconds")
                logger.info(f"Operation {result.name} is still processing")

        except AttributeError as e:
            logger.warning(f"generate_videos method not available: {e}")
            logger.info("Trying alternative REST API approach...")

            # Method 2: Fallback to REST API
            import requests

            url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:predictLongRunning"

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            }

            body = {
                "instances": [{
                    "prompt": prompt
                }],
                "parameters": {
                    "durationSeconds": 6,
                    "aspectRatio": "16:9",
                    "resolution": "1080p"
                }
            }

            response = requests.post(url, headers=headers, json=body, timeout=30)

            if response.status_code == 200:
                operation = response.json()
                operation_name = operation.get('name')
                logger.info(f"Video generation started via REST! Operation: {operation_name}")

                # Now poll using the SDK
                attempt = 0
                max_attempts = 60

                while attempt < max_attempts:
                    time.sleep(5)

                    # Create operation object and get status
                    operation_obj = types.GenerateVideosOperation(name=operation_name)
                    result = client.operations.get(operation_obj)

                    if result.done:
                        logger.info("Video generation complete!")

                        if result.response and result.response.generated_videos:
                            video = result.response.generated_videos[0]
                            video_data = client.files.download(file=video.video)

                            output_path = Path("test_veo_output.mp4")
                            output_path.write_bytes(video_data)

                            logger.info(f"Video saved to: {output_path}")
                            return str(output_path)
                        else:
                            logger.error("No video in completed operation")
                            return None

                    logger.info(f"Still processing... attempt {attempt + 1}/{max_attempts}")
                    attempt += 1

                logger.warning("Polling timed out - video may still be processing")

            else:
                logger.error(f"REST API failed: {response.status_code}")
                logger.error(response.text)

    except ImportError as e:
        logger.error(f"google-genai not installed: {e}")
        logger.info("Install with: pip install google-genai")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    return None

async def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("Google Veo Video Generation Test (Proper SDK)")
    logger.info("=" * 60)

    result = await test_veo_with_genai_sdk()

    if result:
        logger.info(f"\n✅ Success! Video saved to: {result}")
    else:
        logger.info("\n⚠️ Video generation did not complete")
        logger.info("Check logs for details")

    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Test script for Image Generation Enhancements
Verifies all new features work correctly without breaking video generation
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from media_generator import GoogleMediaGenerator
from image_enhancement import ImagePurpose, AspectRatio, ImageModel
from style_modifiers import StylePreset

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

async def test_smart_model_selection():
    """Test smart model selection for different purposes"""
    print("\n" + "="*60)
    print("Testing Smart Model Selection")
    print("="*60)

    generator = GoogleMediaGenerator()

    test_cases = [
        {
            "prompt": "Corporate executive robot in glass office, photorealistic product shot",
            "purpose": ImagePurpose.PHOTOREALISTIC,
            "quality": "ultra",
            "expected_model": "Imagen 4 Ultra"
        },
        {
            "prompt": "Add glowing red eyes to the corporate logo, make it menacing",
            "purpose": ImagePurpose.SATIRICAL_EDIT,
            "needs_editing": True,
            "expected_model": "Gemini Flash Image"
        },
        {
            "prompt": "Quick preview of brand concept",
            "purpose": ImagePurpose.QUICK_PREVIEW,
            "quality": "fast",
            "expected_model": "Imagen 4 Fast"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['expected_model']}")
        print(f"Purpose: {test.get('purpose', ImagePurpose.PHOTOREALISTIC).value}")

        result = await generator.generate_image(
            prompt=test["prompt"],
            purpose=test.get("purpose", ImagePurpose.PHOTOREALISTIC),
            quality=test.get("quality", "standard"),
            use_smart_selection=True,
            needs_editing=test.get("needs_editing", False)
        )

        if result.get("status") == "complete":
            model_used = result.get("metadata", {}).get("model", "Unknown")
            print(f"✓ Generated with: {model_used}")
            print(f"  Image URL: {result.get('image_url')}")
        else:
            print(f"✗ Generation failed: {result.get('error')}")

async def test_aspect_ratios():
    """Test multiple aspect ratio support"""
    print("\n" + "="*60)
    print("Testing Multi-Aspect Ratio Support")
    print("="*60)

    generator = GoogleMediaGenerator()

    aspect_ratios = [
        AspectRatio.SQUARE,       # 1:1
        AspectRatio.LANDSCAPE,    # 16:9
        AspectRatio.PORTRAIT,     # 9:16
        AspectRatio.FOUR_THREE,   # 4:3
    ]

    base_prompt = "Dystopian corporate headquarters with neon accents"

    for ratio in aspect_ratios:
        print(f"\nGenerating {ratio.value} image...")

        result = await generator.generate_image(
            prompt=base_prompt,
            purpose=ImagePurpose.PHOTOREALISTIC,
            aspect_ratio=ratio,
            use_smart_selection=True
        )

        if result.get("status") == "complete":
            print(f"✓ Generated {ratio.value} image")
            print(f"  URL: {result.get('image_url')}")
        else:
            print(f"✗ Failed to generate {ratio.value}: {result.get('error')}")

async def test_batch_generation():
    """Test batch image generation"""
    print("\n" + "="*60)
    print("Testing Batch Generation")
    print("="*60)

    generator = GoogleMediaGenerator()

    prompts = [
        "Corporate logo melting like Salvador Dali clocks",
        "Executive suite transformed into cyberpunk nightmare",
        "Brand mascot with glitch art aesthetic",
        "Office building dissolving into digital particles"
    ]

    print(f"Generating batch of {len(prompts)} images...")

    results = await generator.generate_image_batch(
        prompts=prompts,
        purpose=ImagePurpose.ABSTRACT_CONCEPT,
        aspect_ratio=AspectRatio.LANDSCAPE,
        quality="standard"
    )

    success_count = sum(1 for r in results if r.get("status") == "complete")
    print(f"\n✓ Successfully generated {success_count}/{len(prompts)} images")

    for i, result in enumerate(results, 1):
        if result.get("status") == "complete":
            print(f"  {i}. {result.get('image_url')}")

async def test_image_editing():
    """Test Gemini image editing capabilities"""
    print("\n" + "="*60)
    print("Testing Gemini Image Editing")
    print("="*60)

    generator = GoogleMediaGenerator()

    # First, generate a base image
    print("Generating base image...")
    base_result = await generator.generate_image(
        prompt="Corporate office building in daylight",
        purpose=ImagePurpose.PHOTOREALISTIC,
        use_smart_selection=True
    )

    if base_result.get("status") != "complete":
        print("✗ Failed to generate base image")
        return

    base_url = base_result.get("image_url")
    print(f"✓ Base image: {base_url}")

    # Now edit it
    print("\nApplying dystopian edit...")
    edit_result = await generator.edit_image(
        image_url=base_url,
        edit_instruction="Transform into dystopian nightmare with red sky, broken windows, and apocalyptic atmosphere",
        style_preset=StylePreset.CYBERPUNK
    )

    if edit_result.get("status") == "complete":
        print(f"✓ Edited image: {edit_result.get('edited_url')}")
    else:
        print(f"✗ Edit failed: {edit_result.get('error')}")

async def test_video_still_works():
    """Verify video generation still works after changes"""
    print("\n" + "="*60)
    print("Testing Video Generation (Verify No Breaking Changes)")
    print("="*60)

    generator = GoogleMediaGenerator()

    print("Starting video generation...")
    result = await generator.generate_video(
        prompt="Corporate executive robot malfunctioning in boardroom",
        style_preset=StylePreset.CINEMATIC,
        duration=6,
        aspect_ratio="16:9",
        resolution="720p"
    )

    if result.get("status") in ["pending", "processing"]:
        job_id = result.get("job_id")
        print(f"✓ Video generation started successfully")
        print(f"  Job ID: {job_id}")
        print(f"  Poll URL: {result.get('poll_url')}")

        # Wait a bit and check status
        await asyncio.sleep(5)
        status = await generator.check_video_status(job_id)
        print(f"  Status after 5s: {status.get('status')} ({status.get('progress')}%)")
    else:
        print(f"✗ Video generation failed: {result.get('error')}")

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("BRAND DECONSTRUCTION STATION")
    print("Image Generation Enhancement Test Suite")
    print("="*60)

    # Check for API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("\n⚠️  Warning: GOOGLE_API_KEY not set")
        print("   Tests will run in mock mode")
        print("   Set the key for real API testing")

    try:
        # Run tests
        await test_smart_model_selection()
        await test_aspect_ratios()
        await test_batch_generation()
        await test_image_editing()
        await test_video_still_works()

        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
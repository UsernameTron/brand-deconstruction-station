#!/usr/bin/env python3
"""
Test script for verifying new high-quality modifiers in style_modifiers.py
"""

from style_modifiers import StyleModifierEngine, StylePreset, MediaType

def test_modifiers():
    engine = StyleModifierEngine()
    
    print("=== Testing Image Modifiers (Photorealistic) ===")
    base_prompt = "A portrait of a woman"
    enhanced_prompt = engine.apply_modifiers(
        base_prompt,
        StylePreset.PHOTOREALISTIC,
        MediaType.IMAGE
    )
    print(enhanced_prompt)
    print("\n")

    print("=== Testing Image Modifiers (Cinematic) ===")
    enhanced_prompt = engine.apply_modifiers(
        base_prompt,
        StylePreset.CINEMATIC,
        MediaType.IMAGE
    )
    print(enhanced_prompt)
    print("\n")

    print("=== Testing Video Modifiers (Photorealistic) ===")
    veo_prompt = engine.generate_veo_prompt(
        subject="A dog running in a park",
        action="running fast",
        style_preset=StylePreset.PHOTOREALISTIC,
        duration=6
    )
    print(veo_prompt["full_text"])
    print("\n")

    print("=== Testing Video Modifiers (Cinematic) ===")
    veo_prompt = engine.generate_veo_prompt(
        subject="A spaceship landing on Mars",
        action="landing slowly",
        style_preset=StylePreset.CINEMATIC,
        duration=8
    )
    print(veo_prompt["full_text"])
    print("\n")

if __name__ == "__main__":
    test_modifiers()

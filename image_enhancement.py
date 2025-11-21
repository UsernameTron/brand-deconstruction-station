#!/usr/bin/env python3
"""
Image Generation Enhancement Module for Brand Deconstruction Station
Implements smart model selection, enhanced prompts, and multi-aspect ratio support
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass

class ImageModel(Enum):
    """Available image generation models"""
    # Imagen 4 models
    IMAGEN_4_ULTRA = "imagen-4.0-ultra-generate-001"  # Ultra quality, highest cost
    IMAGEN_4_STANDARD = "imagen-4.0-generate-001"  # Standard quality, balanced
    IMAGEN_4_FAST = "imagen-4.0-fast-generate-001"  # Fast generation, lower quality
    IMAGEN_3 = "imagen-3.0-generate-001"  # Previous gen, stable (if available)

    # Gemini models (Vertex AI)
    GEMINI_FLASH_IMAGE = "gemini-2.5-flash-image"  # Best for editing and flexibility
    GEMINI_PRO_VISION = "gemini-2.0-pro-vision"  # Alternative vision model
    
    # Gemini Native API models (Nano Banana 🍌)
    GEMINI_NATIVE_FLASH = "gemini-2.5-flash-image-native"  # Fast native generation, 1024px
    GEMINI_NATIVE_PRO = "gemini-3-pro-image-preview"  # 4K professional with grounding

class ImagePurpose(Enum):
    """Purpose of image generation to guide model selection"""
    PHOTOREALISTIC = "photorealistic"  # Ultra-realistic brand mockups
    SATIRICAL_EDIT = "satirical_edit"  # Editing existing images
    COMPOSITE = "composite"  # Combining multiple elements
    LOGO_MOCKUP = "logo_mockup"  # Product/logo placement
    ABSTRACT_CONCEPT = "abstract_concept"  # Conceptual visualization
    TEXT_HEAVY = "text_heavy"  # Images with text overlay
    QUICK_PREVIEW = "quick_preview"  # Fast generation for previews

class AspectRatio(Enum):
    """Supported aspect ratios"""
    SQUARE = "1:1"  # Social media posts
    LANDSCAPE = "16:9"  # Presentations, YouTube
    PORTRAIT = "9:16"  # Stories, mobile
    FOUR_THREE = "4:3"  # Traditional photos
    THREE_TWO = "3:2"  # Classic photo ratio
    ULTRA_WIDE = "21:9"  # Cinematic banners
    THREE_FOUR = "3:4"  # Portrait orientation
    FOUR_FIVE = "4:5"  # Instagram portrait
    FIVE_FOUR = "5:4"  # Medium format
    TWO_THREE = "2:3"  # Vertical classic

@dataclass
class ImageGenerationConfig:
    """Configuration for image generation"""
    model: ImageModel
    purpose: ImagePurpose
    aspect_ratio: AspectRatio
    quality: str  # "ultra", "standard", "fast"
    enable_editing: bool
    batch_size: int
    use_cache: bool
    style_consistency: Optional[str] = None
    reference_style: Optional[str] = None


class SmartModelSelector:
    """Intelligently selects the best model for image generation"""

    def __init__(self):
        self.model_capabilities = {
            ImageModel.IMAGEN_4_ULTRA: {
                "strengths": ["photorealistic", "sharp_clarity", "product_shots"],
                "latency": "high",
                "cost": "high",
                "supports_editing": False
            },
            ImageModel.IMAGEN_4_STANDARD: {
                "strengths": ["balanced_quality", "good_speed"],
                "latency": "medium",
                "cost": "medium",
                "supports_editing": False
            },
            ImageModel.IMAGEN_4_FAST: {
                "strengths": ["quick_generation", "previews"],
                "latency": "low",
                "cost": "low",
                "supports_editing": False
            },
            ImageModel.GEMINI_FLASH_IMAGE: {
                "strengths": ["editing", "flexibility", "composition", "iterative"],
                "latency": "medium",
                "cost": "token_based",
                "supports_editing": True
            },
            ImageModel.GEMINI_NATIVE_FLASH: {
                "strengths": ["speed", "efficiency", "low_latency", "quick_generation"],
                "latency": "low",
                "cost": "token_based",
                "supports_editing": False,
                "resolution": "1024px"
            },
            ImageModel.GEMINI_NATIVE_PRO: {
                "strengths": ["4k_output", "grounding", "thinking_mode", "text_rendering", "professional_quality"],
                "latency": "high",
                "cost": "high",
                "supports_editing": False,
                "resolution": "4k"
            }
        }

    def select_model(
        self,
        purpose: ImagePurpose,
        quality_preference: str = "standard",
        needs_editing: bool = False,
        speed_priority: bool = False
    ) -> ImageModel:
        """
        Select the optimal model based on requirements

        Args:
            purpose: The purpose of image generation
            quality_preference: "ultra", "standard", or "fast"
            needs_editing: Whether editing capabilities are needed
            speed_priority: Whether speed is more important than quality

        Returns:
            The selected ImageModel
        """
        # If editing is needed, use Gemini
        if needs_editing or purpose == ImagePurpose.SATIRICAL_EDIT:
            logging.info("Selected Gemini Flash Image for editing capabilities")
            return ImageModel.GEMINI_FLASH_IMAGE

        # For composite or complex scenes, use Gemini
        if purpose in [ImagePurpose.COMPOSITE, ImagePurpose.ABSTRACT_CONCEPT]:
            logging.info("Selected Gemini Flash Image for composition flexibility")
            return ImageModel.GEMINI_FLASH_IMAGE

        # For photorealistic needs, use Imagen or Gemini Native
        if purpose in [ImagePurpose.PHOTOREALISTIC, ImagePurpose.LOGO_MOCKUP]:
            if quality_preference == "ultra":
                # Use Gemini Native Pro for 4K ultra quality
                logging.info("Selected Gemini Native Pro for 4K maximum quality")
                return ImageModel.GEMINI_NATIVE_PRO
            elif speed_priority:
                # Use Gemini Native Flash for fastest generation
                logging.info("Selected Gemini Native Flash for quick generation")
                return ImageModel.GEMINI_NATIVE_FLASH
            else:
                logging.info("Selected Imagen 4 Standard for balanced performance")
                return ImageModel.IMAGEN_4_STANDARD

        # For text-heavy images, use Gemini Native Pro (best text rendering)
        if purpose == ImagePurpose.TEXT_HEAVY:
            logging.info("Selected Gemini Native Pro for advanced text rendering")
            return ImageModel.GEMINI_NATIVE_PRO

        # For quick previews, use Gemini Native Flash (fastest)
        if purpose == ImagePurpose.QUICK_PREVIEW or speed_priority:
            logging.info("Selected Gemini Native Flash for preview generation")
            return ImageModel.GEMINI_NATIVE_FLASH

        # Default to standard Imagen
        logging.info("Selected Imagen 4 Standard as default")
        return ImageModel.IMAGEN_4_STANDARD


class EnhancedPromptTemplates:
    """Templates for generating high-quality prompts"""

    @staticmethod
    def photorealistic_scene(
        subject: str,
        action: str,
        environment: str,
        lighting: str,
        mood: str,
        camera_specs: str,
        key_details: str,
        aspect_ratio: AspectRatio
    ) -> str:
        """
        Generate a photorealistic scene prompt

        Example output:
        "A photorealistic wide shot of a corporate executive robot, malfunctioning
        with sparks flying, set in a glass-walled boardroom. The scene is illuminated
        by harsh fluorescent lighting, creating a sterile corporate atmosphere.
        Captured with a 24mm wide-angle lens, emphasizing the isolation and scale.
        16:9 cinematic format."
        """
        return f"""A photorealistic {camera_specs} of {subject}, {action}, set in {environment}.
The scene is illuminated by {lighting}, creating a {mood} atmosphere.
Captured with professional photography techniques, emphasizing {key_details}.
{aspect_ratio.value} format."""

    @staticmethod
    def brand_satire(
        brand_element: str,
        satirical_twist: str,
        visual_metaphor: str,
        style_modifier: str,
        aspect_ratio: AspectRatio
    ) -> str:
        """
        Generate a satirical brand deconstruction prompt

        Example output:
        "Corporate logo melting like Salvador Dali's clocks, representing the
        dissolution of brand integrity. Hyper-realistic rendering with cyberpunk
        neon accents. Dark humor aesthetic. 16:9 format."
        """
        return f"""{brand_element} {satirical_twist}, representing {visual_metaphor}.
{style_modifier} aesthetic with sharp social commentary undertones.
Professional product photography quality with subversive elements.
{aspect_ratio.value} format."""

    @staticmethod
    def product_mockup(
        product: str,
        setting: str,
        lighting_setup: str,
        surface: str,
        angle: str,
        brand_elements: str,
        aspect_ratio: AspectRatio
    ) -> str:
        """
        Generate a product mockup prompt
        """
        return f"""Professional product photography of {product} placed on {surface} in {setting}.
Shot from {angle} with {lighting_setup} lighting setup.
{brand_elements} visible but naturally integrated.
Clean, minimalist composition with perfect shadows and reflections.
{aspect_ratio.value} format."""

    @staticmethod
    def editorial_style(
        subject: str,
        narrative: str,
        composition: str,
        color_palette: str,
        typography_note: str,
        aspect_ratio: AspectRatio
    ) -> str:
        """
        Generate an editorial/magazine style prompt
        """
        return f"""Editorial photography style: {subject} {narrative}.
{composition} composition with {color_palette} color grading.
Magazine-quality layout with space for {typography_note}.
Professional retouching, high-end fashion magazine aesthetic.
{aspect_ratio.value} format."""

    @staticmethod
    def dystopian_corporate(
        corporate_element: str,
        dystopian_twist: str,
        atmosphere: str,
        visual_style: str,
        aspect_ratio: AspectRatio
    ) -> str:
        """
        Generate a dystopian corporate visualization
        """
        return f"""{corporate_element} transformed into {dystopian_twist}.
{atmosphere} atmosphere with {visual_style} visual treatment.
Blade Runner meets corporate nightmare, high contrast,
dramatic shadows, unsettling corporate symbolism.
{aspect_ratio.value} format."""


class PromptEnhancer:
    """Enhances prompts with additional modifiers and refinements"""

    def __init__(self):
        self.style_modifiers = {
            "cyberpunk": "neon-lit, holographic overlays, tech-noir aesthetic, cyan and magenta accents",
            "corporate_satire": "subversive humor, uncanny valley effect, sterile corporate environment",
            "glitch_art": "digital artifacts, data corruption aesthetic, RGB channel separation",
            "brutalist": "concrete textures, imposing architecture, harsh geometric forms",
            "vaporwave": "retro-futuristic, pastel gradients, 80s nostalgia with modern critique"
        }

        self.quality_boosters = [
            "ultra-high resolution",
            "professional photography",
            "award-winning composition",
            "perfect lighting",
            "sharp focus with subtle depth of field",
            "cinematic color grading"
        ]

    def enhance_prompt(
        self,
        base_prompt: str,
        style: Optional[str] = None,
        add_quality_boosters: bool = True,
        model: Optional[ImageModel] = None
    ) -> str:
        """
        Enhance a prompt with style modifiers and quality boosters

        Args:
            base_prompt: The base prompt to enhance
            style: Optional style to apply
            add_quality_boosters: Whether to add quality enhancement terms
            model: The model being used (affects enhancement strategy)

        Returns:
            Enhanced prompt string
        """
        enhanced = base_prompt

        # Add style modifiers
        if style and style in self.style_modifiers:
            enhanced = f"{enhanced} {self.style_modifiers[style]}"

        # Add quality boosters for Imagen models
        if add_quality_boosters and model and "imagen" in model.value.lower():
            quality_terms = ", ".join(self.quality_boosters[:3])
            enhanced = f"{enhanced}, {quality_terms}"

        # Add Gemini-specific enhancements
        if model == ImageModel.GEMINI_FLASH_IMAGE:
            enhanced = f"{enhanced}. Please ensure high visual quality and artistic composition."

        return enhanced


class ImageGenerationOrchestrator:
    """Orchestrates the entire image generation process"""

    def __init__(self):
        self.model_selector = SmartModelSelector()
        self.prompt_enhancer = PromptEnhancer()
        self.prompt_templates = EnhancedPromptTemplates()

    def prepare_generation(
        self,
        prompt: str,
        purpose: ImagePurpose,
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
        quality: str = "standard",
        style: Optional[str] = None,
        needs_editing: bool = False
    ) -> Dict[str, Any]:
        """
        Prepare everything needed for image generation

        Returns:
            Dictionary with model, enhanced prompt, and configuration
        """
        # Select the best model
        model = self.model_selector.select_model(
            purpose=purpose,
            quality_preference=quality,
            needs_editing=needs_editing,
            speed_priority=(quality == "fast")
        )

        # Enhance the prompt
        enhanced_prompt = self.prompt_enhancer.enhance_prompt(
            base_prompt=prompt,
            style=style,
            add_quality_boosters=(quality != "fast"),
            model=model
        )

        # Create configuration
        config = ImageGenerationConfig(
            model=model,
            purpose=purpose,
            aspect_ratio=aspect_ratio,
            quality=quality,
            enable_editing=needs_editing,
            batch_size=1,
            use_cache=True,
            style_consistency=style
        )

        return {
            "model": model,
            "enhanced_prompt": enhanced_prompt,
            "config": config,
            "aspect_ratio": aspect_ratio.value,
            "original_prompt": prompt
        }


# Utility functions for batch generation and caching
class BatchGenerator:
    """Handles batch generation of multiple images"""

    @staticmethod
    async def generate_batch(
        prompts: List[str],
        model: ImageModel,
        aspect_ratio: AspectRatio,
        max_parallel: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images in parallel

        Args:
            prompts: List of prompts to generate
            model: Model to use
            aspect_ratio: Aspect ratio for all images
            max_parallel: Maximum parallel generations

        Returns:
            List of generation results
        """
        # Implementation will be added when integrating with main media_generator
        pass


class PromptCache:
    """Simple cache for similar prompts to reduce API costs"""

    def __init__(self):
        self.cache = {}
        self.max_size = 100

    def get_cached(self, prompt: str, model: str) -> Optional[str]:
        """Check if we have a cached result for similar prompt"""
        cache_key = f"{model}:{prompt[:100]}"
        return self.cache.get(cache_key)

    def add_to_cache(self, prompt: str, model: str, result: str):
        """Add a result to cache"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))

        cache_key = f"{model}:{prompt[:100]}"
        self.cache[cache_key] = result
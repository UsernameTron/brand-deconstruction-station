#!/usr/bin/env python3
"""
Style Modifier Engine for Brand Deconstruction Station
Applies photorealistic and cinematic modifiers to PENTAGRAM prompts for Google Imagen and Veo
Based on modifiers.md and Veo_Guidelines.md
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class MediaType(Enum):
    """Type of media to generate"""
    IMAGE = "image"
    VIDEO = "video"


class StylePreset(Enum):
    """Available style presets for generation"""
    EDITORIAL = "editorial"
    PHOTOREALISTIC = "photorealistic"
    CYBERPUNK = "cyberpunk"
    VINTAGE = "vintage"
    DOCUMENTARY = "documentary"
    CINEMATIC = "cinematic"
    SATIRICAL = "satirical"


@dataclass
class ModifierSet:
    """Collection of modifiers for a specific aspect"""
    lens: List[str]
    lighting: List[str]
    composition: List[str]
    color: List[str]
    atmosphere: List[str]
    movement: Optional[List[str]] = None  # For video only
    audio: Optional[List[str]] = None  # For video only


class StyleModifierEngine:
    """
    Applies style modifiers to PENTAGRAM prompts based on modifiers.md
    Optimized for Google Imagen (images) and Veo (videos)
    """

    # Image-specific modifiers (from modifiers.md)
    IMAGE_MODIFIERS = {
        StylePreset.EDITORIAL: ModifierSet(
            lens=["85mm portrait lens", "shallow depth of field", "natural bokeh"],
            lighting=["soft beauty lighting", "key 70% fill 30% back 20%", "flattering portraits"],
            composition=["rule of thirds", "balanced framing", "professional composition"],
            color=["neutral color grading", "natural skin tones", "preserved highlight detail"],
            atmosphere=["soft haze for depth", "subtle atmospheric texture", "professional quality"]
        ),
        StylePreset.PHOTOREALISTIC: ModifierSet(
            lens=["50mm natural perspective", "realistic depth of field", "subtle lens falloff"],
            lighting=["natural lighting", "soft diffused light", "realistic shadows"],
            composition=["eye level perspective", "natural framing", "environmental context"],
            color=["Kodak Portra 400 color palette", "warm highlights", "natural color grading"],
            atmosphere=["natural film grain", "realistic physics", "visible skin pores"]
        ),
        StylePreset.CYBERPUNK: ModifierSet(
            lens=["wide-angle lens", "deep focus", "lens flare from neon"],
            lighting=["neon glow", "harsh contrast", "cool 5600K rim light"],
            composition=["35° Dutch tilt for unease", "dramatic angles", "urban framing"],
            color=["teal-cyan mids", "electric blues", "toxic greens", "hot pinks"],
            atmosphere=["rain-slicked streets", "atmospheric fog", "light beams through haze"]
        ),
        StylePreset.VINTAGE: ModifierSet(
            lens=["vintage anamorphic lens", "oval bokeh", "soft focus edges"],
            lighting=["warm 3000K tungsten", "dramatic chiaroscuro", "Rembrandt lighting"],
            composition=["classic portrait framing", "centered composition", "negative space"],
            color=["shot on 1980s color film", "warm amber tones", "faded highlights"],
            atmosphere=["visible film grain", "analog bloom", "nostalgic quality"]
        ),
        StylePreset.DOCUMENTARY: ModifierSet(
            lens=["24mm environmental lens", "deep focus", "natural perspective"],
            lighting=["available light", "harsh midday sun", "uncontrolled natural light"],
            composition=["handheld framing", "observational angles", "candid moments"],
            color=["neutral grading", "gritty realism", "restrained color"],
            atmosphere=["documentary authenticity", "no stylization", "raw unpolished"]
        ),
        StylePreset.CINEMATIC: ModifierSet(
            lens=["anamorphic 2.39:1", "cinematic bokeh", "lens breathing"],
            lighting=["three-point lighting", "motivated key light", "dramatic backlight"],
            composition=["widescreen framing", "leading lines", "symmetrical balance"],
            color=["filmic color grade", "teal and orange", "cinematic density"],
            atmosphere=["soft god rays", "dust in shafts of light", "cinematic haze"]
        ),
        StylePreset.SATIRICAL: ModifierSet(
            lens=["distorted wide angle", "exaggerated perspective", "fish-eye edges"],
            lighting=["harsh corporate fluorescent", "unflattering overhead", "sterile bright"],
            composition=["uncomfortable close-ups", "imposing low angles", "corporate symmetry"],
            color=["oversaturated corporate colors", "artificial vibrancy", "plastic sheen"],
            atmosphere=["sterile environment", "artificial cleanliness", "uncanny valley"]
        )
    }

    # Video-specific modifiers (from Veo_Guidelines.md)
    VIDEO_MODIFIERS = {
        StylePreset.EDITORIAL: ModifierSet(
            lens=["85mm telephoto feel", "shallow depth of field", "smooth focus pulls"],
            lighting=["consistent golden hour", "soft key light", "professional three-point"],
            composition=["medium shots", "professional framing", "rule of thirds throughout"],
            color=["consistent color grade", "warm professional tone", "broadcast quality"],
            atmosphere=["subtle atmospheric depth", "controlled environment", "polished finish"],
            movement=["slow dolly forward", "gentle lateral tracking", "smooth gimbal movement"],
            audio=["room tone", "subtle ambience", "professional foley"]
        ),
        StylePreset.PHOTOREALISTIC: ModifierSet(
            lens=["50mm natural feel", "1/50 shutter for motion blur", "24fps"],
            lighting=["natural progression", "realistic time of day", "motivated light sources"],
            composition=["eye level tracking", "natural movement", "human perspective"],
            color=["naturalistic grade", "real-world colors", "no stylization"],
            atmosphere=["environmental particles", "realistic weather", "authentic textures"],
            movement=["handheld organic feel", "natural camera sway", "realistic speed"],
            audio=["natural ambient sound", "footsteps", "breathing", "environmental audio"]
        ),
        StylePreset.CYBERPUNK: ModifierSet(
            lens=["wide angle dystopian", "deep focus urban", "anamorphic flares"],
            lighting=["neon-lit streets", "harsh LED sources", "dark shadows with color"],
            composition=["low angle hero shots", "dramatic Dutch tilts", "urban maze framing"],
            color=["neon palette", "high contrast", "electric blue and magenta"],
            atmosphere=["rain effects", "steam from vents", "holographic distortions"],
            movement=["dynamic camera moves", "whip pans", "rapid tracking shots"],
            audio=["synthetic ambience", "electronic hums", "dystopian soundscape"]
        ),
        StylePreset.VINTAGE: ModifierSet(
            lens=["vintage glass characteristics", "film gate visible", "period-accurate focal lengths"],
            lighting=["period-appropriate lighting", "tungsten warmth", "practical lights only"],
            composition=["classic Hollywood framing", "static tripod shots", "theatrical staging"],
            color=["period film stock emulation", "faded colors", "vintage color timing"],
            atmosphere=["film grain and dust", "optical imperfections", "nostalgic quality"],
            movement=["classic dolly moves", "steady crane shots", "theatrical blocking"],
            audio=["period-appropriate ambience", "vintage room tone", "analog imperfections"]
        ),
        StylePreset.DOCUMENTARY: ModifierSet(
            lens=["zoom lens flexibility", "variable focal length", "documentary realism"],
            lighting=["available light only", "no lighting setup", "natural conditions"],
            composition=["observational framing", "following action", "reactive camera"],
            color=["minimal grading", "raw footage feel", "authentic colors"],
            atmosphere=["uncontrolled environment", "real-world conditions", "authentic moments"],
            movement=["handheld documentary style", "following subjects", "reactive panning"],
            audio=["direct sound recording", "ambient reality", "unprocessed audio"]
        ),
        StylePreset.CINEMATIC: ModifierSet(
            lens=["anamorphic characteristics", "2.39:1 aspect", "cinematic depth"],
            lighting=["dramatic film lighting", "motivated sources", "cinematic contrast"],
            composition=["cinematic blocking", "composed frames", "visual storytelling"],
            color=["professional color grade", "cinematic LUT", "film emulation"],
            atmosphere=["controlled atmosphere", "production value", "cinematic quality"],
            movement=["crane shots", "steadicam moves", "dolly tracking", "professional moves"],
            audio=["cinematic sound design", "layered ambience", "professional mix"]
        ),
        StylePreset.SATIRICAL: ModifierSet(
            lens=["distorting wide angle", "unsettling focal lengths", "corporate sterility"],
            lighting=["harsh fluorescent", "overlit offices", "unflattering angles"],
            composition=["corporate video parody", "awkward framing", "forced symmetry"],
            color=["oversaturated corporate", "unnatural skin tones", "plastic reality"],
            atmosphere=["artificial environment", "corporate dystopia", "uncanny valley"],
            movement=["robotic camera moves", "unnatural smoothness", "corporate video style"],
            audio=["muzak undertones", "corporate ambience", "artificial happiness"]
        )
    }

    # Technical parameters for Veo (from guidelines)
    VEO_TECHNICAL_PARAMS = {
        "duration_options": [4, 6, 8],  # seconds
        "aspect_ratios": ["16:9", "9:16"],
        "resolutions": ["720p", "1080p"],
        "fps": 24,
        "max_reference_images": 3
    }

    # Negative prompts to avoid (what NOT to include)
    NEGATIVE_MODIFIERS = [
        "no AI look",
        "no stylization",
        "no cartoon look",
        "no floating limbs",
        "no harsh hotspots",
        "no oversaturated colors",
        "avoid green contamination",
        "no lens dirt",
        "no flicker",
        "realistic physics only"
    ]

    def __init__(self):
        """Initialize the style modifier engine"""
        self.current_style = StylePreset.PHOTOREALISTIC
        self.media_type = MediaType.IMAGE

    def apply_modifiers(
        self,
        base_prompt: str,
        style_preset: StylePreset,
        media_type: MediaType,
        custom_modifiers: Optional[Dict[str, List[str]]] = None,
        include_negative: bool = True
    ) -> str:
        """
        Apply style modifiers to enhance a PENTAGRAM prompt

        Args:
            base_prompt: Original PENTAGRAM-structured prompt
            style_preset: Style to apply (editorial, cyberpunk, etc.)
            media_type: IMAGE or VIDEO
            custom_modifiers: Additional custom modifiers to apply
            include_negative: Whether to include negative prompts

        Returns:
            Enhanced prompt with modifiers applied
        """
        self.current_style = style_preset
        self.media_type = media_type

        # Select appropriate modifier set
        if media_type == MediaType.IMAGE:
            modifiers = self.IMAGE_MODIFIERS.get(style_preset, self.IMAGE_MODIFIERS[StylePreset.PHOTOREALISTIC])
        else:
            modifiers = self.VIDEO_MODIFIERS.get(style_preset, self.VIDEO_MODIFIERS[StylePreset.PHOTOREALISTIC])

        # Build enhanced prompt
        enhanced_parts = [base_prompt]

        # Add lens characteristics
        if modifiers.lens:
            enhanced_parts.append(f"[Lens]: {', '.join(random.sample(modifiers.lens, min(2, len(modifiers.lens))))}")

        # Add lighting
        if modifiers.lighting:
            enhanced_parts.append(f"[Lighting]: {', '.join(random.sample(modifiers.lighting, min(2, len(modifiers.lighting))))}")

        # Add composition
        if modifiers.composition:
            enhanced_parts.append(f"[Composition]: {', '.join(random.sample(modifiers.composition, min(2, len(modifiers.composition))))}")

        # Add color grading
        if modifiers.color:
            enhanced_parts.append(f"[Color]: {', '.join(random.sample(modifiers.color, min(3, len(modifiers.color))))}")

        # Add atmosphere
        if modifiers.atmosphere:
            enhanced_parts.append(f"[Atmosphere]: {', '.join(random.sample(modifiers.atmosphere, min(2, len(modifiers.atmosphere))))}")

        # Add video-specific modifiers
        if media_type == MediaType.VIDEO:
            if modifiers.movement:
                enhanced_parts.append(f"[Camera Movement]: {', '.join(random.sample(modifiers.movement, min(2, len(modifiers.movement))))}")
            if modifiers.audio:
                enhanced_parts.append(f"[Audio]: {', '.join(random.sample(modifiers.audio, min(2, len(modifiers.audio))))}")

        # Add custom modifiers if provided
        if custom_modifiers:
            for category, values in custom_modifiers.items():
                enhanced_parts.append(f"[{category}]: {', '.join(values)}")

        # Add negative modifiers
        if include_negative:
            enhanced_parts.append(f"[Avoid]: {', '.join(random.sample(self.NEGATIVE_MODIFIERS, min(3, len(self.NEGATIVE_MODIFIERS))))}")

        return "\n".join(enhanced_parts)

    def generate_veo_prompt(
        self,
        subject: str,
        action: str,
        style_preset: StylePreset,
        duration: int = 6,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
        shot_number: int = 1
    ) -> Dict[str, any]:
        """
        Generate a complete Veo-formatted prompt following guidelines

        Args:
            subject: Main subject description
            action: Primary action in the shot
            style_preset: Visual style to apply
            duration: Shot duration (4, 6, or 8 seconds)
            aspect_ratio: "16:9" or "9:16"
            resolution: "720p" or "1080p"
            shot_number: Shot number in sequence

        Returns:
            Complete Veo prompt with technical parameters
        """
        # Validate parameters
        if duration not in self.VEO_TECHNICAL_PARAMS["duration_options"]:
            duration = 6  # Default to 6 seconds
        if aspect_ratio not in self.VEO_TECHNICAL_PARAMS["aspect_ratios"]:
            aspect_ratio = "16:9"
        if resolution not in self.VEO_TECHNICAL_PARAMS["resolutions"]:
            resolution = "1080p"

        # Get modifiers for the style
        modifiers = self.VIDEO_MODIFIERS.get(style_preset, self.VIDEO_MODIFIERS[StylePreset.PHOTOREALISTIC])

        # Build the Veo prompt structure
        veo_prompt = {
            "shot_number": shot_number,
            "header": f"SHOT {shot_number} - {duration}s, {aspect_ratio}, {resolution}",
            "prompt": {
                "subject_and_action": f"{subject}, {action}",
                "camera": ", ".join(random.sample(modifiers.lens + modifiers.composition, 3)),
                "environment_and_mood": ", ".join(random.sample(modifiers.atmosphere + modifiers.lighting, 3)),
                "style_grade": ", ".join(random.sample(modifiers.color, 2))
            },
            "technical_parameters": {
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "fps": self.VEO_TECHNICAL_PARAMS["fps"],
                "audio": "Enabled" if modifiers.audio else "Disabled",
                "reference_images": "No",
                "frame_control": None
            },
            "full_text": ""
        }

        # Compile full text prompt
        full_prompt = f"""
{veo_prompt['header']}

PROMPT:
[Subject and action]: "{veo_prompt['prompt']['subject_and_action']}"
[Camera]: "{veo_prompt['prompt']['camera']}"
[Environment and mood]: "{veo_prompt['prompt']['environment_and_mood']}"
[Style/grade]: "{veo_prompt['prompt']['style_grade']}"

TECHNICAL PARAMETERS:
- Duration: {veo_prompt['technical_parameters']['duration']} seconds
- Aspect Ratio: {veo_prompt['technical_parameters']['aspect_ratio']}
- Resolution: {veo_prompt['technical_parameters']['resolution']}
- Audio: {veo_prompt['technical_parameters']['audio']}
- Reference Images: {veo_prompt['technical_parameters']['reference_images']}
"""
        veo_prompt["full_text"] = full_prompt.strip()

        return veo_prompt

    def suggest_modifiers_for_concept(self, concept: str, vulnerabilities: List[str]) -> StylePreset:
        """
        Suggest the best style preset based on brand vulnerabilities

        Args:
            concept: Brand concept or description
            vulnerabilities: List of identified brand vulnerabilities

        Returns:
            Recommended style preset
        """
        # Analyze vulnerabilities to suggest style
        vuln_text = " ".join(vulnerabilities).lower()

        if any(word in vuln_text for word in ["corporate", "sterile", "fake", "artificial"]):
            return StylePreset.SATIRICAL
        elif any(word in vuln_text for word in ["tech", "digital", "future", "innovation"]):
            return StylePreset.CYBERPUNK
        elif any(word in vuln_text for word in ["authentic", "real", "honest", "transparent"]):
            return StylePreset.DOCUMENTARY
        elif any(word in vuln_text for word in ["premium", "luxury", "exclusive", "sophisticated"]):
            return StylePreset.EDITORIAL
        elif any(word in vuln_text for word in ["nostalgic", "traditional", "heritage", "classic"]):
            return StylePreset.VINTAGE
        elif any(word in vuln_text for word in ["epic", "dramatic", "powerful", "impressive"]):
            return StylePreset.CINEMATIC
        else:
            return StylePreset.PHOTOREALISTIC

    def get_random_modifiers(self, category: str, count: int = 3) -> List[str]:
        """
        Get random modifiers from a specific category

        Args:
            category: Category name (lens, lighting, etc.)
            count: Number of modifiers to return

        Returns:
            List of random modifiers
        """
        all_modifiers = []

        # Collect modifiers from all styles
        modifier_source = self.IMAGE_MODIFIERS if self.media_type == MediaType.IMAGE else self.VIDEO_MODIFIERS

        for style_modifiers in modifier_source.values():
            if hasattr(style_modifiers, category):
                category_list = getattr(style_modifiers, category)
                if category_list:
                    all_modifiers.extend(category_list)

        # Remove duplicates and return random sample
        unique_modifiers = list(set(all_modifiers))
        return random.sample(unique_modifiers, min(count, len(unique_modifiers)))

    def create_shot_sequence(
        self,
        brand_name: str,
        vulnerabilities: List[str],
        shot_count: int = 4,
        style_preset: Optional[StylePreset] = None
    ) -> List[Dict]:
        """
        Create a sequence of shots for a satirical brand video

        Args:
            brand_name: Name of the brand
            vulnerabilities: Brand vulnerabilities to highlight
            shot_count: Number of shots to generate
            style_preset: Style to use (auto-detected if None)

        Returns:
            List of shot descriptions with Veo prompts
        """
        if not style_preset:
            style_preset = self.suggest_modifiers_for_concept(brand_name, vulnerabilities)

        shots = []

        # Define shot templates for satirical brand videos
        shot_templates = [
            ("Establishing shot", f"Wide exterior view of {brand_name} corporate headquarters", "slow push in revealing imposing architecture"),
            ("Product glamour", f"Sleek {brand_name} product on pristine white surface", "360-degree rotation with dramatic lighting"),
            ("Employee testimony", f"Smiling employee in {brand_name} uniform", "speaking enthusiastically to camera"),
            ("Customer interaction", f"Customer engaging with {brand_name} service", "tracking shot following interaction"),
            ("Logo reveal", f"Dramatic {brand_name} logo", "emerging from darkness with lens flares"),
            ("Behind the scenes", f"Factory or office interior of {brand_name}", "revealing automated processes"),
        ]

        # Generate shots
        for i in range(min(shot_count, len(shot_templates))):
            shot_type, subject, action = shot_templates[i]

            # Vary technical parameters
            duration = random.choice([4, 6, 8])
            aspect_ratio = "16:9"  # Default to landscape for brand videos

            veo_prompt = self.generate_veo_prompt(
                subject=subject,
                action=action,
                style_preset=style_preset,
                duration=duration,
                aspect_ratio=aspect_ratio,
                resolution="1080p",
                shot_number=i + 1
            )

            shots.append({
                "shot_type": shot_type,
                "veo_prompt": veo_prompt,
                "style": style_preset.value
            })

        return shots


# Example usage and testing
if __name__ == "__main__":
    # Initialize the engine
    engine = StyleModifierEngine()

    # Test image modifier application
    base_prompt = "A corporate executive standing in a glass office"
    enhanced_image = engine.apply_modifiers(
        base_prompt,
        StylePreset.SATIRICAL,
        MediaType.IMAGE
    )
    print("Enhanced Image Prompt:")
    print(enhanced_image)
    print("\n" + "="*50 + "\n")

    # Test video prompt generation
    veo_prompt = engine.generate_veo_prompt(
        subject="A sleek corporate lobby with marble floors",
        action="camera glides through revealing sterile perfection",
        style_preset=StylePreset.SATIRICAL,
        duration=8,
        aspect_ratio="16:9",
        resolution="1080p",
        shot_number=1
    )
    print("Veo Video Prompt:")
    print(veo_prompt["full_text"])
    print("\n" + "="*50 + "\n")

    # Test shot sequence generation
    shots = engine.create_shot_sequence(
        brand_name="MegaCorp",
        vulnerabilities=["corporate sterility", "fake authenticity", "profit over people"],
        shot_count=3
    )
    print("Shot Sequence:")
    for shot in shots:
        print(f"\n{shot['shot_type']} ({shot['style']}):")
        print(shot['veo_prompt']['full_text'])
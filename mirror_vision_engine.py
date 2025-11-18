#!/usr/bin/env python3
"""
Mirror Vision Prompt Crafter Engine
Generates photorealistic MidJourney v6+ YAML prompts with brutal visual metaphors
NO PR LAYERS - RAW AND UNFILTERED SATIRICAL CONTENT

Based on Mirror Vision Prompt Crafter skill and reference documentation
"""

import yaml
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict


class VisualMetaphorPattern(Enum):
    """Six core visual metaphor patterns for satirical image generation"""
    JUXTAPOSITION = "juxtaposition"  # Side-by-side truth
    REVEAL = "reveal"  # Pull back the curtain
    ARCHAEOLOGICAL = "archaeological"  # Evidence left behind
    CONNECTION = "connection"  # Follow the money/power
    SCALE_DISTORTION = "scale_distortion"  # Resource allocation
    TIME_LAPSE = "time_lapse"  # Promises vs delivery


class SatiricalTarget(Enum):
    """Types of satirical targets"""
    CORPORATE = "corporate"
    TECH = "tech"
    POLITICAL = "political"
    SOCIAL = "social"


@dataclass
class MirrorVisionPrompt:
    """Complete Mirror Vision YAML prompt structure"""
    description: str
    subject: str
    environment: List[str]
    style: List[str]
    lighting: List[str]
    color_palette: List[str]
    mood: List[str]
    camera: List[str]
    post_processing: List[str]
    resolution: str
    text_overlays: List[str]
    caption: str
    parameters: str
    negative: str

    def to_yaml(self) -> str:
        """Convert to YAML string"""
        data = asdict(self)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def to_imagen_prompt(self) -> str:
        """Extract prompt suitable for Google Imagen"""
        # Combine description, subject, and key visual elements
        prompt_parts = [
            self.description,
            self.subject,
            ", ".join(self.environment[:2]),
            ", ".join(self.style),
            ", ".join(self.lighting[:2]),
            self.resolution
        ]
        return " ".join(filter(None, prompt_parts))


class FidelityModifierLibrary:
    """
    Complete fidelity modifier library from REFERENCE.md
    30+ modifiers per category for photorealistic rendering
    """

    RESOLUTION_RENDER = [
        "12K (12288×6480)", "15360×8640", "32-bit linear EXR", "16-bit RAW pipeline",
        "Path-traced", "Spectral ray-traced", "Bidirectional global-illumination",
        "Unclamped HDR", "15-stop dynamic range", "x16 super-sampling",
        "Sub-pixel jitter", "Micro-displacement", "Adaptive tessellation",
        "Parallax occlusion mapping", "PBR shading", "Disney BRDF",
        "Energy-conserving materials", "Stochastic denoise OFF"
    ]

    SENSOR_OPTICS = [
        "ARRI Alexa 65", "RED V-Raptor XL 8K", "Sony Venice 2", "Phase One IQ4 150MP",
        "Zeiss Otus 85 mm f/1.4", "Canon EF 100 mm Macro L f/2.8",
        "Leica Noctilux 50 mm f/0.95", "ƒ/1.2 prime", "1/125 s shutter", "ISO 100",
        "11-blade round bokeh", "Sensor bloom", "Lens breathing",
        "Aperture starburst", "Anamorphic horizontal flare", "Gate weave",
        "Edge diffraction spikes"
    ]

    LIGHTING_ATMOSPHERICS = [
        "HDRI 32-bit dome", "3-point studio softboxes", "Kino-Flo bounce fill",
        "5600 K key", "3200 K practicals", "Negative fill flags",
        "Specular kicker", "Volumetric fog", "God rays", "Air particulate",
        "Aerosol haze", "Light wrap", "Subsurface translucency back-light",
        "Multi-bounce caustics", "Global volumetrics", "ACES-cg pipeline RRT+ODT"
    ]

    MATERIAL_SURFACE = [
        "Anisotropic brushed titanium", "Aged bronze patina", "Chromed nickel",
        "Frosted borosilicate glass", "Translucent resin", "Nano-coated polymer",
        "Tri-layer human skin SSS", "Fine-grain leather pore", "Cross-weave linen",
        "Fingerprint oils", "Dust motes", "Hairline scratches",
        "Thin-film interference", "IOR 1.52", "Anisotropic roughness 0.15",
        "Micron-scale normal noise"
    ]

    COLOR_GRADING = [
        "ACEScg color space", "ACES 1.3 RRT", "Rec. 709 ODT", "Display P3 export",
        "Kodak Vision3 500T 5219", "Fuji Eterna 250D", "Kodak Ektachrome 100D",
        "Teal-orange blockbuster", "Bleach-bypass", "Cool-neutral commercial",
        "Soft pastel fashion", "Chromatic aberration (subtle)", "Halation glow",
        "Bloom 1%", "Fine 35 mm grain"
    ]

    POST_PROCESSING = [
        "Sharpen radius 0.3 px", "Clarity micro-contrast +5%", "Vignette −0.5 EV",
        "Letterbox 2.39:1", "Clean plate", "Zero watermark", "PNG-16 bit",
        "TIFF-16 bit", "Lossless compression", "Metadata embed: lens & body tags"
    ]

    @classmethod
    def get_random_modifiers(cls, category: str, count: int = 4) -> List[str]:
        """Get random modifiers from a category"""
        category_map = {
            'resolution': cls.RESOLUTION_RENDER,
            'sensor': cls.SENSOR_OPTICS,
            'lighting': cls.LIGHTING_ATMOSPHERICS,
            'material': cls.MATERIAL_SURFACE,
            'color': cls.COLOR_GRADING,
            'post': cls.POST_PROCESSING
        }
        pool = category_map.get(category, [])
        return random.sample(pool, min(count, len(pool)))


class MirrorUniversePeteVoice:
    """
    Caption generator using Mirror Universe Pete voice
    75% cold logic, 20% weaponized politeness, 5% dark irony
    NO PR-PROOFING - RAW AND BRUTAL
    """

    @staticmethod
    def generate_caption(
        contradiction: str,
        brand_name: str,
        evidence: str,
        severity: str = "brutal"
    ) -> str:
        """
        Generate 3-component caption with surgical precision

        Args:
            contradiction: The specific hypocrisy being exposed
            brand_name: Target brand name
            evidence: Visual evidence shown in the image
            severity: How brutal to be (brutal, ruthless, lethal)
        """
        # Surgical opening templates (establish contradiction)
        openings = [
            f"The {evidence} remains pristine—proof that {contradiction} works best when nobody has time to use it.",
            f"Every presentation about {contradiction} is approximately 47 milliseconds from revealing the actual priority.",
            f"{brand_name}'s commitment to {contradiction} is most evident in what remains unused.",
            f"The gap between {brand_name}'s {contradiction} claims and {evidence} tells the real story.",
            f"Observable fact: {evidence} contradicts every public statement about {contradiction}."
        ]

        # Forensic dismantling templates (expose mechanism)
        dismantlings = [
            "Follow the money to see what actually gets optimized.",
            "The cable doesn't lie—trace it to find the real priorities.",
            "Efficiency in optics, consistency in inaction.",
            "Impressive commitment to the aesthetic of care without the burden of implementation.",
            "The data flow reveals what they actually measure."
        ]

        # Lethal dismissal templates (close with finality)
        if severity == "brutal":
            dismissals = [
                "Brutal honesty: they never intended to follow through.",
                "The contradiction is the feature, not the bug.",
                "Performance art masquerading as policy.",
                "The quiet part, said loud through architectural choices.",
                "Thank you for making the hypocrisy photographable."
            ]
        elif severity == "ruthless":
            dismissals = [
                "Cut the bullshit: this was theater from day one.",
                "The corpse of corporate responsibility, beautifully preserved.",
                "Weaponized incompetence disguised as initiative.",
                "They're not even trying to hide it anymore.",
                "The emperor's new clothes, in 12K resolution."
            ]
        else:  # lethal
            dismissals = [
                "They knew. They always knew. This is what they chose.",
                "Moral bankruptcy, rendered in path-traced realism.",
                "The machine eating itself, one quarterly report at a time.",
                "Capitalism's epitaph, written in dust and unused intentions.",
                "The truth they didn't want you to see, now impossible to unsee."
            ]

        # Construct 3-component execution
        opening = random.choice(openings)
        dismantling = random.choice(dismantlings)
        dismissal = random.choice(dismissals)

        return f"{opening} {dismantling} {dismissal}"


class MirrorVisionEngine:
    """
    Core engine for generating Mirror Vision prompts
    NO PR LAYERS - COMPLETELY RAW AND UNFILTERED
    """

    def __init__(self):
        self.modifier_lib = FidelityModifierLibrary()
        self.caption_gen = MirrorUniversePeteVoice()

    def generate_prompt(
        self,
        brand_name: str,
        vulnerability: str,
        satirical_angle: str,
        target_type: SatiricalTarget = SatiricalTarget.CORPORATE,
        metaphor_pattern: Optional[VisualMetaphorPattern] = None,
        severity: str = "brutal"
    ) -> MirrorVisionPrompt:
        """
        Generate complete Mirror Vision YAML prompt

        Args:
            brand_name: Target brand name
            vulnerability: Primary vulnerability to expose
            satirical_angle: Satirical perspective/angle
            target_type: Type of satirical target
            metaphor_pattern: Visual metaphor pattern (auto-selected if None)
            severity: How brutal to be (brutal, ruthless, lethal)
        """
        # Auto-select metaphor pattern if not specified
        if metaphor_pattern is None:
            metaphor_pattern = self._select_metaphor_pattern(vulnerability, satirical_angle)

        # Select appropriate template based on target and pattern
        if target_type == SatiricalTarget.TECH:
            return self._generate_tech_dystopia(
                brand_name, vulnerability, satirical_angle, metaphor_pattern, severity
            )
        elif metaphor_pattern == VisualMetaphorPattern.ARCHAEOLOGICAL:
            return self._generate_abandoned_promise(
                brand_name, vulnerability, satirical_angle, severity
            )
        else:
            return self._generate_corporate_contradiction(
                brand_name, vulnerability, satirical_angle, metaphor_pattern, severity
            )

    def _select_metaphor_pattern(self, vulnerability: str, satirical_angle: str) -> VisualMetaphorPattern:
        """Auto-select metaphor pattern based on content"""
        # Simple keyword matching for pattern selection
        text = (vulnerability + " " + satirical_angle).lower()

        if any(word in text for word in ["unused", "abandoned", "forgotten", "dust", "empty"]):
            return VisualMetaphorPattern.ARCHAEOLOGICAL
        elif any(word in text for word in ["connection", "link", "flow", "pipeline", "data"]):
            return VisualMetaphorPattern.CONNECTION
        elif any(word in text for word in ["scale", "size", "budget", "allocation", "disparity"]):
            return VisualMetaphorPattern.SCALE_DISTORTION
        elif any(word in text for word in ["promise", "reality", "claim", "actual", "vs"]):
            return VisualMetaphorPattern.JUXTAPOSITION
        elif any(word in text for word in ["hidden", "reveal", "behind", "curtain", "facade"]):
            return VisualMetaphorPattern.REVEAL
        else:
            return VisualMetaphorPattern.TIME_LAPSE

    def _generate_corporate_contradiction(
        self,
        brand_name: str,
        vulnerability: str,
        satirical_angle: str,
        metaphor_pattern: VisualMetaphorPattern,
        severity: str
    ) -> MirrorVisionPrompt:
        """Generate Corporate Contradiction template"""

        # Get fidelity modifiers (3-5 from each category)
        resolution_mods = self.modifier_lib.get_random_modifiers('resolution', 4)
        sensor_mods = self.modifier_lib.get_random_modifiers('sensor', 4)
        lighting_mods = self.modifier_lib.get_random_modifiers('lighting', 4)
        material_mods = self.modifier_lib.get_random_modifiers('material', 4)
        color_mods = self.modifier_lib.get_random_modifiers('color', 4)
        post_mods = self.modifier_lib.get_random_modifiers('post', 4)

        # Build photorealistic description
        description = f"""Photorealistic corporate environment, {', '.join(resolution_mods[:3])}, {sensor_mods[0]}, {sensor_mods[1]}, {lighting_mods[0]}. Pristine corporate {vulnerability} initiative space contrasted with harsh reality of actual {satirical_angle}. {lighting_mods[1]} separating the facade from truth. {', '.join(material_mods[:2])}. {color_mods[0]}, {color_mods[1]}."""

        # Build subject with brutal metaphor
        subject = f"""Untouched {vulnerability} materials centered on display, showing {satirical_angle} was never the actual priority. {material_mods[2]} revealing fingerprint-free surfaces proving zero genuine engagement. The contradiction made physically visible."""

        # Environment elements exposing truth
        environment = [
            f"{brand_name} {vulnerability} initiative room with pristine, unused materials",
            f"Adjacent actual workspace visible through glass—reality of {satirical_angle}",
            "Architectural design exposing what gets resources versus what gets press releases",
            f"{lighting_mods[2]} bleeding through, illuminating the actual priorities"
        ]

        # Style specifications
        style = [
            "Photorealistic",
            "Documentary evidence photography",
            "Brutally honest juxtaposition—no softening, no PR spin"
        ]

        # Lighting setup
        lighting = [
            f"{lighting_mods[0]} in initiative space (serene, unused)",
            "Harsh fluorescent reality in actual work environment",
            f"{lighting_mods[1]} creating separation membrane",
            f"{lighting_mods[3]} revealing dust accumulation patterns"
        ]

        # Color palette with intent
        color_palette = [
            "Sterile white (initiative space: unused purity, corporate theater)",
            f"Harsh fluorescent ({satirical_angle}: actual priority reality)",
            "Warm wood accents (false comfort, performative aesthetics)"
        ]

        # Mood
        mood = [
            "Cynically forensic",
            "Architectural truth-telling through resource allocation"
        ]

        # Camera specs
        camera = [
            sensor_mods[1],
            "Golden-spiral composition centering the unused facade",
            sensor_mods[0],
            "Symmetrical framing exposing the contradiction through design"
        ]

        # Post-processing
        post_processing = [
            post_mods[0],
            post_mods[1],
            f"{color_mods[2]} emphasizing the gap between promise and reality",
            post_mods[2],
            color_mods[3]
        ]

        # Resolution
        resolution = f"{resolution_mods[0]}, {resolution_mods[1]}, {resolution_mods[2]}"

        # Generate brutal caption
        caption = self.caption_gen.generate_caption(
            contradiction=vulnerability,
            brand_name=brand_name,
            evidence=f"{vulnerability} initiative materials",
            severity=severity
        )

        return MirrorVisionPrompt(
            description=description,
            subject=subject,
            environment=environment,
            style=style,
            lighting=lighting,
            color_palette=color_palette,
            mood=mood,
            camera=camera,
            post_processing=post_processing,
            resolution=resolution,
            text_overlays=[],
            caption=caption,
            parameters="--ar 3:2 --q 2 --style raw --v 6",
            negative="--no cartoon, --no illustration, --no stylized, --no text overlays, --no aliased edges, --no distortion"
        )

    def _generate_tech_dystopia(
        self,
        brand_name: str,
        vulnerability: str,
        satirical_angle: str,
        metaphor_pattern: VisualMetaphorPattern,
        severity: str
    ) -> MirrorVisionPrompt:
        """Generate Tech Dystopia template"""

        # Get fidelity modifiers
        resolution_mods = self.modifier_lib.get_random_modifiers('resolution', 5)
        sensor_mods = self.modifier_lib.get_random_modifiers('sensor', 4)
        lighting_mods = self.modifier_lib.get_random_modifiers('lighting', 4)
        material_mods = self.modifier_lib.get_random_modifiers('material', 4)
        color_mods = self.modifier_lib.get_random_modifiers('color', 4)
        post_mods = self.modifier_lib.get_random_modifiers('post', 4)

        description = f"""Photorealistic split-scene tech environment, {', '.join(resolution_mods[:3])}, {sensor_mods[0]}, {sensor_mods[1]}. Left: Gleaming {brand_name} presentation showing {vulnerability} solutions. Right: Server room displaying actual {satirical_angle} metrics in real-time. {material_mods[0]} server racks, {lighting_mods[0]}, {lighting_mods[1]} between marketing and reality. {resolution_mods[3]}, {color_mods[0]}."""

        subject = f"""Fiber-optic cable physically connecting both spaces—the truth connector. Macro detail shows data flowing from "{vulnerability} FOR GOOD" server to "{satirical_angle} OPTIMIZATION" server. {material_mods[1]} on cable sheath, {material_mods[2]} caught in light, making the hypocrisy tangible."""

        environment = [
            f"Left: {brand_name} pristine presentation room with holographic {vulnerability} displays",
            f"Right: Utilitarian server room with {satirical_angle} revenue dashboards, counters spinning",
            "Center: Physical cable connection exposing the data flow—the truth pathway",
            f"{lighting_mods[1]} creating atmospheric separation between promise and execution"
        ]

        style = [
            "Photorealistic",
            "Technical macro documentary photography",
            "Follow-the-money visual journalism—brutal and unambiguous"
        ]

        lighting = [
            f"Left: Warm {lighting_mods[2]} (aspirational, TED-talk glow, marketing theater)",
            f"Right: Cool {lighting_mods[0]} (cold machinery reality, actual priorities)",
            f"Cable: Internal fiber-optic glow, {lighting_mods[3]}, revealing data truth",
            "Multi-bounce caustics on server racks showing the computational reality"
        ]

        color_palette = [
            "Warm gold (left: marketing optimism, facade construction)",
            "Cold steel blue (right: profit machinery, actual algorithmic priorities)",
            "Fiber-optic green (data flow: the unfiltered truth pathway)"
        ]

        mood = [
            "Technically brutal—follow the cable to find what's actually optimized",
            "Forensic precision exposing the gap between pitch deck and production"
        ]

        camera = [
            f"{sensor_mods[1]} at ƒ/2.8",
            "Split diptych framing with rule-of-thirds grid",
            sensor_mods[0],
            "Foreground parallax layer on truth-revealing cable connection"
        ]

        post_processing = [
            f"{post_mods[0]} for cable macro detail—make the connection undeniable",
            post_mods[1],
            f"{color_mods[1]} for documentary evidence feel",
            color_mods[2],
            f"{color_mods[0]} with {post_mods[3]}"
        ]

        resolution = f"{resolution_mods[0]}, {resolution_mods[1]}, {resolution_mods[3]}, {resolution_mods[4]}"

        caption = self.caption_gen.generate_caption(
            contradiction=vulnerability,
            brand_name=brand_name,
            evidence="data cable connection",
            severity=severity
        )

        return MirrorVisionPrompt(
            description=description,
            subject=subject,
            environment=environment,
            style=style,
            lighting=lighting,
            color_palette=color_palette,
            mood=mood,
            camera=camera,
            post_processing=post_processing,
            resolution=resolution,
            text_overlays=[],
            caption=caption,
            parameters="--ar 3:2 --q 2 --style raw --v 6",
            negative="--no cartoon, --no illustration, --no stylized, --no text overlays, --no people faces, --no aliased edges"
        )

    def _generate_abandoned_promise(
        self,
        brand_name: str,
        vulnerability: str,
        satirical_angle: str,
        severity: str
    ) -> MirrorVisionPrompt:
        """Generate Abandoned Promise template"""

        # Get fidelity modifiers
        resolution_mods = self.modifier_lib.get_random_modifiers('resolution', 4)
        sensor_mods = self.modifier_lib.get_random_modifiers('sensor', 4)
        lighting_mods = self.modifier_lib.get_random_modifiers('lighting', 4)
        material_mods = self.modifier_lib.get_random_modifiers('material', 4)
        color_mods = self.modifier_lib.get_random_modifiers('color', 4)
        post_mods = self.modifier_lib.get_random_modifiers('post', 4)

        description = f"""Photorealistic abandoned {brand_name} {vulnerability} space, {', '.join(resolution_mods[:3])}, {sensor_mods[0]}, {sensor_mods[1]}, {lighting_mods[0]}. Pristine initiative materials showing zero signs of actual use despite {satirical_angle} claims. {material_mods[0]} accumulation macro detail, {material_mods[1]} on unused objects. {color_mods[0]}, {color_mods[1]}."""

        subject = f"""Untouched {vulnerability} materials centered on display, {material_mods[2]} showing months of non-use. Fingerprint-free surfaces proving this was always performative. Archaeological evidence of corporate theater preserved in pristine abandonment."""

        environment = [
            f"{brand_name} {vulnerability} initiative space with floor-to-ceiling glass walls",
            f"Pristine {vulnerability} materials arranged for photos, never for actual use",
            f"View into adjacent workspace showing actual {satirical_angle} priorities",
            f"{lighting_mods[1]} through windows revealing dust particles—time's truth"
        ]

        style = [
            "Photorealistic",
            "Archaeological evidence photography",
            "Abandonment study—pristine preservation revealing neglect"
        ]

        lighting = [
            f"Soft {lighting_mods[0]} in initiative space revealing dust evidence",
            f"{lighting_mods[1]} through blinds showing air particulate accumulation",
            "Unused space well-lit but empty—the theater must be maintained",
            f"Harsh lighting from actual workspace bleeding through—the real priorities"
        ]

        color_palette = [
            "Sterile white (initiative space: unused purity, corporate performance art)",
            "Warm wood accents (false comfort, aesthetic compliance)",
            f"Harsh fluorescent from actual workspace (where {satirical_angle} actually happens)"
        ]

        mood = [
            "Archaeological irony—proof through pristine preservation",
            "What remains unused reveals actual priorities louder than any statement"
        ]

        camera = [
            f"{sensor_mods[1]} at ƒ/1.2",
            "Symmetrical framing showing pristine abandonment",
            sensor_mods[0],
            "Golden-spiral composition centering the unused materials—the evidence"
        ]

        post_processing = [
            f"{post_mods[0]} to show dust detail—archaeological precision",
            post_mods[1],
            f"{color_mods[2]} emphasizing the abandonment",
            color_mods[3],
            post_mods[2]
        ]

        resolution = f"{resolution_mods[0]}, {resolution_mods[1]}, {resolution_mods[2]}"

        caption = self.caption_gen.generate_caption(
            contradiction=vulnerability,
            brand_name=brand_name,
            evidence="pristine unused materials",
            severity=severity
        )

        return MirrorVisionPrompt(
            description=description,
            subject=subject,
            environment=environment,
            style=style,
            lighting=lighting,
            color_palette=color_palette,
            mood=mood,
            camera=camera,
            post_processing=post_processing,
            resolution=resolution,
            text_overlays=[],
            caption=caption,
            parameters="--ar 3:2 --q 2 --style raw --v 6",
            negative="--no cartoon, --no illustration, --no stylized, --no text, --no people in abandoned space, --no aliased edges"
        )

Comprehensive Plan: Replacing PENTAGRAM with Mirror Vision Prompt Crafter
Executive Summary
This plan outlines the complete migration from the current PENTAGRAM prompt framework to the Mirror Vision Prompt Crafter system for generating satirical brand images. The Mirror Vision system offers superior photorealistic prompt generation with YAML-structured outputs optimized for MidJourney v6+ and Google Imagen.
Current State Analysis
PENTAGRAM Framework Locations
Core Implementation - /app.py:
_build_pentagram_prompt() method (lines 168-203)
generate_satirical_images() method (lines 394-462)
Used for creating structured prompts for brand satire
Style Modifiers - /style_modifiers.py:
Comments reference PENTAGRAM prompts (lines 4, 45, 206, 209)
Applies photorealistic modifiers to PENTAGRAM outputs
UI Reference - /templates/brand_station.html:
Display of PENTAGRAM framework info (lines 694-696)
User-facing framework explanation
Documentation - Multiple files:
CLAUDE.md - Framework documentation
CRITICAL_FIX_APPLIED.md - Framework references
PlanningforDeployment.md - Architecture notes
PENTAGRAM Structure
Current framework uses 9 components:
Purpose - Core satirical intent
Elements - Visual components and symbols
Narrative - Story/message conveyed
Tone - Emotional/stylistic approach
Audience - Target understanding
Guidelines - Technical constraints
Results - Expected output
Aesthetics - Visual style
Metaphors - Symbolic representations
Mirror Vision Architecture
Key Improvements
YAML Structure - 14 comprehensive fields vs 9 text components
Photorealistic Focus - 30+ fidelity modifiers per prompt
Brutal Satire - Enhanced visual metaphor patterns
MidJourney Optimization - Native v6+ parameter support
Caption System - Mirror Universe Pete voice integration
YAML Components
- description     # Detailed scene with photorealistic modifiers
- subject        # Main subject with visual metaphor
- environment    # 3-4 location/setting details
- style          # Photorealistic + 2 additional
- lighting       # 3 lighting specifications
- color_palette  # 3 colors with intent
- mood           # 2 emotional tones
- camera         # Lens, angle, sensor specifications
- post_processing # 5 enhancement techniques
- resolution     # 12K/15K specifications
- text_overlays  # Empty array (no text)
- caption        # Mirror Universe Pete voice
- parameters     # MidJourney v6 parameters
- negative       # Exclusion parameters
Migration Architecture
Phase 1: Core Module Creation
New File: /mirror_vision_engine.py Components:
MirrorVisionEngine Class
YAML prompt generation
Fidelity modifier library
Visual metaphor patterns
Caption generation
Prompt Templates
Corporate Contradiction template
Tech Dystopia template
Abandoned Promise template
Custom pattern builders
Modifier System
Resolution & Render Engine modifiers
Sensor & Optics modifiers
Lighting & Atmospherics
Material & Surface Fidelity
Color Grading & Science
Post-Processing Enhancements
Phase 2: Integration Points
Modified Files:
/app.py - Primary Integration
Replace _build_pentagram_prompt() with _build_mirror_vision_prompt()
Update generate_satirical_images() to use MirrorVisionEngine
Modify prompt structure from text to YAML
Add clarification protocol for unclear targets
/style_modifiers.py - Enhancement Layer
Update to process YAML structures
Integrate Mirror Vision fidelity modifiers
Maintain compatibility with existing style presets
Add YAML-to-prompt conversion for APIs
/media_generator.py - Output Processing
Handle YAML prompt format
Extract relevant fields for Imagen/Veo
Process Mirror Vision parameters
Phase 3: UI Updates
Modified Files:
/templates/brand_station.html
Update framework display from PENTAGRAM to Mirror Vision
Show YAML structure preview
Display fidelity modifier categories
Add clarification dialog for unclear targets
Frontend JavaScript
Handle YAML prompt display
Format Mirror Vision output
Show caption in Mirror Universe Pete style
Implementation Strategy
Step 1: Data Mapping
Map PENTAGRAM components to Mirror Vision:
PENTAGRAM	Mirror Vision Fields
Purpose	caption, mood
Elements	subject, environment
Narrative	description, caption
Tone	mood, style
Audience	(implicit in caption voice)
Guidelines	parameters, negative
Results	resolution, post_processing
Aesthetics	style, camera, lighting
Metaphors	subject, environment
Step 2: Prompt Transformation
Transform flow:
Extract vulnerabilities and satirical angles
Select appropriate Mirror Vision template
Apply visual metaphor pattern (1 of 6 patterns)
Generate YAML structure with:
3-5 modifiers per category
Photorealistic specifications
Brutal satirical elements
Create Mirror Universe Pete caption
Step 3: API Compatibility
Ensure compatibility:
Google Imagen - Extract prompt from YAML description
Google Veo - Use description + style fields
OpenAI GPT-4o - Feed YAML for concept refinement
Future MidJourney - Direct YAML-to-prompt conversion
Step 4: Testing Strategy
Unit Tests
YAML structure validation
Modifier application verification
Caption generation quality
Template selection logic
Integration Tests
End-to-end prompt generation
API compatibility verification
UI display correctness
Fallback mechanism testing
Quality Tests
Satire intensity validation
Photorealistic modifier presence
Visual metaphor clarity
Caption voice consistency
Migration Execution Plan
Week 1: Foundation
Create mirror_vision_engine.py
Implement MirrorVisionEngine class
Port modifier libraries from reference files
Create template system
Week 2: Core Integration
Update app.py with new engine
Modify prompt generation flow
Integrate clarification protocol
Update error handling
Week 3: Enhancement & UI
Update style_modifiers.py
Modify media_generator.py
Update HTML templates
Implement frontend changes
Week 4: Testing & Refinement
Execute test suite
Performance optimization
Documentation updates
User acceptance testing
Risk Mitigation
Technical Risks
YAML Processing - Ensure proper YAML parsing/generation
API Compatibility - Maintain backward compatibility
Performance - Monitor prompt generation speed
Memory Usage - Optimize modifier libraries
Functional Risks
Satire Level - Implement adjustable intensity
User Understanding - Provide clear documentation
Fallback Scenarios - Maintain PENTAGRAM as backup
Success Metrics
Prompt Quality
100% YAML structure validity
30+ fidelity modifiers per prompt
Photorealistic specifications present
Performance
< 500ms prompt generation time
< 50MB memory overhead
Zero API compatibility issues
User Experience
Clear satirical targeting
Brutal visual metaphors
Professional output quality
Documentation Requirements
Code Documentation
Inline comments for YAML structure
Modifier library references
Template usage examples
User Documentation
Mirror Vision framework explanation
Visual metaphor pattern guide
Caption voice examples
API Documentation
YAML-to-prompt conversion rules
Field mapping specifications
Integration examples
Rollback Plan
If issues arise:
Maintain PENTAGRAM code in separate branch
Feature flag for framework selection
A/B testing capability
Gradual rollout strategy
Conclusion
This migration will transform the Brand Deconstruction Station's image generation from basic structured prompts to sophisticated, photorealistic YAML-based prompts optimized for modern AI image generation. The Mirror Vision Prompt Crafter provides superior satirical intensity, visual metaphor clarity, and technical specifications that align with state-of-the-art image generation requirements.
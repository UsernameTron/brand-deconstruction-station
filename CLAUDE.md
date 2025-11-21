# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a dual-application Python project combining:

1. **Brand Deconstruction Station** (`app.py`) - AI-powered corporate brand vulnerability analysis with a cyberpunk terminal interface
2. **Neural Voice Synthesis Terminal** (`tts_app.py`) - Text-to-speech engine with dual API support (OpenAI + ElevenLabs)

Both applications feature cyberpunk-themed interfaces with matrix effects, neon glows, and terminal aesthetics using the Fira Code monospace font.

## Development Commands

### Brand Deconstruction Station
```bash
# Start main application (requires all 5 API keys)
python3 app.py

# Alternative launcher with dependency check
python3 run.py

# Shell launcher (macOS/Linux)
./start.sh
```

### TTS Terminal
```bash
# Start TTS application
python3 tts_app.py

# Shell launcher for TTS
./start_tts.sh
```

### Dependencies
```bash
# Install main app dependencies
pip install -r requirements.txt

# Install TTS-specific dependencies
pip install -r tts_requirements.txt

# Check Python version compatibility (3.8+ required)
python3 --version
```

### Desktop Integration
```bash
# Build and install desktop launcher
./build-and-install.sh

# Install to macOS dock
./install-to-dock.sh
```

## Application Architecture

### Brand Deconstruction Station (`app.py`)

**Core Components:**
- `BrandAnalysisEngine` class - Multi-API AI analysis engine requiring 5 API keys
- Multi-agent simulation system with 4 agents: CEO, Research, Performance, Image
- PENTAGRAM framework for image concept generation
- Flask web server on port 3000

**Key Features:**
- Website scraping and analysis
- Brand vulnerability scoring (0-10 scale)
- Satirical attack angle generation
- Export formats: JSON, PDF, HTML
- Real-time agent status monitoring

**API Requirements (ALL REQUIRED):**
- `OPENAI_API_KEY` - GPT-4o for image concepts
- `ANTHROPIC_API_KEY` - Claude integration
- `GOOGLE_API_KEY` - Google Gemini
- `HUGGINGFACE_API_TOKEN` - Hugging Face models
- `ELEVENLABS_API_KEY` - Voice synthesis

### TTS Terminal (`tts_app.py`)

**Core Components:**
- `VoiceSynthesisEngine` class - Dual-API TTS engine
- Flask web server on port 5003
- Base64 audio streaming
- Voice parameter controls

**Supported Services:**
- OpenAI TTS (voices: alloy, echo, fable, onyx, nova, shimmer)
- ElevenLabs (voices: rachel, drew, clyde, paul, domi, custom1)

## Configuration

### Required Environment Variables
For full functionality, set these environment variables:

#### Brand Deconstruction Station (Required)
- `OPENAI_API_KEY` - GPT-4o for image concepts (primary requirement)
- `ANTHROPIC_API_KEY` - Claude integration
- `GOOGLE_API_KEY` - Google Gemini and media generation
- `HUGGINGFACE_API_TOKEN` - Hugging Face models
- `ELEVENLABS_API_KEY` - Voice synthesis

#### Google Cloud (Optional, for Vertex AI)
- `GOOGLE_CLOUD_PROJECT` - GCP project ID (no default, must be explicit)
- `GOOGLE_CLOUD_LOCATION` - Region (default: us-central1)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON

### Environment Files
- `tts.env` - TTS application API keys (copy from `tts.env.example`)
- API keys can also be loaded from `/Users/cpconnor/Desktop/keys.env` (brand station)

### Key Differences Between Applications
- **Brand Station**: Requires ALL 5 API keys, fails without them
- **TTS Terminal**: Gracefully degrades, works with any available API keys

## File Structure

```
├── app.py                  # Main brand analysis application
├── tts_app.py             # TTS terminal application
├── run.py                 # Auto-setup launcher
├── start.sh               # Brand station launcher
├── start_tts.sh           # TTS launcher
├── requirements.txt       # Brand station dependencies
├── tts_requirements.txt   # TTS dependencies
├── templates/
│   ├── brand_station.html # Cyberpunk brand analysis UI
│   └── tts_interface.html # TTS terminal UI
├── static/                # Static web assets
├── desktop-launcher/      # Electron-based desktop app
└── data/                  # Analysis data storage
```

## API Integration Patterns

### Error Handling
Both applications implement graceful fallbacks:
- Brand station: Fails hard if APIs missing (by design)
- TTS terminal: Continues with available services

### Multi-API Architecture
The `BrandAnalysisEngine` class demonstrates a pattern for coordinating multiple AI services:
1. API key validation on startup
2. Service availability checking
3. Fallback mechanisms for failures
4. Structured prompt engineering (PENTAGRAM framework)

### PENTAGRAM Framework
Used in brand analysis for structured prompt generation:
- **P**urpose, **E**lements, **N**arrative, **T**one, **A**udience, **G**uidelines, **R**esults, **A**esthetics, **M**etaphors

## Testing

### API Connection Tests
```bash
python3 test_openai.py
python3 test_anthropic.py
python3 test_google_gemini.py
python3 test_huggingface.py
python3 test_elevenlabs.py
```

### Service Health Checks
- Brand Station: `/api/health`
- TTS Terminal: `/api/health`

## Cyberpunk UI Components

Both applications share design patterns:
- Matrix falling character backgrounds
- Neon glow effects (green, red, blue, purple)
- Terminal-style progress bars with shimmer
- Retro flicker animations
- Responsive grid layouts

## Deployment

### Local Development
- Brand Station: `http://localhost:3000`
- TTS Terminal: `http://localhost:5003`

### Production Notes
- Both apps support Gunicorn deployment
- Environment variables required for API keys
- Static file serving included
- CORS handling for web requests

## Security Considerations

- API keys must be provided via environment variables
- No hardcoded credentials in source
- Temporary file cleanup for audio generation
- Request validation and rate limiting built-in
- Web scraping respects robots.txt

## Performance Notes

- Threaded agent simulation prevents blocking
- Temporary audio file management
- Efficient CSS animations using hardware acceleration
- Background processing for analysis tasks
# 🎤 Neural Voice Synthesis Terminal

A cyberpunk-themed Text-to-Speech application that uses both OpenAI and ElevenLabs APIs for high-quality voice synthesis.

## Features

### 🤖 Dual AI Engines
- **OpenAI TTS**: Industry-standard text-to-speech with 6 neural voices
- **ElevenLabs**: Premium voice synthesis with advanced emotional control

### 🎵 Voice Options
**OpenAI Voices:**
- Alloy - Balanced Neural Matrix
- Echo - Resonance Algorithm  
- Fable - Narrative Protocol
- Onyx - Deep Bass Synthesis
- Nova - High-Energy Pattern
- Shimmer - Harmonic Cascade

**ElevenLabs Voices:**
- Rachel - Corporate Executive
- Drew - Technical Analyst
- Clyde - Security Officer
- Paul - System Administrator
- Domi - AI Coordinator

### 🎛️ Advanced Controls
- **Speed Control**: 0.25x to 4.0x (OpenAI)
- **Stability Matrix**: Fine-tune voice consistency (ElevenLabs)
- **Clarity Enhancement**: Adjust voice clarity (ElevenLabs)
- **Model Selection**: Standard vs HD quality (OpenAI)

### 🎮 Cyberpunk Interface
- Terminal-style UI with neon aesthetics
- Real-time status monitoring
- Audio visualizations
- Progress indicators
- System health checks

## Quick Start

### 1. Desktop Launcher (Recommended)
1. Double-click `LaunchTTSTerminal.command` on your desktop
2. The application will automatically:
   - Install dependencies
   - Start the server
   - Open your browser to http://localhost:5000

### 2. Manual Launch
```bash
# Navigate to project directory
cd /path/to/neural-voice-synthesis

# Run the startup script
./start_tts.sh

# Or run directly
python3 tts_app.py
```

## Setup

### Environment Configuration
1. Copy `tts.env` and add your API keys:
```bash
OPENAI_API_KEY=your-openai-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

### Dependencies
```bash
pip install -r tts_requirements.txt
```

Required packages:
- flask==2.3.3
- requests==2.31.0
- python-dotenv==1.0.0
- openai==1.3.0
- gunicorn==21.2.0
- werkzeug==2.3.7

## API Keys

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add to `tts.env` file

### ElevenLabs API Key
1. Visit [ElevenLabs](https://elevenlabs.io/)
2. Create an account or sign in
3. Go to Profile & API Key section
4. Copy your API key
5. Add to `tts.env` file

## Usage

### Basic Text-to-Speech
1. Enter text in the Neural Text Buffer (max 4096 characters)
2. Select your preferred service (OpenAI or ElevenLabs)
3. Choose voice and adjust settings
4. Click "INITIALIZE SYNTHESIS" or "EXECUTE SYNTHESIS"
5. Audio will auto-play and controls will appear

### Service Status
- **Green panels**: Service available and configured
- **Dimmed panels**: Service offline or not configured
- Status indicators show real-time connection status

## Technical Details

### Architecture
- **Backend**: Flask web server with RESTful API
- **Frontend**: Vanilla JavaScript with cyberpunk CSS
- **Audio**: Base64 encoding for seamless browser playback
- **Real-time**: WebSocket-style status updates

### API Endpoints
- `GET /api/services` - Check service availability
- `POST /api/synthesize/openai` - Generate OpenAI speech
- `POST /api/synthesize/elevenlabs` - Generate ElevenLabs speech
- `GET /api/health` - System health check

### Security Features
- Environment variable protection
- Input validation and sanitization
- Rate limiting ready
- Secure API key handling

## Troubleshooting

### Common Issues

**"Service Offline" Error:**
- Check API keys in `tts.env`
- Verify internet connection
- Ensure API keys are valid and have credits

**"Dependencies Missing" Error:**
```bash
pip3 install -r tts_requirements.txt
```

**Port Already in Use:**
- Change port in `tts_app.py` (default: 5000)
- Or kill existing process: `lsof -ti:5000 | xargs kill`

**Audio Not Playing:**
- Check browser auto-play settings
- Manually click play button
- Verify audio format support

### Performance Tips
- Use OpenAI TTS-1 for faster generation
- Use TTS-1-HD for higher quality
- ElevenLabs provides better emotional control
- Shorter texts generate faster

## Development

### Project Structure
```
neural-voice-synthesis/
├── tts_app.py              # Main Flask application
├── templates/
│   └── tts_interface.html  # Cyberpunk UI
├── tts_requirements.txt    # Python dependencies
├── tts.env                 # Environment configuration
├── start_tts.sh           # Startup script
└── LaunchTTSTerminal.command # Desktop launcher
```

### Adding New Voices
1. Update voice mappings in `VoiceSynthesisEngine`
2. Add options to HTML select elements
3. Test with both services

### Customizing UI
- Edit `templates/tts_interface.html`
- Modify CSS classes for different themes
- Add new control panels as needed

## Credits

Built with the same cyberpunk aesthetic and development patterns as:
- Brand Deconstruction Station
- Vector RAG Database

Inspired by 1980s terminal interfaces and modern AI capabilities.

---

**🎭 Neural Voice Synthesis Terminal** - Where retro-futurism meets cutting-edge AI.

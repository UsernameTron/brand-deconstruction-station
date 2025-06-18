#!/bin/bash
# 🎤 Neural Voice Synthesis Terminal Launcher for macOS/Linux

echo "🎤 Starting Neural Voice Synthesis Terminal..."
echo "📡 Server will be available at: http://localhost:5003"
echo "🎵 Interface: Cyberpunk TTS Terminal"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Source shell environment to get API keys
if [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc"
    echo "✅ Environment loaded from ~/.zshrc"
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found"
    echo "   Please install Python 3.8+ and try again"
    exit 1
fi

# Load TTS environment variables if file exists
if [ -f "tts.env" ]; then
    export $(grep -v '^#' tts.env | xargs)
    echo "✅ TTS environment loaded"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if dependencies are installed
python3 -c "import flask" 2>/dev/null || {
    echo "📦 Installing TTS dependencies..."
    python3 -m pip install -r tts_requirements.txt
    echo "✅ Dependencies installed"
}

# Check for API keys
echo "🔍 Checking API configuration..."
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo "⚠️  OpenAI API key not configured"
else
    echo "✅ OpenAI API key detected"
fi

if [ -z "$ELEVENLABS_API_KEY" ] || [ "$ELEVENLABS_API_KEY" = "your-elevenlabs-api-key-here" ]; then
    echo "⚠️  ElevenLabs API key not configured"
else
    echo "✅ ElevenLabs API key detected"
fi

# Start the application
echo ""
echo "🚀 Launching Neural Voice Synthesis Terminal..."
echo "🎤 Voice synthesis engines initializing"
echo "🤖 AI TTS agents online"
echo ""
echo "="*50
echo "Press Ctrl+C to stop the server"
echo "="*50
echo ""

python3 tts_app.py

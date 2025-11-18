#!/bin/bash
# 🎭 Brand Deconstruction Station Launcher for macOS/Linux

echo "🎭 Starting Brand Deconstruction Station..."
echo "📡 Server will be available at: http://localhost:3000"
echo "🎮 Interface: Cyberpunk Terminal"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Load API keys from Desktop/keys.env if not already set
if [ -f "/Users/cpconnor/Desktop/keys.env" ]; then
    echo "📋 Loading API keys from Desktop/keys.env..."
    set -a  # automatically export all variables
    source "/Users/cpconnor/Desktop/keys.env"
    set +a
    echo "✅ API keys loaded"
else
    echo "⚠️  API keys file not found at /Users/cpconnor/Desktop/keys.env"
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found"
    echo "   Please install Python 3.8+ and try again"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if dependencies are installed
python3 -c "import flask" 2>/dev/null || {
    echo "📦 Installing dependencies..."
    python3 -m pip install -r requirements.txt
    echo "✅ Dependencies installed"
}

# Check for required API keys
echo "🔍 Checking API keys..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OpenAI API key not found"
    exit 1
else
    echo "✅ OpenAI API key found"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: Anthropic API key not found"
    exit 1
else
    echo "✅ Anthropic API key found"
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: Google API key not found"
    exit 1
else
    echo "✅ Google API key found"
fi

if [ -z "$HUGGINGFACE_API_TOKEN" ]; then
    echo "❌ Error: HuggingFace token not found"
    exit 1
else
    echo "✅ HuggingFace token found"
fi

if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo "❌ Error: ElevenLabs API key not found"
    exit 1
else
    echo "✅ ElevenLabs API key found"
fi

echo "✅ All API keys verified"

# Start the application
echo ""
echo "🚀 Launching application..."
echo "🎯 Target acquisition ready"
echo "🤖 AI agents online"
echo ""
echo "="*50
echo "Press Ctrl+C to stop the server"
echo "="*50
echo ""

# Check if we should auto-open browser (skip if called from desktop launcher)
if [ "$SKIP_BROWSER" != "true" ]; then
    # Start Flask app in background and open browser
    python3 app.py &
    FLASK_PID=$!

    # Wait for server to start then open browser
    echo "⏳ Waiting for server to start..."
    sleep 3

    # Open browser
    echo "🌐 Opening browser at http://localhost:3000..."
    if command -v open &> /dev/null; then
        # macOS
        open http://localhost:3000
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open http://localhost:3000
    elif command -v start &> /dev/null; then
        # Windows
        start http://localhost:3000
    else
        echo "⚠️  Could not auto-open browser. Please navigate to http://localhost:3000"
    fi

    echo "✅ Browser launched! App should be loading..."
    echo ""

    # Wait for Flask process to finish
    wait $FLASK_PID
else
    # Just start the Flask app (browser will be opened by launcher)
    python3 app.py
fi

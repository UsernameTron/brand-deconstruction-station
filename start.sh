#!/bin/bash
# 🎭 Brand Deconstruction Station Launcher for macOS/Linux

echo "🎭 Starting Brand Deconstruction Station..."
echo "📡 Server will be available at: http://localhost:3000"
echo "🎮 Interface: Cyberpunk Terminal"
echo ""

# Change to script directory
cd "$(dirname "$0")"

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

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Running in mock mode (set OPENAI_API_KEY for real AI analysis)"
else
    echo "✅ OpenAI API key detected - Real AI analysis enabled"
fi

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

python3 app.py

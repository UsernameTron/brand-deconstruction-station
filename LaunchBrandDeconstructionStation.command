#!/bin/bash
# MacOS launcher for Brand Deconstruction Station
# Enhanced with better error handling and debugging

# Change to script directory
cd "$(dirname "$0")"

# Clear screen for clean output
clear

echo "=================================================="
echo "     BRAND DECONSTRUCTION STATION LAUNCHER"
echo "=================================================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
echo "1️⃣  Checking Python installation..."
if ! command_exists python3; then
    echo "❌ Python 3 is not installed!"
    echo "   Please install Python 3.8 or higher from python.org"
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "   ✅ Python $PYTHON_VERSION found"
echo ""

# Check if keys.env exists
echo "2️⃣  Checking API keys file..."
if [ ! -f "/Users/cpconnor/Desktop/keys.env" ]; then
    echo "❌ API keys file not found!"
    echo "   Expected location: /Users/cpconnor/Desktop/keys.env"
    echo ""
    echo "   Please create this file with your API keys:"
    echo "   OPENAI_API_KEY=your-key-here"
    echo "   ANTHROPIC_API_KEY=your-key-here"
    echo "   GOOGLE_API_KEY=your-key-here"
    echo "   HUGGINGFACE_API_TOKEN=your-key-here"
    echo "   ELEVENLABS_API_KEY=your-key-here"
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi
echo "   ✅ API keys file found"
echo ""

# Load and validate API keys
echo "3️⃣  Loading API keys..."
set -a  # automatically export all variables
source "/Users/cpconnor/Desktop/keys.env"
set +a

# Check each required API key
missing_keys=()
[ -z "$OPENAI_API_KEY" ] && missing_keys+=("OPENAI_API_KEY")
[ -z "$ANTHROPIC_API_KEY" ] && missing_keys+=("ANTHROPIC_API_KEY")
[ -z "$GOOGLE_API_KEY" ] && missing_keys+=("GOOGLE_API_KEY")
[ -z "$HUGGINGFACE_API_TOKEN" ] && missing_keys+=("HUGGINGFACE_API_TOKEN")
[ -z "$ELEVENLABS_API_KEY" ] && missing_keys+=("ELEVENLABS_API_KEY")

if [ ${#missing_keys[@]} -ne 0 ]; then
    echo "❌ Missing required API keys:"
    for key in "${missing_keys[@]}"; do
        echo "   • $key"
    done
    echo ""
    echo "   Please add these to /Users/cpconnor/Desktop/keys.env"
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi
echo "   ✅ All API keys loaded"
echo ""

# Check dependencies
echo "4️⃣  Checking Python dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "   ⚠️  Flask not installed. Installing dependencies..."
    pip3 install -r requirements.txt
fi
echo "   ✅ Dependencies verified"
echo ""

# Start the application
echo "5️⃣  Starting Brand Deconstruction Station..."
echo "=================================================="
echo ""

# Export skip browser flag since we'll handle it manually
export SKIP_BROWSER=false

# Start the Flask server
echo "Starting Flask server on port 3000..."
echo ""

# Run the app directly with proper error handling
python3 app.py 2>&1 || {
    echo ""
    echo "❌ Application failed to start!"
    echo "   Check the error messages above for details"
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
}
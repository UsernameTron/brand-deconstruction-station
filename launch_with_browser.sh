#!/bin/bash
# 🎭 Brand Deconstruction Station - Direct Browser Launcher

echo "🎭 Brand Deconstruction Station - Browser Launcher"
echo "📡 Starting Flask server and opening browser..."
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Source API keys from Desktop/keys.env if it exists
if [ -f "/Users/cpconnor/Desktop/keys.env" ]; then
    echo "📋 Loading API keys from Desktop/keys.env..."
    set -a  # automatically export all variables
    source "/Users/cpconnor/Desktop/keys.env"
    set +a
    echo "✅ API keys loaded"
else
    echo "⚠️  API keys file not found at /Users/cpconnor/Desktop/keys.env"
    echo "❌ Cannot start without API keys. Please create /Users/cpconnor/Desktop/keys.env"
    echo "   See API_SETUP_GUIDE.md for instructions"
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

# Pre-validate API keys before starting server
echo "🔍 Validating API keys..."
missing_keys=()

if [ -z "$OPENAI_API_KEY" ]; then
    missing_keys+=("OPENAI_API_KEY")
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    missing_keys+=("ANTHROPIC_API_KEY")
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    missing_keys+=("GOOGLE_API_KEY")
fi

if [ -z "$HUGGINGFACE_API_TOKEN" ]; then
    missing_keys+=("HUGGINGFACE_API_TOKEN")
fi

if [ -z "$ELEVENLABS_API_KEY" ]; then
    missing_keys+=("ELEVENLABS_API_KEY")
fi

if [ ${#missing_keys[@]} -ne 0 ]; then
    echo "❌ Missing required API keys:"
    for key in "${missing_keys[@]}"; do
        echo "   • $key"
    done
    echo ""
    echo "📋 Please add these keys to /Users/cpconnor/Desktop/keys.env"
    echo "   See API_SETUP_GUIDE.md for instructions"
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

echo "✅ All API keys validated"

# Start Flask server in background
echo "🚀 Starting Flask server..."
export SKIP_BROWSER=true
./start.sh &
SERVER_PID=$!

# Function to check if server is running and responding
check_server() {
    curl -s http://localhost:3000/api/health > /dev/null 2>&1
    return $?
}

# Function to check if server process is still alive
server_alive() {
    kill -0 $SERVER_PID 2>/dev/null
    return $?
}

# Wait for server to be ready
echo "⏳ Waiting for server to be ready..."
for i in {1..60}; do
    if ! server_alive; then
        echo "❌ Server process died unexpectedly"
        echo "   Check the terminal output above for error details"
        echo ""
        echo "Press any key to exit..."
        read -n 1
        exit 1
    fi
    
    if check_server; then
        echo "✅ Server is ready and responding!"
        break
    fi
    
    if [ $i -eq 60 ]; then
        echo "⚠️  Server taking too long to respond"
        echo "   The server might be starting but not responding to health checks"
        echo "   Attempting browser launch anyway..."
        break
    fi
    sleep 1
done

# Small additional delay to ensure complete startup
sleep 2

# Only open browser if server process is still alive
if server_alive; then
    echo "🌐 Opening browser..."
    if /usr/bin/open http://localhost:3000 2>/dev/null; then
        echo "✅ Browser launched successfully!"
    else
        echo "⚠️  Browser launch failed. Please manually navigate to:"
        echo "    http://localhost:3000"
    fi
    
    echo ""
    echo "🎮 Brand Deconstruction Station is now running!"
    echo "📱 Check your browser for the cyberpunk interface"
    echo "🛑 Press Ctrl+C in Terminal to stop the server"
    echo ""
    
    # Wait for the server process
    wait $SERVER_PID
else
    echo "❌ Server failed to start properly"
    echo "   Please check the error messages above"
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi
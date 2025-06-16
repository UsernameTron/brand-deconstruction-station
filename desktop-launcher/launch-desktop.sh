#!/bin/bash
# 🎭 Brand Deconstruction Station - Desktop Launcher

echo "🎭 Brand Deconstruction Station - Desktop App"
echo "🖥️  Launching Electron wrapper..."
echo ""

# Change to desktop launcher directory
cd "$(dirname "$0")"

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Electron dependencies..."
    npm install
    echo ""
fi

# Check if Python dependencies are installed in parent directory
cd ..
python3 -c "import flask" 2>/dev/null || {
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    echo ""
}

# Return to launcher directory and start app
cd desktop-launcher
echo "🚀 Starting desktop application..."
echo "🎮 Brand Deconstruction Station will open in desktop window"
echo ""

npm start

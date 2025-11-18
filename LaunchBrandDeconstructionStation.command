#!/bin/bash
# MacOS launcher for Brand Deconstruction Station
cd "$(dirname "$0")"

echo "🎭 Launching Brand Deconstruction Station..."
echo "📡 Opening Terminal with server and browser launcher..."

# Use the dedicated launch script that handles both server and browser
open -a Terminal ./launch_with_browser.sh

echo "✅ Brand Deconstruction Station is starting!"
echo "📱 Terminal window will open showing progress"
echo "🌐 Browser will automatically open when server is ready"
echo ""
echo "🛑 To stop: Close the Terminal window or press Ctrl+C in Terminal"

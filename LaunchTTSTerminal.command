#!/bin/bash
# MacOS launcher for Neural Voice Synthesis Terminal

# Project directory
PROJECT_DIR="/Users/cpconnor/projects/brand-deconstruction-station-standalone"

# Change to project directory
cd "$PROJECT_DIR"

# Make start_tts.sh executable (in case it's not)
chmod +x start_tts.sh

# Run the TTS script directly in this terminal window
echo "🎤 Launching Neural Voice Synthesis Terminal..."
echo "📡 Opening http://localhost:5002 in your browser shortly..."
./start_tts.sh &

# Wait a few seconds for the server to start
sleep 3

# Open the browser
open http://localhost:5002

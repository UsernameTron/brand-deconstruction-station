#!/bin/bash
# MacOS launcher for Brand Deconstruction Station
cd "$(dirname "$0")"

# Source API keys from Desktop/keys.env if it exists
if [ -f "/Users/cpconnor/Desktop/keys.env" ]; then
    set -a  # automatically export all variables
    source "/Users/cpconnor/Desktop/keys.env"
    set +a
fi

echo "🎭 Launching Brand Deconstruction Station..."
echo "📡 Opening http://localhost:3000 in your browser shortly..."

open -a Terminal ./start.sh

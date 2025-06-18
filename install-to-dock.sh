#!/bin/bash
# 🎭 Brand Deconstruction Station - Dock Installation

echo "🎭 Installing Brand Deconstruction Station to macOS Dock..."

# Add to dock using dockutil if available, otherwise provide instructions
if command -v dockutil &> /dev/null; then
    echo "📍 Adding to Dock with dockutil..."
    dockutil --add "/Applications/Brand Deconstruction Station.app"
    echo "✅ Added to Dock!"
else
    echo "📋 Manual Dock Installation:"
    echo "1. Open Finder"
    echo "2. Go to Applications folder"
    echo "3. Find 'Brand Deconstruction Station'"
    echo "4. Drag it to your Dock"
    echo ""
    echo "💡 Or install dockutil for automatic dock management:"
    echo "   brew install dockutil"
    echo ""
    echo "🎯 The app is now in your Applications folder and on your Desktop!"
fi

echo ""
echo "🚀 Brand Deconstruction Station is ready to launch!"
echo "📍 Locations:"
echo "   • Applications: /Applications/Brand Deconstruction Station.app"
echo "   • Desktop: ~/Desktop/Brand Deconstruction Station.app"
echo ""
echo "🎮 Click the app icon to start deconstructing brands with cyberpunk style!"

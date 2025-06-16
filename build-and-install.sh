#!/bin/bash
# 🎭 Brand Deconstruction Station - Build and Install Desktop App

echo "🎭 Brand Deconstruction Station - Desktop App Builder"
echo "🔧 Building and installing native macOS application..."
echo ""

# Navigate to desktop launcher
cd desktop-launcher

# Build the app
echo "📦 Building macOS application..."
npm run build:mac

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    
    # Install to Applications
    echo "📲 Installing to Applications folder..."
    cp -r "dist/mac-arm64/Brand Deconstruction Station.app" /Applications/
    
    # Create desktop shortcut
    echo "🖥️ Creating desktop shortcut..."
    ln -sf "/Applications/Brand Deconstruction Station.app" ~/Desktop/
    
    echo ""
    echo "🎉 Installation Complete!"
    echo "📍 App installed to:"
    echo "   • /Applications/Brand Deconstruction Station.app"
    echo "   • ~/Desktop/Brand Deconstruction Station.app"
    echo ""
    echo "🚀 Launch options:"
    echo "   • Double-click the desktop icon"
    echo "   • Open from Applications folder"
    echo "   • Search 'Brand Deconstruction' in Spotlight"
    echo "   • Add to Dock by dragging from Applications"
    echo ""
    echo "🎮 Ready to deconstruct brands with cyberpunk style!"
    
else
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi

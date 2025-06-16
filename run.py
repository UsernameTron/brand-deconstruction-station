#!/usr/bin/env python3
"""
🎭 Brand Deconstruction Station - Automatic Setup & Launch
Installs dependencies and starts the cyberpunk terminal interface
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def print_banner():
    """Display cyberpunk-style banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🎭 BRAND DECONSTRUCTION STATION                          ║
    ║     Corporate Vulnerability Analysis Engine                  ║
    ║                                                              ║
    ║     🤖 AI-Powered Satirical Brand Analysis                   ║
    ║     🎮 Cyberpunk Terminal Interface                          ║
    ║     ⚡ Standalone Application                                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print("⚠️  Warning: Some dependencies may not have installed correctly")
            print(f"   Error output: {result.stderr}")
            
    except subprocess.CalledProcessError:
        print("❌ Error: pip not found. Please install pip first.")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: requirements.txt not found")
        sys.exit(1)

def check_optional_dependencies():
    """Check for optional dependencies and suggest alternatives"""
    print("\n🔍 Checking optional dependencies...")
    
    # Check for OpenAI API key
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API key found - Real AI analysis enabled")
    else:
        print("⚠️  OpenAI API key not found - Running in mock mode")
        print("   Set OPENAI_API_KEY environment variable for real AI analysis")
    
    # Check for GPU availability (for potential future image generation)
    try:
        import torch
        if torch.cuda.is_available():
            print("✅ CUDA GPU detected - Enhanced performance available")
        else:
            print("ℹ️  No CUDA GPU detected - CPU mode will be used")
    except ImportError:
        print("ℹ️  PyTorch not installed - Mock image generation will be used")

def create_launcher_script():
    """Create platform-specific launcher script"""
    system = platform.system()
    
    if system in ['Darwin', 'Linux']:  # macOS and Linux
        script_content = """#!/bin/bash
# Brand Deconstruction Station Launcher

echo "🎭 Starting Brand Deconstruction Station..."
echo "📡 Server will be available at: http://localhost:3000"
echo "🎮 Interface: Cyberpunk Terminal"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if dependencies are installed
python3 -c "import flask" 2>/dev/null || {
    echo "📦 Installing dependencies..."
    python3 -m pip install -r requirements.txt
}

# Start the application
echo "🚀 Launching application..."
python3 app.py
"""
        
        script_path = "start.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        print(f"✅ Created launcher script: {script_path}")
        
    elif system == 'Windows':
        script_content = """@echo off
REM Brand Deconstruction Station Launcher

echo 🎭 Starting Brand Deconstruction Station...
echo 📡 Server will be available at: http://localhost:3000
echo 🎮 Interface: Cyberpunk Terminal
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
    echo ✅ Virtual environment activated
)

REM Check if dependencies are installed
python -c "import flask" 2>nul || (
    echo 📦 Installing dependencies...
    python -m pip install -r requirements.txt
)

REM Start the application
echo 🚀 Launching application...
python app.py

pause
"""
        
        script_path = "start.bat"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"✅ Created launcher script: {script_path}")

def setup_environment():
    """Setup environment variables and configuration"""
    print("\n⚙️  Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        env_content = """# Brand Deconstruction Station Configuration

# OpenAI API Key (optional - runs in mock mode without this)
# OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Server Configuration
HOST=0.0.0.0
PORT=3000
"""
        env_file.write_text(env_content)
        print("✅ Created .env configuration file")
    else:
        print("ℹ️  Using existing .env configuration")

def launch_application():
    """Launch the Flask application"""
    print("\n🚀 Launching Brand Deconstruction Station...")
    print("📡 Server will be available at: http://localhost:3000")
    print("🎮 Interface: Cyberpunk Terminal")
    print("🤖 AI Agents: Ready for deployment")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(host='0.0.0.0', port=3000, debug=False, threaded=True)
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("   Make sure all dependencies are installed correctly")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("💀 Brand Deconstruction Station offline")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main setup and launch function"""
    print_banner()
    
    # System checks
    check_python_version()
    
    # Dependency management
    install_dependencies()
    check_optional_dependencies()
    
    # Environment setup
    setup_environment()
    create_launcher_script()
    
    print("\n" + "="*60)
    print("🎯 Setup complete! Ready to deconstruct brands.")
    print("="*60)
    
    # Ask user if they want to launch now
    try:
        response = input("\n🚀 Launch Brand Deconstruction Station now? (y/n): ").lower()
        if response in ['y', 'yes', '']:
            launch_application()
        else:
            print("\n📋 To launch later, run:")
            print("   python3 run.py")
            print("   or use the created launcher script")
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")

if __name__ == "__main__":
    main()

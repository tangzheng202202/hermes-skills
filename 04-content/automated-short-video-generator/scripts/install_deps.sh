#!/bin/bash
# Automated Short Video Generator - Dependency Installer

set -e

echo "🔍 Checking and installing dependencies..."
echo ""

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 required"
    echo "   macOS: brew install python3"
    echo "   Ubuntu: sudo apt install python3"
    exit 1
fi
echo "✅ Python3 installed"

# Check pip3
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 required"
    exit 1
fi
echo "✅ pip3 installed"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "🔄 Installing FFmpeg..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ Homebrew required: https://brew.sh"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install -y ffmpeg
    else
        echo "❌ Please install FFmpeg manually: https://ffmpeg.org/download.html"
        exit 1
    fi
fi
echo "✅ FFmpeg installed"

# Install Python dependencies
echo ""
echo "🔄 Installing Python packages..."
pip3 install -q edge-tts pillow

if python3 -c "import PIL; import edge_tts" 2>/dev/null; then
    echo "✅ Python packages installed"
else
    echo "❌ Package installation failed"
    exit 1
fi

echo ""
echo "🎉 All dependencies ready!"
echo "Run: python3 auto_video_generator.py"

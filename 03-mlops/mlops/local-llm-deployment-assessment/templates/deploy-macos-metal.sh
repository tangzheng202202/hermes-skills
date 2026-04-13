#!/bin/bash
# Mac Apple Silicon LLM Deployment Script
# Generated based on hardware assessment

set -e

MODEL=${1:-"gemma3:12b"}
MODEL_URL=${2:-""}
QUANT="${3:-Q4_K_M}"

echo "🚀 Deploying ${MODEL} (${QUANT}) on Mac Apple Silicon"
echo "================================================"

# Detect hardware
echo "📊 Detecting hardware..."
CPU=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Unknown")
MEM_GB=$(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))
echo "  CPU: ${CPU}"
echo "  Memory: ${MEM_GB}GB"

# Check memory sufficiency
MODEL_SIZE_GB=8  # Default for 12B Q4
if [[ "${MODEL}" == *"27b"* ]] || [[ "${MODEL}" == *"27B"* ]]; then
    MODEL_SIZE_GB=16
elif [[ "${MODEL}" == *"70b"* ]] || [[ "${MODEL}" == *"70B"* ]]; then
    MODEL_SIZE_GB=40
fi

if [ "$MEM_GB" -lt "$((MODEL_SIZE_GB / 2))" ]; then
    echo "⚠️  WARNING: ${MEM_GB}GB RAM may be insufficient for ${MODEL}"
    echo "   Recommended: ${MODEL_SIZE_GB}GB+"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

# Install dependencies
echo "📦 Checking dependencies..."
if ! command -v cmake &> /dev/null; then
    echo "Installing cmake..."
    brew install cmake
fi

# Setup directories
mkdir -p ~/llm-models
cd ~/llm-models

# Build llama.cpp with Metal
echo "🔧 Building llama.cpp (Metal backend)..."
if [ ! -d "llama.cpp" ]; then
    git clone https://github.com/ggerganov/llama.cpp.git
fi
cd llama.cpp
rm -rf build
mkdir build && cd build

cmake .. \
    -DLLAMA_METAL=ON \
    -DLLAMA_METAL_EMBED_LIBRARY=ON \
    -DCMAKE_OSX_ARCHITECTURES=arm64 \
    -DCMAKE_BUILD_TYPE=Release

make -j$(sysctl -n hw.ncpu)

echo "✓ Build complete"

# Download model if URL provided
if [ -n "$MODEL_URL" ]; then
    cd ~/llm-models
    MODEL_FILE="${MODEL//:/_}.gguf"
    if [ ! -f "$MODEL_FILE" ]; then
        echo "📥 Downloading model..."
        wget -c "$MODEL_URL" -O "$MODEL_FILE"
    fi
fi

# Create launch script
cat > ~/llm-models/run-${MODEL//:/-}.sh << EOF
#!/bin/bash
cd ~/llm-models/llama.cpp/build/bin
./llama-server \\
    -m ~/llm-models/${MODEL_FILE} \\
    -c 4096 \\
    --threads $(($(sysctl -n hw.ncpu) - 2)) \\
    --gpu-layers 99 \\
    --metal \\
    --host 0.0.0.0 \\
    --port 8080 \\
    --flash-attn
EOF

chmod +x ~/llm-models/run-${MODEL//:/-}.sh

echo ""
echo "✅ Deployment complete!"
echo "   Launch: ~/llm-models/run-${MODEL//:/-}.sh"
echo "   API: http://localhost:8080"

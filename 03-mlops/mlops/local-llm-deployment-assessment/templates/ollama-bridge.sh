#!/bin/bash
# Ollama Local Model Bridge Configuration
# Sets up environment variables for various tools to use Ollama

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
MODEL="${1:-gemma3:12b}"

echo "🌉 Ollama Bridge Configuration"
echo "==============================="
echo "Model: ${MODEL}"
echo "URL: ${OLLAMA_URL}"
echo ""

# Check Ollama status
if ! curl -s "${OLLAMA_URL}/api/tags" > /dev/null 2>&1; then
    echo "❌ Ollama not running. Starting..."
    open -a Ollama  # macOS
    # systemctl start ollama  # Linux
    sleep 3
fi

# Check if model exists
if ! curl -s "${OLLAMA_URL}/api/tags" | grep -q "${MODEL}"; then
    echo "⚠️  Model ${MODEL} not found. Available models:"
    curl -s "${OLLAMA_URL}/api/tags" | \
        python3 -c "import sys,json; d=json.load(sys.stdin); [print('  -',m['name']) for m in d['models']]" 2>/dev/null
    echo ""
    echo "Pull with: ollama pull ${MODEL}"
    return 1
fi

echo "✓ Ollama running, model available"
echo ""

# ============================================
# OpenAI-compatible API settings (universal)
# ============================================
export OPENAI_API_KEY="ollama"
export OPENAI_BASE_URL="${OLLAMA_URL}/v1"
export OPENAI_MODEL="${MODEL}"

# ============================================
# Tool-specific configurations
# ============================================

# Aider (AI pair programming)
export AIDER_MODEL="ollama/${MODEL}"
export OLLAMA_API_BASE="${OLLAMA_URL}"

# Continue (VS Code extension)
# Config in ~/.continue/config.json

# ShellGPT
export OPENAI_API_HOST="${OLLAMA_URL}/v1"

# Fabric
export OPENAI_API_KEY="ollama"
export OPENAI_BASE_URL="${OLLAMA_URL}/v1"

# LangChain/LlamaIndex
export OLLAMA_BASE_URL="${OLLAMA_URL}"

echo "✅ Environment variables set:"
echo "  OPENAI_API_KEY: ollama"
echo "  OPENAI_BASE_URL: ${OLLAMA_URL}/v1"
echo "  AIDER_MODEL: ollama/${MODEL}"
echo ""
echo "🎯 Usage examples:"
echo "  Python: OpenAI(base_url='${OLLAMA_URL}/v1', api_key='ollama')"
echo "  Aider: aider --model ollama/${MODEL}"
echo "  curl: curl ${OLLAMA_URL}/api/generate -d '{\"model\":\"${MODEL}\",\"prompt\":\"Hello\"}'"
echo ""

# Create quick alias
alias local-ai="curl -s ${OLLAMA_URL}/api/generate -d '{\"model\":\"${MODEL}\",\"prompt\":\"'\$1'\",\"stream\":false}' 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin)[\"response\"])'"

echo "✓ Alias created: local-ai 'your question'"

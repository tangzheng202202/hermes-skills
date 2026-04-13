---
name: local-llm-deployment
description: "Deploy local LLMs (Llama, Gemma, Qwen, etc.) optimized for user's hardware. Detects CPU/RAM/GPU, recommends appropriate model size and quantization, generates deployment scripts for Ollama/llama.cpp/vLLM."
---

# Local LLM Deployment Skill

Deploy local Large Language Models optimized for the user's hardware configuration.

---

## Workflow

### Step 1: Hardware Detection

```bash
# Detect system specs
uname -a  # OS/Architecture
sysctl -n machdep.cpu.brand_string  # CPU (macOS)
cat /proc/cpuinfo | grep "model name" | head -1  # CPU (Linux)
system_profiler SPHardwareDataType | grep "Memory:"  # RAM (macOS)
free -h  # RAM (Linux)
system_profiler SPDisplaysDataType | grep -E "(Chipset|VRAM)"  # GPU (macOS)
nvidia-smi  # GPU (NVIDIA)
df -h /  # Disk space
```

### Step 2: Determine Feasibility

| Memory | Max Model Size | Recommended Quantization |
|--------|---------------|-------------------------|
| 8 GB | 7B | Q4_K_M |
| 16 GB | 12B-13B | Q4_K_M (12B) or Q3_K_L (13B) |
| 24 GB | 27B-30B | Q4_K_M |
| 32 GB+ | 70B | Q4_K_M or Q5_K_M |
| 64 GB+ | 70B-110B | Q5_K_M - Q8_0 |

**Formula**: Model RAM ≈ (Parameters × Quantization bits) / 8
- Q4 = 4 bits → 27B model ≈ 13.5GB + overhead
- Q5 = 5 bits → 27B model ≈ 17GB + overhead
- Q8 = 8 bits → 27B model ≈ 27GB + overhead

### Step 3: Model Selection

**Recommended Models by Use Case**:

| Use Case | Model | Size | Best For |
|----------|-------|------|----------|
| General Chat | Gemma 3 12B | 12B | Balanced, multilingual |
| Code | Qwen 2.5 Coder 14B | 14B | Programming tasks |
| Chinese | Qwen 2.5 14B/32B | 14-32B | Chinese optimization |
| Long Context | Llama 3.1 8B | 8B | 128K context |
| Reasoning | DeepSeek-R1 14B | 14B | Math/coding |

### Step 4: Check Existing Installation

```bash
# Check Ollama
which ollama
ollama --version
ollama list  # See installed models
ps aux | grep ollama  # Check if running

# Test API
curl http://localhost:11434/api/tags
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:12b",
  "prompt": "test",
  "stream": false
}'
```

### Step 5: Generate Deployment Scripts

**For Ollama (Recommended for beginners)**:
```bash
# Pull model
ollama pull gemma3:12b

# Create Modelfile for customization
cat > Modelfile << 'EOF'
FROM gemma3:12b
PARAMETER temperature 0.7
PARAMETER top_p 0.95
PARAMETER num_ctx 8192
SYSTEM You are a helpful AI assistant.
EOF

ollama create my-gemma -f Modelfile
```

**For llama.cpp (Best performance)**:
```bash
# Compile with Metal (Apple Silicon) or CUDA (NVIDIA)
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir build && cd build

cmake .. -DLLAMA_METAL=ON -DCMAKE_OSX_ARCHITECTURES=arm64  # macOS Apple Silicon
cmake .. -DLLAMA_CUDA=ON  # NVIDIA GPU
make -j$(sysctl -n hw.ncpu)

# Download GGUF
huggingface-cli download bartowski/gemma-3-12b-it-GGUF \
  gemma-3-12b-it-Q4_K_M.gguf --local-dir .

# Run
./llama-server -m gemma-3-12b-it-Q4_K_M.gguf \
  -c 8192 --gpu-layers 99 --metal --port 8080
```

### Step 6: API Integration Setup

**OpenAI-compatible endpoint**:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="gemma3:12b",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Direct Ollama API**:
```python
import requests

def chat(prompt):
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma3:12b",
        "prompt": prompt,
        "stream": False
    })
    return r.json()["response"]
```

---

## Troubleshooting

### Out of Memory
- Reduce context size: `--ctx-size 4096` instead of 8192
- Lower GPU layers: `--gpu-layers 50` instead of 99
- Use smaller quantization: Q3 instead of Q4
- Enable swap/memory compression

### Slow Generation
- Check GPU utilization: `nvidia-smi` or `sudo powermetrics` (macOS)
- Increase batch size: `--batch-size 1024`
- Enable Flash Attention: `--flash-attn`
- Use quantized KV cache

### Model Not Found
```bash
# List available
ollama list

# Pull if missing
ollama pull gemma3:12b
```

---

## Security

⚠️ **Never expose Ollama directly to internet**

Options for remote access:
1. SSH tunnel: `ssh -L 11434:localhost:11434 user@host`
2. VPN/ZeroTier
3. Cloudflare Tunnel with auth
4. Nginx reverse proxy with Basic Auth

---

## Tools

- **Ollama**: Easiest setup
- **llama.cpp**: Best performance, most control
- **vLLM**: Production serving
- **LM Studio**: GUI for beginners
- **text-generation-webui**: Feature-rich GUI

---

## Requirements

- Python 3.8+
- For Apple Silicon: Xcode Command Line Tools
- For NVIDIA: CUDA toolkit
- 8GB+ RAM (16GB+ recommended)
- 10GB+ free disk space per model

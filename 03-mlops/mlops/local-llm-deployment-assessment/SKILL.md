---
name: local-llm-deployment-assessment
description: "Assess local hardware capabilities and generate optimized LLM deployment scripts. Detects CPU, RAM, GPU, and recommends appropriate model sizes, quantization levels, and deployment configurations."
---

# Local LLM Deployment Assessment

Assess hardware capabilities and generate custom deployment configurations for local LLMs.

## When to Use

- User wants to deploy a large model (7B+) locally
- Need to check if hardware can support the requested model
- Generate optimized deployment scripts based on detected hardware
- Recommend alternative models if hardware is insufficient

## Workflow

### Step 1: Hardware Detection

Detect system specifications:

```bash
# macOS
system_profiler SPHardwareDataType
system_profiler SPDisplaysDataType
sysctl -n hw.memsize

# Linux  
cat /proc/cpuinfo | grep "model name"
free -h
nvidia-smi  # if NVIDIA GPU

# General
df -h /
uname -m  # architecture
```

### Step 2: Feasibility Analysis

Calculate if requested model fits:

| Model Size | Q4_K_M | Q4_0 | Q3_K_L | Q5_K_M | Q8_0 |
|-----------|--------|------|--------|--------|------|
| 7B  | ~4GB | ~4GB | ~3GB | ~5GB | ~7GB |
| 13B | ~8GB | ~7GB | ~6GB | ~9GB | ~13GB |
| 27B | ~16GB| ~14GB| ~11GB| ~19GB| ~30GB |
| 70B | ~40GB| ~35GB| ~28GB| ~48GB| ~75GB |

**Rule of thumb**: Need 1.2-1.5x model size in RAM/VRAM for comfortable operation.

### Step 3: Recommend Alternatives (if needed)

If requested model is too large:

1. **Same family, smaller size**: Gemma 3 27B → Gemma 3 12B
2. **More aggressive quantization**: Q4 → Q3 (slight quality loss)
3. **Different architecture**: DeepSeek-V2 16B instead of 27B

### Step 4: Generate Deployment Scripts

Create tailored scripts based on hardware:

**For macOS Apple Silicon**:
- Use `llama.cpp` with Metal (`-DLLAMA_METAL=ON`)
- Compile for `arm64` architecture
- Use all GPU layers (`--gpu-layers 99`)

**For NVIDIA GPU**:
- Use `llama.cpp` with CUDA
- Or use `vLLM` for high-throughput serving

**For CPU-only**:
- Use Q4_0 or Q3_K_L quantization
- Reduce context size (`-c 2048`)
- Limit threads appropriately

### Step 5: Tool-Specific Configuration

Configure popular tools to use local model:

**Ollama** (recommended for beginners):
```bash
ollama pull gemma3:12b
ollama run gemma3:12b
```

**Continue (VS Code)**:
```json
{
  "title": "Gemma 3 12B (本地)",
  "provider": "ollama",
  "model": "gemma3:12b",
  "apiBase": "http://localhost:11434"
}
```

**Aider**:
```bash
export AIDER_MODEL="ollama/gemma3:12b"
aider
```

**OpenAI-compatible API**:
```bash
export OPENAI_API_KEY="ollama"
export OPENAI_BASE_URL="http://localhost:11434/v1"
```

## Common Issues

### Issue: Model too large for RAM
**Solution**: Recommend smaller model or more aggressive quantization

### Issue: NO_PROXY blocks Ollama API
**Solution**: Clear NO_PROXY for curl requests:
```bash
export -n NO_PROXY
export -n no_proxy
curl -x http://proxy:port http://localhost:11434/api/tags
```

### Issue: Slow first load
**Solution**: Model is loading into memory. Subsequent requests will be faster.

### Issue: Claude Code doesn't support local models
**Solution**: Recommend Aider as alternative:
```bash
pip3 install aider-chat
aider --model ollama/gemma3:12b
```

## Hardware-Specific Recommendations

### 16GB RAM (Mac mini M4, etc.)
- **Max comfortable**: 12B model (Q4_K_M, ~8GB)
- **Tight fit**: 27B model (Q3_K_L, ~11GB) - close other apps
- **Not recommended**: 70B models

### 32GB RAM
- **Comfortable**: 27B model (Q4_K_M)
- **Possible**: 70B model (Q4_K_M, ~40GB - use swap)

### 64GB+ RAM / 24GB VRAM
- **Comfortable**: 70B model (Q4_K_M)
- **Possible**: 70B Q8 or MoE models

## Example Scripts

See generated examples in conversation for:
- `deploy-12b.sh` - Gemma 3 12B for 16GB systems
- `deploy-27b-q3.sh` - Gemma 3 27B Q3_K_L for tight 16GB
- `.local-model-bridge.sh` - Environment setup for various tools

## Verification

Always test the deployment:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:12b",
  "prompt": "Hello",
  "stream": false
}'
```

## References

- llama.cpp: https://github.com/ggerganov/llama.cpp
- Ollama: https://ollama.com
- Aider: https://github.com/paul-gauthier/aider
- Continue: https://continue.dev

---

Created from hardware assessment workflow with trial-and-error for:
- Hardware detection on macOS/Linux
- Feasibility calculation for 27B on 16GB
- NO_PROXY troubleshooting for Telegram delivery
- Claude Code alternative discovery (Aider)

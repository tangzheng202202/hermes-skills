---
name: multi-agent-voice-router
title: Multi-Agent Voice Router Hub
description: Build a voice-controlled routing system that directs commands to different AI agents based on wake words
version: 1.0
tags: [voice, ai, smart-home, routing, whisper, piper, ollama]
---

# Multi-Agent Voice Router Hub

Build a voice-controlled routing system that directs commands to different AI agents based on wake words.

## Use Cases

- Smart home with multiple AI personalities/services
- Routing work commands to coding assistant vs general queries to chatbot
- Voice interface for existing CLI tools
- Multi-backend AI (local + cloud) with unified voice interface

## Architecture

```
🎤 Microphone
    ↓
Whisper (STT - Speech to Text)
    ↓
Voice Router (wake word detection)
    ↓
    ├─ "Hey Hermes" → Hermes CLI (coding/system)
    ├─ "Hey 奶龙"   → OpenClaw (Feishu/collaboration)
    ├─ "Hey Jarvis" → Ollama (local LLM)
    └─ "Hey Home"   → Home Assistant (smart home)
    ↓
Piper (TTS - Text to Speech)
```

## Core Components

### 1. Docker Services

```yaml
services:
  ollama:      # Local LLM inference
    image: ollama/ollama:latest
    ports: ["11434:11434"]
  
  whisper:     # Speech-to-text (Wyoming protocol)
    image: rhasspy/wyoming-whisper:latest
    ports: ["10300:10300"]
  
  piper:       # Text-to-speech
    image: rhasspy/wyoming-piper:latest
    ports: ["10200:10200"]
```

### 2. Voice Router (Python)

Key logic:
- Record audio chunk
- Send to Whisper for transcription
- Detect wake word in text
- Route to appropriate handler
- Speak response via Piper

```python
def process(self, text: str) -> str:
    agent = self.detect_wake_word(text)
    clean_text = remove_wake_word(text, agent)
    
    if agent == "hermes":
        return self.call_hermes(clean_text)
    elif agent == "ollama":
        return self.call_ollama(clean_text)
```

### 3. CLI Tool Adapters

CLI tools don't have HTTP APIs. Create lightweight HTTP adapters:

```python
class HermesAdapter:
    def chat(self, message: str) -> str:
        result = subprocess.run(
            ["hermes", "-c", message],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout

# Wrap as HTTP API
from http.server import HTTPServer, BaseHTTPRequestHandler

class HermesHandler(BaseHTTPRequestHandler):
    adapter = HermesAdapter()
    
    def do_POST(self):
        # Parse request, call adapter.chat(), return JSON
        pass

def start_server(port=8081):
    server = HTTPServer(('localhost', port), HermesHandler)
    server.serve_forever()
```

**Run:** `python hermes_adapter.py --server --port 8081`

**Router Integration with Fallback:**
```python
def route_to_hermes(self, text: str) -> str:
    try:
        # Try HTTP adapter first
        response = requests.post(
            "http://localhost:8081/chat",
            json={"message": text},
            timeout=60
        )
        return response.json()["response"]
    except requests.ConnectionError:
        # Fallback: direct subprocess call
        result = subprocess.run(
            ["python3", "adapters/hermes_adapter.py", text],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
```

### 4. Wake Word Configuration

```yaml
wake_words:
  hermes: ["hey hermes", "hermes", "黑慕斯"]
  openclaw: ["hey 奶龙", "奶龙", "nai long"]
  ollama: ["hey jarvis", "jarvis", "贾维斯"]
```

## Implementation Steps

```bash
# 1. Start core services
docker-compose up -d

# 2. Download LLM model
docker exec ollama ollama pull llama3.1:8b

# 3. Start adapters
python adapters/hermes_adapter.py --server --port 8081 &
python adapters/openclaw_adapter.py --server --port 8082 &

# 4. Run voice router
python voice_router.py
```

## Testing

### Unit Test Wake Words (No External Services)

Create `test_routing.py` to test wake word detection without Docker:

```python
from voice_router import VoiceRouter

router = VoiceRouter()
test_cases = [
    ("hey hermes list files", "hermes"),
    ("奶龙 发送消息", "openclaw"),
    ("hey jarvis hello", "ollama"),
    ("turn on lights", None),  # No wake word
]

for text, expected in test_cases:
    result = router.detect_wake_word(text)
    assert result == expected, f"Failed: {text}"
print(f"✅ All {len(test_cases)} wake word tests passed")
```

### Text Mode (No Mic)
```bash
python voice_router.py --test
> hey jarvis what time is it
> hey hermes list files
```

### Check Adapter Status
```bash
lsof -ti:8081  # Hermes adapter
lsof -ti:8082  # OpenClaw adapter
```

## Dependencies

```bash
pip install sounddevice soundfile numpy requests pyyaml
```

## Pitfalls

1. **CLI tools hang**: Use non-interactive flags (`-c`, `--batch`)
2. **Wake word false positives**: Keep words phonetically distinct
3. **Audio device selection**: Use `sounddevice.query_devices()`
4. **Docker startup delay**: Add sleep between up and first request
5. **Docker mirror timeouts**: Some Chinese mirrors (USTC, 163) may be unreachable. Use working mirrors:
   ```json
   {
     "registry-mirrors": [
       "https://docker.1panel.live",
       "https://hub.rat.dev"
     ]
   }
   ```
   Then restart Docker Desktop.
6. **Adapter not running**: Check port occupancy before starting:
   ```bash
   if ! lsof -ti:8081 > /dev/null 2>&1; then
       python3 adapters/hermes_adapter.py --server --port 8081 &
   fi
   ```

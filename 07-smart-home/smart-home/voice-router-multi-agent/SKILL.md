---
name: voice-router-multi-agent
title: Voice Router Multi-Agent Hub
description: Build a voice-controlled routing hub that directs commands to different AI agents based on wake words
version: 1.0
tags: [voice, ai, routing, smart-home, ollama, multi-agent]
---

# Voice Router Multi-Agent Hub

Build a voice-controlled routing hub that directs commands to different AI agents based on wake words.

## Overview

Create a centralized voice interface where users can say different wake words to route to specific AI backends:
- "Hey Hermes" → Hermes CLI (coding/system tasks)
- "Hey 奶龙" → OpenClaw/Feishu Agent (collaboration)
- "Hey Jarvis" → Ollama local LLM (general AI)
- "Hey Home" → Home Assistant (smart home)

## Architecture

```
Voice Input → Wake Word Detection → Router → Agent Adapter → Response → TTS
                ↓                      ↓
           hermes|openclaw|ollama|ha   HTTP API Bridge
```

## Project Structure

```
home-ai/
├── voice_router.py          # Core routing logic
├── config.yaml              # Agent configurations
├── adapters/                # CLI-to-HTTP bridges
│   ├── hermes_adapter.py   # Hermes CLI wrapper
│   └── openclaw_adapter.py # OpenClaw wrapper
├── docker-compose.yml       # Supporting services
└── launch.sh               # One-click startup
```

## Implementation Steps

### 1. Core Router (voice_router.py)

```python
CONFIG = {
    "wake_words": {
        "hermes": ["hey hermes", "hermes", "黑慕斯"],
        "openclaw": ["hey 奶龙", "奶龙", "nai long"],
        "ollama": ["hey jarvis", "jarvis", "贾维斯"],
        "ha": ["hey home", "home assistant", "智能家居"]
    },
    "ollama_url": "http://localhost:11434",
    "ollama_model": "qwen3.5-9b-fast:latest"
}

def detect_wake_word(self, text: str) -> Optional[str]:
    text = text.lower().strip()
    for agent, words in self.config["wake_words"].items():
        if any(word in text for word in words):
            return agent
    return None

def process(self, text: str) -> str:
    agent = self.detect_wake_word(text)
    if not agent:
        return "请使用唤醒词：Hey Hermes / Hey 奶龙 / Hey Jarvis"
    
    # Remove wake word
    clean_text = text.lower()
    for word in self.config["wake_words"][agent]:
        clean_text = clean_text.replace(word, "").strip()
    
    # Route to handler
    handlers = {
        "hermes": self.route_to_hermes,
        "openclaw": self.route_to_openclaw,
        "ollama": self.route_to_ollama,
        "ha": self.route_to_ha
    }
    return handlers[agent](clean_text)
```

### 2. Agent Adapter Pattern

When CLI tools don't have HTTP APIs, create lightweight HTTP adapters:

```python
# adapters/hermes_adapter.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

class HermesHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/chat":
            data = json.loads(self.rfile.read(...))
            result = subprocess.run(
                ["hermes", "-c", data["message"]],
                capture_output=True, text=True, timeout=60
            )
            self.send_response(200)
            self.wfile.write(json.dumps({
                "response": result.stdout.strip()
            }).encode())

def start_server(port=8081):
    server = HTTPServer(('localhost', port), HermesHandler)
    server.serve_forever()
```

### 3. Docker Services (Optional)

For speech-to-text and text-to-speech:

```yaml
# docker-compose.yml
services:
  whisper:
    image: rhasspy/wyoming-whisper:latest
    ports: ["10300:10300"]
    command: [--model, small, --language, zh]
    
  piper:
    image: rhasspy/wyoming-piper:latest
    ports: ["10200:10200"]
    command: [--voice, zh_CN-huayan-medium]
    
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: [ollama-data:/root/.ollama]
```

### 4. Startup Script

```bash
#!/bin/bash
# launch.sh - Start all services

# 1. Start Docker services
docker-compose up -d

# 2. Start agent adapters
python3 adapters/hermes_adapter.py --server --port 8081 &
python3 adapters/openclaw_adapter.py --server --port 8082 &

# 3. Start voice router
python3 voice_router.py
```

## Configuration

Edit `config.yaml`:

```yaml
agents:
  hermes:
    wake_words: ["hey hermes", "hermes"]
    mode: "cli"
    cli_path: "hermes"
    
  openclaw:
    wake_words: ["hey 奶龙", "奶龙"]
    mode: "cli"
    cli_path: "openclaw"
    
  ollama:
    wake_words: ["hey jarvis", "jarvis"]
    model: "qwen3.5-9b-fast:latest"
    url: "http://localhost:11434"
```

## Testing

**Text mode (no microphone):**
```bash
python3 voice_router.py --test
> hey jarvis 今天天气怎么样
> 奶龙 总结一下会议纪要
```

**Voice mode:**
```bash
./launch.sh
```

## Troubleshooting

### Docker Registry Issues (China)

If `docker pull` fails with DNS/timeout errors:

```bash
# Edit ~/.docker/daemon.json
cat > ~/.docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://docker.m.daocloud.io"
  ]
}
EOF

# Restart Docker Desktop
osascript -e 'quit app "Docker Desktop"'
open -a "Docker Desktop"
```

### Adapter Not Responding

Check if ports are in use:
```bash
lsof -ti:8081  # Hermes adapter
lsof -ti:8082  # OpenClaw adapter
```

Restart adapters:
```bash
python3 adapters/hermes_adapter.py --server --port 8081 &
python3 adapters/openclaw_adapter.py --server --port 8082 &
```

### Ollama Slow Response

Large models (9B+) take time to load. Options:
1. Use smaller model: `qwen3:4b` instead of `qwen3.5-9b`
2. Keep model loaded: `ollama run qwen3.5-9b-fast` in background
3. Increase timeout in voice_router.py

## Extension Guide

**Add new agent:**
1. Add wake_words to CONFIG
2. Create handler method in VoiceRouter
3. Create adapter if CLI-only tool
4. Add to docker-compose if needed

**Example - Add Claude Code:**
```python
# In voice_router.py
"claude": ["hey claude", "claude", "克劳德"]

def route_to_claude(self, text: str) -> str:
    result = subprocess.run(
        ["claude", "-p", text],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout.strip()
```

## Requirements

- Python 3.9+
- macOS (Apple Silicon optimized)
- Docker Desktop (optional, for voice services)
- Ollama (local LLM)
- Agent CLIs (Hermes, OpenClaw, etc.)

## Key Files

| File | Purpose |
|------|---------|
| `voice_router.py` | Core routing logic |
| `adapters/*.py` | CLI-to-HTTP bridges |
| `config.yaml` | Agent configuration |
| `docker-compose.yml` | Supporting services |
| `launch.sh` | One-click startup |
| `test_routing.py` | Wake word tests |

## Lessons Learned

1. **Adapter Pattern**: CLI tools without APIs need lightweight HTTP wrappers
2. **Docker Mirrors**: In China, registry-mirrors configuration is essential
3. **Model Size**: 9B+ models are slow for voice; 4B models respond faster
4. **Wake Words**: Multiple variants improve recognition (中文+拼音+英文)
5. **Service Discovery**: Check ports before starting to avoid conflicts

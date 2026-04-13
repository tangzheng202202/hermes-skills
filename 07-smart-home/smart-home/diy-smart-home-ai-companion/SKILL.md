---
name: diy-smart-home-ai-companion
title: DIY Smart Home AI Companion System
description: Complete guide for building a local-first smart home with AI voice assistant, computer vision, and home automation
emoji: 🏠
tags: [smart-home, home-assistant, ai, edge-computing, frigate, ollama, zigbee, iot]
author: Hermes
last_updated: 2026-04-12
---

# DIY Smart Home AI Companion System

Complete reference for building a privacy-focused, local-first smart home with natural language AI interaction.

## Overview

This skill provides:
- Three budget tiers (low/mid/high) with specific hardware recommendations
- 7-phase implementation roadmap from hardware to production
- Complete configuration templates for Home Assistant, Frigate, Ollama
- Privacy and security hardening guides
- Business model suggestions for commercialization

## Core Stack

- **Home Assistant OS** - Central control hub
- **Frigate NVR** - AI-powered video surveillance with Coral TPU
- **Ollama** - Local LLM (Qwen2.5 for Chinese)
- **Wyoming Stack** - Whisper (ASR) + Piper (TTS) + openWakeWord
- **Zigbee2MQTT** - IoT device integration

## Budget Tiers

### Zero-Cost (¥0): Mac mini M4 + Old Phones ⭐ Zero Investment
**Hardware**: Mac mini M4 (existing), 2x old smartphones (existing)
- 2 cameras (old phones via IP Webcam), motion detection
- Llama3.1 8B or Qwen2.5 7B model
- 5-10 WiFi/Zigbee devices
- **Use case**: Development, testing, personal use
- **Pros**: No new hardware, Metal GPU acceleration, portable
- **Cons**: Not 24/7 (Mac may sleep), phone battery wear

See [Mac mini Setup Guide](#mac-mini-zero-cost-setup) below.

### Low (¥2,800-3,500): Raspberry Pi 5 8GB
- 2-3 cameras, 5fps AI detection
- Qwen2.5 3B model
- 20-30 Zigbee devices

### Mid (¥6,000-8,000): Intel N100 + 16GB ⭐ Recommended
- 4-6 cameras, 10fps detection + face recognition  
- Qwen2.5 7B/14B model
- 50-100 Zigbee devices
- 7x24 stable operation

### High (¥15,000-20,000): Intel NUC i5 + 32GB + GPU
- 8-12 cameras, 25fps full analysis
- Qwen2.5 32B model
- 200+ devices
- Enterprise-grade reliability

## Mac mini Zero-Cost Setup

For users with existing Mac hardware and old smartphones.

### Architecture
```
Mac mini M4 (16GB RAM)
├── Home Assistant (Docker)
├── Ollama (Llama3.1 8B, Metal GPU)
├── Whisper (Wyoming, medium-int8)
├── Piper TTS (zh_CN-huayan-medium)
└── IP Cameras (old phones)
    └── Android/iPhone → IP Webcam App
```

### Resource Usage (~8-9GB total)
- Home Assistant: ~500MB
- Ollama 8B: ~6GB
- Whisper: ~2GB
- Piper: ~100MB

### Docker Compose (Mac)
```yaml
version: '3.8'

services:
  homeassistant:
    container_name: ha-core
    image: ghcr.io/home-assistant/home-assistant:stable
    privileged: true
    restart: unless-stopped
    ports:
      - "8123:8123"
    volumes:
      - ./ha-config:/config
      - /etc/localtime:/etc/localtime:ro
    environment:
      - TZ=Asia/Shanghai

  ollama:
    container_name: ai-brain
    image: ollama/ollama:latest
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/root/.ollama
    environment:
      - OLLAMA_ORIGINS=*
    deploy:
      resources:
        reservations:
          memory: 4G

  whisper:
    container_name: ai-ears
    image: rhasspy/wyoming-whisper:latest
    restart: unless-stopped
    ports:
      - "10300:10300"
    volumes:
      - whisper-models:/data
    command: >
      --model medium-int8
      --language zh
      --beam-size 5

  piper:
    container_name: ai-mouth
    image: rhasspy/wyoming-piper:latest
    restart: unless-stopped
    ports:
      - "10200:10200"
    volumes:
      - piper-voices:/data
    command: >
      --voice zh_CN-huayan-medium
      --speaker 0

volumes:
  ollama-models:
  whisper-models:
  piper-voices:
```

### IP Camera Setup (Old Phones)

**Android: IP Webcam App**
1. Install from Google Play
2. Settings → 1280x720, 15fps, H.264
3. Start server, note IP (e.g., 192.168.1.101:8080)
4. Test: `http://PHONE_IP:8080/video`

**iPhone: 掌上看家 or Stream**
- 掌上看家: 采集端模式，记录 CID
- Stream App: RTMP stream output

**Home Assistant Integration**
```yaml
camera:
  - platform: generic
    name: "客厅摄像头"
    still_image_url: "http://PHONE_IP:8080/shot.jpg"
    stream_source: "http://PHONE_IP:8080/video"
    verify_ssl: false
```

**Power Management**
- Keep phones plugged in 24/7
- Android: Battery optimization → IP Webcam → "不优化"
- iPhone: Settings → Display → Auto-lock → Never

### Mac-Specific Optimizations
- Ollama auto-uses Metal GPU on Apple Silicon
- Use DroidCam for audio input if needed
- LaunchAgent for auto-start on boot
- Disable Mac sleep for 24/7 operation

---

## Quick Start: Zero-Cost Setup (Mac + Old Phones)

**Prerequisites**: Mac mini M4 (or Intel Mac), old smartphone(s), same WiFi network

```bash
# 1. Install Docker Desktop
brew install --cask docker

# 2. Create project
mkdir -p ~/home-ai/ha-config && cd ~/home-ai

# 3. Create docker-compose.yml (use Mac config above)
# 4. Create HA config
cat > ha-config/configuration.yaml << 'EOF'
default_config:
camera:
  - platform: generic
    name: "客厅摄像头"
    still_image_url: "http://PHONE_IP:8080/shot.jpg"
    stream_source: "http://PHONE_IP:8080/video"
conversation:
tts:
  - platform: google_translate
    language: zh-cn
homeassistant:
  name: 我的家
  latitude: 31.2304
  longitude: 121.4737
  unit_system: metric
  time_zone: Asia/Shanghai
EOF

# 5. Start services
docker-compose up -d

# 6. Download model
docker exec -it ai-brain ollama pull llama3.1:8b

# 7. Open Home Assistant
open http://localhost:8123
```

**Total time**: 30 minutes to first camera feed.

---

## Implementation Phases

1. **Hardware procurement** (1-2 weeks)
   - Verify Coral TPU authenticity
   - Must use official 27W PSU for Pi5
   - Test all RTSP streams before mounting

2. **OS Installation** (2-3 days)
   - Burn HAOS using Raspberry Pi Imager
   - Set static IP immediately
   - Verify network connectivity

3. **HA Core Setup** (3-5 days)
   - Install HACS for community add-ons
   - Configure Zigbee2MQTT
   - Verify Zigbee channel (15/20/25) doesn't conflict with WiFi

4. **Frigate NVR** (3-5 days)
   - Configure Coral TPU (usb/pci)
   - Set up RTSP streams
   - Configure face recognition
   - **Pitfall**: Test RTSP in VLC first

5. **Voice AI System** (5-7 days)
   - Install faster-whisper (ASR)
   - Install Piper TTS (zh_CN-huayan-medium)
   - Configure openWakeWord
   - Integrate Ollama with Extended OpenAI Conversation
   - **Key**: Language must be set to "zh" for Chinese

6. **Device Integration** (ongoing)
   - Pair Zigbee devices
   - Create automations
   - Set up notifications

7. **Optimization & Maintenance**
   - Automated backups
   - Performance monitoring
   - Security hardening
   - UPS integration

## Critical Configuration Snippets

### Frigate with Coral TPU
```yaml
detectors:
  coral:
    type: edgetpu
    device: usb  # or pci for M.2

cameras:
  entrance:
    ffmpeg:
      inputs:
        - path: rtsp://admin:pass@ip:554/Streaming/Channels/101
          roles: [detect, record]
    face_recognition:
      enabled: true
```

### Chinese Voice Pipeline
```yaml
# Whisper - must set language: zh
model: small
language: zh
beam_size: 5

# Piper TTS
voice: zh_CN-huayan-medium
length_scale: 1.1
sentence_silence: 0.3
```

### Ollama Integration
```bash
# Pull Qwen2.5
ollama pull qwen2.5:7b

# Extended OpenAI Conversation config:
Base URL: http://localhost:11434/v1
Model: qwen2.5:7b
System Prompt: 你是智能家庭助手...
```

## Common Pitfalls

1. **Zigbee interference**: Use USB extension cable, avoid USB3.0 near 2.4GHz
2. **Coral TPU not detected**: Check USB power (use powered hub if needed)
3. **Whisper poor Chinese recognition**: Use "small" or larger model, not "tiny"
4. **Frigate high CPU**: Verify TPU is being used (check logs)
5. **MQTT connection fails**: Ensure MQTT broker add-on is installed first
6. **IP Camera disconnects**: Disable phone sleep/battery optimization
7. **Mac audio input not working**: Use DroidCam or BlackHole virtual audio
8. **Ollama slow on Mac**: Verify Metal GPU is being used (`OLLAMA_DEBUG=1`)

## Privacy Checklist

- [ ] Disable cloud integrations
- [ ] Set up local DNS blocking
- [ ] Configure firewall rules (LAN-only access)
- [ ] Enable HTTPS (Nginx Proxy Manager)
- [ ] Regular automated backups
- [ ] UPS for graceful shutdown

## Related Skills

- `ip-camera-monitor`: Minimal Python-only camera monitoring when Docker/HA is overkill
- HA Docs: https://www.home-assistant.io/docs/
- Frigate Docs: https://docs.frigate.video/
- Zigbee2MQTT: https://www.zigbee2mqtt.io/
- Qwen2.5: https://github.com/QwenLM/Qwen2.5
- Wyoming Protocol: https://www.home-assistant.io/integrations/wyoming/

## Business Model Options

- B2C: Installation (¥2-5k), Annual maintenance (¥500-1.2k)
- B2B: Shop monitoring (¥8-20k), Office automation (¥15-50k)
- Differentiator: Local-only, no subscriptions, fully customizable

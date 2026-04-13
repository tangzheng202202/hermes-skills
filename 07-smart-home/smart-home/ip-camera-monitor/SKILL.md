---
name: ip-camera-monitor
title: IP Camera Monitor (Minimal Setup)
description: Turn any Android phone or IP camera into a monitoring system using Python - no Docker or Home Assistant required
emoji: 📷
tags: [smart-home, camera, monitoring, python, ip-webcam]
author: Hermes
last_updated: 2026-04-12
---

# IP Camera Monitor

Turn any Android phone or IP camera into a simple monitoring system using Python - no Docker or Home Assistant required.

## When to Use This

- You want **quick setup** without complex infrastructure
- Docker/Home Assistant is **too heavy** for your use case
- You need **snapshot recording**, not real-time streaming
- You're on **Apple Silicon** where HA Docker has issues
- You want a **minimal dependency** solution

## Prerequisites

1. **Android phone with IP Webcam app** (or any IP camera with MJPEG/HTTP interface)
2. **Python 3** (built-in, no pip install needed - uses only stdlib)
3. **Same WiFi network** for phone and computer

## Quick Start

### 1. Set up the camera (Android)

Install [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam):
- Open app → tap **"Start server"**
- Note the IP address shown (e.g., `192.168.1.17:8080`)
- Keep phone plugged in (battery drains fast)

### 2. Test in browser first

```bash
# View web interface
open http://PHONE_IP:8080

# Direct snapshot URL
open http://PHONE_IP:8080/shot.jpg

# MJPEG stream (VLC can play this)
open http://PHONE_IP:8080/video
```

### 3. Python monitoring script

Save as `camera_monitor.py`:

```python
#!/usr/bin/env python3
"""Minimal IP camera monitor - saves snapshots every N seconds"""
import urllib.request
import time
import os

# CONFIGURATION - change these
CAM_URL = "http://192.168.1.17:8080/shot.jpg"  # Your phone's IP
OUTPUT_DIR = os.path.expanduser("~/camera_snapshots")
INTERVAL = 5  # seconds between snapshots

# Setup
os.makedirs(OUTPUT_DIR, exist_ok=True)
print("📷 Starting camera monitor...")
print(f"Saving to: {OUTPUT_DIR}")
print(f"Interval: {INTERVAL}s")
print("Press Ctrl+C to stop\n")

count = 0
while True:
    try:
        filename = f"{OUTPUT_DIR}/snap_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
        urllib.request.urlretrieve(CAM_URL, filename)
        count += 1
        print(f"✅ [{count}] {time.strftime('%H:%M:%S')} {filename}")
        time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print(f"\n⏹️ Stopped. Total snapshots: {count}")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(INTERVAL)
```

Run it:
```bash
python3 camera_monitor.py
```

## Comparison: Approaches

| Method | Setup Time | Dependencies | Storage | Best For |
|--------|------------|--------------|---------|----------|
| **Python script** | 2 min | None (stdlib) | Disk snapshots | Quick monitoring, timelapse |
| **Home Assistant** | 30+ min | Docker + 1GB+ | Database + recordings | Full smart home integration |
| **VLC streaming** | 1 min | VLC installed | None | Real-time viewing only |
| **ffmpeg continuous** | 5 min | ffmpeg | Video files | Continuous recording |

## Common Issues

### "Connection refused" or timeout
- Phone and computer not on **same WiFi**
- IP Webcam app not started
- Phone went to sleep → disable auto-lock

### IP address keeps changing
- Assign **static IP** in router settings (DHCP reservation)
- Or use IP Webcam's cloud feature (if available)

### Images are blurry/dark
- Adjust camera settings in IP Webcam app
- Ensure good lighting on subject

### Script fails on first run
```bash
# Create output directory manually
mkdir -p ~/camera_snapshots
```

## Variations

### Timelapse creator (after recording)
```bash
# Install ffmpeg first: brew install ffmpeg
# Then create video from snapshots:
ffmpeg -framerate 10 -pattern_type glob -i "*.jpg" -c:v libx264 timelapse.mp4
```

### Simple motion detection
```python
import urllib.request
import cv2  # pip install opencv-python
import numpy as np

prev_frame = None
while True:
    img = urllib.request.urlopen(CAM_URL).read()
    frame = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    if prev_frame is not None:
        diff = cv2.absdiff(prev_frame, gray)
        if diff.mean() > 10:  # threshold
            print("Motion detected!")
            # Save frame...
    
    prev_frame = gray
    time.sleep(1)
```

### Web dashboard (Flask)
```python
from flask import Flask, Response
import urllib.request

app = Flask(__name__)
CAM_URL = "http://192.168.1.17:8080/shot.jpg"

@app.route('/')
def stream():
    def generate():
        while True:
            img = urllib.request.urlopen(CAM_URL).read()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
            time.sleep(0.5)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(host='0.0.0.0', port=5000)
# Then open http://localhost:5000
```

## Security Warning

⚠️ **Do not expose port 8080 to the internet** without authentication. This setup is for **local network only**.

## Related Skills

- `diy-smart-home-ai-companion`: Full Home Assistant + Frigate + Ollama stack for advanced users

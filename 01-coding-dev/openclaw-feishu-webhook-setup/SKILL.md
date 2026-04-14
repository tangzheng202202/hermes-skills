---
name: openclaw-feishu-webhook-setup
description: "Fix OpenClaw Feishu integration when messages aren't received. Diagnoses WebSocket failures, switches to webhook mode, creates cloudflared tunnel for public URL, and configures event subscription."
---

# OpenClaw Feishu Webhook Setup

Fix Feishu integration when personal chat or group messages aren't being received by the agent.

## Problem Symptoms

- No response when messaging the bot in Feishu personal chat
- Groups show the bot but messages aren't processed
- Gateway logs show: `ws connect failed` or `unable to connect to the server`

## Root Cause

**WebSocket mode requires special app permissions** that may not be available for all Feishu app types. The error:
```
"receive events or callbacks through persistent connection only available in self-build & Feishu app"
```

**Solution: Switch to webhook mode** with a public URL tunnel.

---

## Quick Fix Workflow

### Step 1: Diagnose Current State

```bash
# Check current connection mode
openclaw config get channels.feishu.connectionMode

# View Feishu configuration
openclaw config get channels.feishu

# Check gateway logs for errors
tail -50 ~/.openclaw/logs/gateway.log | grep -E '(feishu|websocket|webhook)'
```

### Step 2: Create Public URL Tunnel

**Option A: cloudflared (Recommended - Free)**

```bash
# Check if cloudflared is installed
which cloudflared

# Create tunnel (runs in background)
nohup cloudflared tunnel --url http://localhost:8080 > /tmp/cloudflared.log 2>&1 &

# Wait for initialization
sleep 5

# Get the public URL
export PUBLIC_URL=$(cat /tmp/cloudflared.log | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | head -1)
echo "Public URL: $PUBLIC_URL"
```

**Option B: ngrok (If cloudflared unavailable)**

```bash
# Requires ngrok account/token
ngrok http 8080

# Copy the https URL from output
```

### Step 3: Configure OpenClaw for Webhook Mode

```bash
# Switch to webhook mode
openclaw config set channels.feishu.connectionMode webhook

# Set the webhook URL (replace with your actual URL)
openclaw config set channels.feishu.webhookUrl 'https://your-tunnel-url.trycloudflare.com/feishu/events'

# Verify configuration
openclaw config get channels.feishu.connectionMode
openclaw config get channels.feishu.webhookUrl
```

### Step 4: Restart Gateway

```bash
openclaw gateway restart

# Verify webhook mode started
tail -30 ~/.openclaw/logs/gateway.log | grep -E '(feishu|webhook)'
```

Expected output:
```
[feishu] starting feishu[default] (mode: webhook)
[feishu] feishu[default]: bot open_id resolved: ou_xxxxx
```

### Step 5: Configure Feishu Open Platform

1. Go to [Feishu Open Platform](https://open.feishu.cn/app/)
2. Select your app (e.g., `cli_a92c417c1b38dced`)
3. Navigate to **「事件与回调」** → **「事件订阅」**
4. Set **请求地址** to:
   ```
   https://your-tunnel-url.trycloudflare.com/feishu/events
   ```
5. Click **保存** (Save)
6. Verify the URL is reachable (platform will test it)

### Step 6: Test

Send a message to your bot in Feishu personal chat or a configured group.

---

## Additional Configuration

### Allow Personal Chat (DM)

```bash
# Set DM policy to "open" (allows direct messages without pairing)
openclaw config set channels.feishu.dmPolicy open

# Add your user ID to allowFrom list
openclaw config set channels.feishu.allowFrom '["ou_your_user_id"]'
```

### Configure Groups

```bash
# Get group chat ID from Feishu
# Then add to configuration:
openclaw config set channels.feishu.groups.oc_xxxxx.enabled true
openclaw config set channels.feishu.groups.oc_xxxxx.allowFrom '["ou_your_user_id"]'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ws connect failed` | Switch to webhook mode (this guide) |
| `authentication failed` | Check appId and appSecret in config |
| `unable to connect to the server` | WebSocket not supported; use webhook |
| cloudflared fails | Check if port 8080 is available; try port 18789 |
| ngrok proxy error | Unset http_proxy environment variables |
| Events not received | Verify URL in Feishu platform matches tunnel URL |

---

## Important Notes

1. **cloudflared tunnel is temporary** - URL changes on restart. For production, use a fixed domain.
2. **Webhook mode is more reliable** than WebSocket for most use cases.
3. **Gateway port** - Default is 8080, but check `openclaw config get gateway.port` to confirm.
4. **Keep tunnel running** - If cloudflared stops, Feishu events won't be received.

---

## Automation Script

```bash
#!/bin/bash
# openclaw-feishu-fix.sh - Quick Feishu webhook setup

set -e

echo "=== OpenClaw Feishu Webhook Fix ==="

# Check if cloudflared exists
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found. Install with: brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

# Kill existing cloudflared
pkill -f "cloudflared tunnel" || true

# Start tunnel
echo "Starting cloudflared tunnel..."
nohup cloudflared tunnel --url http://localhost:8080 > /tmp/cloudflared.log 2>&1 &
sleep 6

# Get public URL
PUBLIC_URL=$(cat /tmp/cloudflared.log | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | head -1)

if [ -z "$PUBLIC_URL" ]; then
    echo "❌ Failed to get public URL. Check /tmp/cloudflared.log"
    exit 1
fi

echo "✅ Public URL: $PUBLIC_URL"

# Configure OpenClaw
openclaw config set channels.feishu.connectionMode webhook
openclaw config set channels.feishu.webhookUrl "${PUBLIC_URL}/feishu/events"

# Restart gateway
openclaw gateway restart

echo ""
echo "=== Configuration Complete ==="
echo "Webhook URL: ${PUBLIC_URL}/feishu/events"
echo ""
echo "Next steps:"
echo "1. Go to https://open.feishu.cn/app/"
echo "2. Select your app → 事件与回调 → 事件订阅"
echo "3. Set request URL to: ${PUBLIC_URL}/feishu/events"
echo "4. Save and test"
```

#!/bin/bash
# openclaw-feishu-fix.sh - Quick Feishu webhook setup
# Usage: ./openclaw-feishu-fix.sh [port]

set -e

PORT=${1:-8080}

echo "=== OpenClaw Feishu Webhook Fix ==="
echo "Using port: $PORT"

# Check if cloudflared exists
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found."
    echo "Install with: brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

# Kill existing cloudflared
pkill -f "cloudflared tunnel" 2>/dev/null || true

# Start tunnel
echo "Starting cloudflared tunnel on port $PORT..."
nohup cloudflared tunnel --url http://localhost:$PORT > /tmp/cloudflared.log 2>&1 &
sleep 6

# Get public URL
PUBLIC_URL=$(cat /tmp/cloudflared.log | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | head -1)

if [ -z "$PUBLIC_URL" ]; then
    echo "❌ Failed to get public URL. Check /tmp/cloudflared.log:"
    tail -20 /tmp/cloudflared.log
    exit 1
fi

echo "✅ Public URL: $PUBLIC_URL"

# Configure OpenClaw
echo "Configuring OpenClaw..."
openclaw config set channels.feishu.connectionMode webhook
openclaw config set channels.feishu.webhookUrl "${PUBLIC_URL}/feishu/events"

# Restart gateway
echo "Restarting gateway..."
openclaw gateway restart

echo ""
echo "=== Configuration Complete ==="
echo ""
echo "Webhook URL: ${PUBLIC_URL}/feishu/events"
echo ""
echo "Next steps:"
echo "1. Go to https://open.feishu.cn/app/"
echo "2. Select your app → 事件与回调 → 事件订阅"
echo "3. Set request URL to: ${PUBLIC_URL}/feishu/events"
echo "4. Save and test"
echo ""
echo "⚠️  Keep this terminal open - cloudflared is running in background"
echo "    Press Ctrl+C to stop the tunnel"

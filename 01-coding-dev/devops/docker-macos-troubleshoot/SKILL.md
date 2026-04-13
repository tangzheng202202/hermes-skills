---
name: docker-macos-troubleshoot
title: Docker macOS Troubleshooting
description: Fix Docker Desktop on macOS, especially image pull failures from outdated registry mirrors.
trigger: docker pull timeout, failed to resolve reference, docker mirror issues
---

# Docker macOS Troubleshooting

Fix Docker Desktop issues on macOS, particularly image pull failures due to outdated registry mirrors.

## Quick Fix

```bash
# 1. Backup current config
cp ~/.docker/daemon.json ~/.docker/daemon.json.backup.$(date +%Y%m%d)

# 2. Update with working mirrors
cat > ~/.docker/daemon.json << 'EOF'
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "features": {
    "buildkit": true
  },
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://docker.m.daocloud.io"
  ]
}
EOF

# 3. Restart Docker Desktop
osascript -e 'tell application "Docker Desktop" to quit'
sleep 3
open -a "Docker Desktop"

# 4. Wait for ready
for i in {1..30}; do
  docker ps > /dev/null 2>&1 && echo "✅ Ready" && break
  sleep 2
done

# 5. Test
docker pull hello-world
```

## Common Issues

### "failed to resolve reference" / timeout
- **Cause**: Outdated/mirror registry URLs in daemon.json
- **Fix**: Update registry-mirrors with working alternatives

### "no such host" for mirrors
- **Cause**: Mirror domain no longer resolves
- **Fix**: Remove dead mirrors, try alternatives

### Docker Desktop won't start
```bash
# Force restart
pkill -9 "Docker Desktop"
sleep 2
open -a "Docker Desktop"
```

## Working Mirror Sources (2026)
- `https://docker.1panel.live`
- `https://hub.rat.dev`
- `https://docker.m.daocloud.io`

## Verify Fix
```bash
docker version
docker pull hello-world
docker images
```

## Pitfalls
- Docker Desktop takes 15-60s to fully start after GUI appears
- Registry mirrors change frequently - may need updates
- Some corporate networks block unofficial mirrors

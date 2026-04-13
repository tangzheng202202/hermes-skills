---
name: openclaw-maintenance
description: "Check OpenClaw version status, compare with latest releases, and safely update. Covers version checking, update channel management, and safe update practices."
---

# OpenClaw Maintenance

Check version status, compare with remote, and safely update OpenClaw CLI.

## Quick Status Check

```bash
# Check current installed version
openclaw --version

# Check update status (shows current vs latest)
openclaw update status

# Check gateway health
openclaw health
```

## Understanding Version Status

### Output Example
```
OpenClaw update status

┌──────────┬──────────────────────────────────────────┐
│ Item     │ Value                                    │
├──────────┼──────────────────────────────────────────┤
│ Install  │ pnpm                                     │
│ Channel  │ stable (default)                         │
│ Update   │ available · pnpm · npm update 2026.4.9   │
└──────────┴──────────────────────────────────────────┘
```

### Key Fields
- **Install**: Package manager used (pnpm, npm, git)
- **Channel**: Update channel (stable, beta, dev)
- **Update**: Status - "available" means update ready

## Safe Update Workflow

### Step 1: Dry Run (Preview)
```bash
openclaw update --dry-run
```

### Step 2: Review Changes
Check for:
- Config warnings (plugin conflicts, etc.)
- Version changes
- Planned actions

### Step 3: Execute Update
```bash
# Interactive mode (recommended first time)
openclaw update

# Non-interactive mode (for automation)
openclaw update --yes

# Without auto-restart
openclaw update --no-restart
```

### Step 4: Verify
```bash
openclaw --version
openclaw health
```

## Update Channels

```bash
# Switch to beta channel
openclaw update --channel beta

# Switch to dev channel
openclaw update --channel dev

# One-off update to specific version/tag
openclaw update --tag 2026.4.5
```

## Common Warnings (Safe to Ignore)

```
Config warnings:
- plugins.entries.feishu: duplicate plugin id detected
- plugins.entries.operator-ui: plugin id mismatch
```

These are typically cosmetic and don't affect functionality.

## Repository Status Check

If OpenClaw was installed from git source:

```bash
cd ~/openclaw-agents  # or wherever repo is

# Check current version
cat CHANGELOG.md | head -20

# Check git status
git log --oneline -5
git remote -v

# Check for updates
git fetch origin
git log HEAD..origin/main --oneline
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "croniter not installed" | `pip install croniter` or use timestamp scheduling |
| Update fails with config errors | Run `openclaw doctor` for health checks |
| Gateway won't start after update | Check logs: `openclaw logs` |
| Plugin conflicts | Check `~/.openclaw/config.json` for duplicates |

## Best Practices

1. **Always dry-run first** - Preview changes before applying
2. **Backup config** - OpenClaw auto-backs up `openclaw.json` before updates
3. **Check health after** - Verify gateway starts correctly
4. **Don't auto-update agents repos** - May conflict with custom config
5. **Document custom configs** - Note any manual changes for troubleshooting

## Automation Example

```bash
#!/bin/bash
# Weekly update check

STATUS=$(openclaw update status --json | jq -r '.update')
if [[ "$STATUS" == *"available"* ]]; then
    echo "Update available, running dry-run..."
    openclaw update --dry-run
    
    # Could auto-update in CI environment
    # openclaw update --yes --no-restart
fi
```

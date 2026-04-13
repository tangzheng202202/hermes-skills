---
name: cronjob-scheduling-patterns
description: "Common patterns and pitfalls for scheduling cron jobs with the cronjob tool. Covers specific-time scheduling, recurrence patterns, and workarounds for cron expression limitations."
---

# Cronjob Scheduling Patterns

## ⚠️ Key Limitations

1. **Standard cron expressions (e.g., `0 9 * * *`) require `croniter` package**
   - If you get error: "Cron expressions require 'croniter' package"
   - The environment may not have it installed
   - Use workarounds below instead

2. **Duration format "24h" schedules from NOW, not from midnight**
   - `schedule: "24h"` → runs every 24 hours from current time
   - NOT the same as "every day at 9am"

## ✅ Working Patterns

### Pattern 1: Specific Time of Day (Daily at 9:00 AM)

**Problem**: Want daily execution at specific time (e.g., 09:00 Beijing time)

**Solution**: Use ISO timestamp for first run + repeat count

```bash
# Step 1: Calculate tomorrow's target time
# macOS:
date -v+1d -v09H -v00M -v00S -Iseconds
# Output: 2026-04-08T09:00:00+08:00

# Step 2: Create job with specific timestamp
cronjob create \
  --name "Daily Morning Task" \
  --schedule "2026-04-08T09:00:00+08:00" \
  --repeat 9999 \
  ...
```

**Result**: First run at specified time, then repeats every 24h automatically

### Pattern 2: Simple Recurring Duration

```bash
# Every 30 minutes
cronjob create --schedule "30m" --repeat 9999 ...

# Every 2 hours
cronjob create --schedule "2h" --repeat 9999 ...

# Every day (from now)
cronjob create --schedule "24h" --repeat 9999 ...
```

### Pattern 3: One-time Scheduled Task

```bash
# Run once at specific time
cronjob create \
  --schedule "2026-04-08T15:30:00+08:00" \
  --repeat 1 ...
```

## 🔧 Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "Cron expressions require 'croniter' package'" | Using `0 9 * * *` format without croniter | Use ISO timestamp or duration format |
| "Invalid duration: 'day at 09:00'" | Unsupported natural language | Use duration (e.g., "24h") or timestamp |
| Job runs at wrong time | "24h" schedules from creation time | Use specific ISO timestamp for time-of-day |

## 📝 Best Practices

1. **Always use `--repeat`** with duration schedules (default is 1)
2. **For daily tasks at specific time**: Calculate next occurrence timestamp explicitly
3. **Timezone**: Include offset in ISO timestamp (e.g., `+08:00` for Beijing)
4. **Verify next_run_at** after creating job to confirm timing is correct

## Example: Complete Daily News Briefing Setup

```bash
# 1. Calculate tomorrow 9am
date -v+1d -v09H -v00M -v00S -Iseconds
# → 2026-04-08T09:00:00+08:00

# 2. Create recurring daily job
cronjob create \
  --name "每日全球新闻简报" \
  --schedule "2026-04-08T09:00:00+08:00" \
  --skill news-aggregator-skill \
  --prompt "..." \
  --deliver telegram \
  --repeat 9999

# 3. Verify
cronjob list
```

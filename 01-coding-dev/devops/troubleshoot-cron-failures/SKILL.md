---
name: troubleshoot-cron-failures
description: "Diagnose and fix failed cron jobs, especially HTTP 429 engine overload errors and missing dependencies. Use when cron jobs fail, user reports missing notifications, or cronjob tool returns errors."
---

# Troubleshooting Cron Job Failures

## Common Failure Patterns

### 1. KeyError 'expr' - 调度器字段名不匹配

**症状:**
- 日志显示 `Error processing job XXX: 'expr'`
- 所有定时任务都是 pending 状态，从未执行 (last_run_at: null)
- 调度器进程运行正常，但任务不触发

**根因:**
`hermes/gateway/cron/scheduler.py` 代码里用 `schedule.expr`，但 jobs.json 存的是 `expression`

**修复:**
```bash
# 替换所有 schedule.expr 为 schedule.expression
sed -i 's/schedule\.expr/schedule.expression/g' \
  ~/Projects/13/Light-House/hermes/gateway/cron/scheduler.py

# 重启 gateway
pkill -f hermes-gateway
hermes gateway start
```

### 2. HTTP 429 - Engine Overloaded

**Symptoms:**
- Task runs but fails with `HTTP 429: The engine is currently overloaded`
- Job state shows "completed" but user received no output

**Root Causes:**
- Peak time execution (9:00 AM, 12:00 PM)
- Too many concurrent requests in the task
- Retry storms amplifying load

**Solution:**
```
# Shift execution time away from peak hours
# Instead of: 0 9 * * * (9:00 AM)
# Use:        0 8 * * * (8:00 AM) or 13 9 * * * (9:13 AM)
```

### 2. Missing croniter Package

**Symptoms:**
- `cronjob create` returns: "Cron expressions require 'croniter' package"
- Already ran `pip install croniter` but still fails

**Root Cause:**
- Package installed in wrong Python environment
- Hermes uses its own venv, not system Python
- `execute_code` tool and `terminal` tool may use different Python paths

**Solution:**
```bash
# Find the correct venv site-packages - check multiple locations:
# 1. ~/.hermes/hermes-agent/venv/lib/python*/site-packages
# 2. Check execute_code: import sys; print(sys.executable)

# Install to the correct location (use the path from execute_code)
python3 -m pip install --target=/Users/mac/.hermes/hermes-agent/venv/lib/python3.11/site-packages croniter

# If still failing, verify with execute_code:
# import sys; print(sys.path)  # Shows which site-packages are loaded
```

### 3. Task Ran But No Output Delivered

**Diagnosis Steps:**
```bash
# 1. List all jobs to check state
cronjob list

# 2. Check output directory for logs
ls -la ~/.hermes/cron/output/[job-id]/

# 3. Read the generated output file
cat ~/.hermes/cron/output/[job-id]/YYYY-MM-DD_HH-MM-SS.md

# 4. Check jobs.json for detailed status
cat ~/.hermes/cron/jobs.json | jq '.jobs[] | {id, state, last_error, last_status}'
```

**Common findings in output files:**
- Task prompt and instructions are logged
- Actual error appears at the end of the file
- HTTP 429 errors show up as final line

### 4. Telegram Notification Not Received (Job Status Shows "ok")

**Symptoms:**
- `cronjob list` shows `last_status: ok` and `state: scheduled`
- Output file exists and contains valid message
- User reports never receiving the notification

**Root Causes:**
1. **TELEGRAM_HOME_CHANNEL misconfigured**
   ```bash
   # Check current value
   grep TELEGRAM_HOME_CHANNEL ~/.hermes/.env
   
   # WRONG: TELEGRAM_HOME_CHANNEL=✓ Telegram token saved
   # CORRECT: TELEGRAM_HOME_CHANNEL=813280132
   ```
   During setup, the value might be accidentally set to a status message instead of the actual chat ID.

2. **Platform mismatch**
   - User is chatting on Feishu/Slack/Discord
   - But `deliver: telegram` is set in the job
   - User expects notification on the platform they're currently using

**Fix:**
```bash
# Fix the env var
sed -i '' 's/TELEGRAM_HOME_CHANNEL=.*/TELEGRAM_HOME_CHANNEL=YOUR_CHAT_ID/' ~/.hermes/.env

# Or change delivery target
cronjob update <job-id> deliver=feishu  # or discord, slack, etc.
```

### 4. "Once" Tasks That Expire

**Problem:**
- User creates a one-time task expecting it to repeat
- After it runs once, it never runs again
- Job state changes to "completed" and enabled=false

**Solution:**
- Change schedule from `"kind": "once"` to `"kind": "cron"`
- Set `"expression": "0 8 * * *"` (daily at 8 AM)
- Set `"repeat": {"times": null, "completed": 0}`

## Manual Job Creation (When Tools Fail)

If `cronjob create` is not working, manually edit `~/.hermes/cron/jobs.json`:

```json
{
  "jobs": [
    {
      "id": "unique-id-here",
      "name": "Task Name",
      "prompt": "Task instructions...",
      "skill": "skill-name",
      "schedule": {
        "kind": "cron",
        "expression": "0 8 * * *",
        "display": "daily at 08:00"
      },
      "enabled": true,
      "state": "pending",
      "next_run_at": "2026-04-09T08:00:00+08:00",
      "deliver": "telegram"
    }
  ]
}
```

## Prevention Checklist

- [ ] Use daily cron schedule instead of "once" for recurring tasks
- [ ] Set execution time to non-peak hours (avoid :00, use :13 or :47)
- [ ] Check that skill dependencies are installed before creating job
- [ ] Verify deliver target (telegram, discord, etc.) is configured
- [ ] Test the skill manually before scheduling it

## Related Issues

- HTTP 429 can also occur from web scraping too aggressively - add delays between requests
- NO_PROXY environment variable can break Telegram delivery - always unset it
- Long reports (>4000 chars) need segmentation for Telegram

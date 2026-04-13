---
name: knowledge-radar-system
description: Multi-source information gathering system with smart analysis tiering and dual backup (local + Notion). Optimizes API costs by applying full AI analysis only to high-heat content.
---

# Knowledge Radar System

Build an automated information gathering system that collects, analyzes, and stores data from multiple sources.

## Architecture

### Categories (5-way radar)
1. **Tech/AI**: HN, GitHub, HuggingFace, X/Twitter
2. **Finance**: WallStreetCN, 36kr, X/Twitter
3. **Industry**: RSS feeds, tech blogs
4. **Academic**: arXiv, HuggingFace Papers
5. **Social**: Weibo, V2EX, Reddit

### Schedule (every 12 hours, staggered)
- 08:00/20:00 - Tech/AI
- 09:00/21:00 - Finance
- 10:00/22:00 - Industry
- 11:00/23:00 - Academic
- 12:00/00:00 - Social

## Smart Analysis Strategy (Cost Optimization)

| Heat Level | Treatment | API Cost |
|------------|-----------|----------|
| ≥ 100 | Full analysis (AI summary + deep analysis + auto-tags + importance score) | High |
| < 100 | Basic info (title + link + heat only) | Low |

**Result**: ~70-80% API cost savings

## Storage

### Local
```
~/knowledge/
├── {category}/
│   ├── raw/       # Original scrape data
│   ├── reports/   # Generated reports
│   └── summaries/ # AI summaries
```

### Notion
- Database with fields: 名称, 来源, 分类, 链接, 热度, 摘要, 深度分析, 标签, 状态, 创建时间, 本地路径
- 5 category pages under parent "知识雷达"

## Implementation

### Step 1: Directory Structure
```bash
mkdir -p ~/knowledge/{tech-ai,finance,industry,academic,social}/{raw,reports,summaries}
```

### Step 2: X API Credentials
Create `~/.config/x-cli/config.yaml`:
```yaml
consumer_key: "YOUR_CONSUMER_KEY"
consumer_secret: "YOUR_CONSUMER_SECRET"
access_token: "YOUR_ACCESS_TOKEN"
access_token_secret: "YOUR_ACCESS_TOKEN_SECRET"
bearer_token: "YOUR_BEARER_TOKEN"
```

### Step 3: Python Script Core
```python
#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

HEAT_THRESHOLD = 100

def collect_hackernews():
    # Fetch top stories from HN API
    pass

def collect_github_trending():
    # Fetch trending repos from GitHub API
    pass

def collect_x_tweets():
    # X API with quota management
    quota_file = Path.home() / "knowledge/x_api_quota.json"
    # Check 500/month limit, update usage
    pass

def analyze_content(items):
    for item in items:
        item["heat"] = item.get("score", 0)
        item["needs_deep_analysis"] = item["heat"] >= HEAT_THRESHOLD
    return items
```

### Step 4: Cron Configuration
```bash
# Knowledge Radar - 5-way data collection
0 8,20 * * * /usr/bin/python3 /Users/mac/knowledge/knowledge-radar.py tech-ai
0 9,21 * * * /usr/bin/python3 /Users/mac/knowledge/knowledge-radar.py finance
0 10,22 * * * /usr/bin/python3 /Users/mac/knowledge/knowledge-radar.py industry
0 11,23 * * * /usr/bin/python3 /Users/mac/knowledge/knowledge-radar.py academic
0 0,12 * * * /usr/bin/python3 /Users/mac/knowledge/knowledge-radar.py social
```

### Step 5: Notion Integration (Optional)
1. Create integration at https://www.notion.so/my-integrations
2. Copy "Internal Integration Token"
3. Add connection to your database
4. Set `NOTION_TOKEN` environment variable

## Cost Considerations

- X API Free: 500 reads/month (use conservatively)
- Firecrawl: 500 pages/month free
- Notion API: Free tier sufficient

## Implementation Details

### Notion Sync Module

Create `notion_sync.py` for Chinese database fields with optional multi-database archiving:

```python
from notion_client import Client
from datetime import datetime
import os
from collections import defaultdict

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # Default/fallback database

# Type-based archiving: separate databases per content type
NOTION_DB_TECH_AI = os.getenv("NOTION_DB_TECH_AI", "")
NOTION_DB_FINANCE = os.getenv("NOTION_DB_FINANCE", "")
NOTION_DB_ACADEMIC = os.getenv("NOTION_DB_ACADEMIC", "")
NOTION_DB_SOCIAL = os.getenv("NOTION_DB_SOCIAL", "")
NOTION_DB_INDUSTRY = os.getenv("NOTION_DB_INDUSTRY", "")

# Source to database TYPE mapping (decouples routing from specific IDs)
SOURCE_DB_MAP = {
    "hackernews": "tech_ai",
    "github": "tech_ai",
    "huggingface": "tech_ai",
    "wallstreetcn": "finance",
    "36kr": "finance",
    "arxiv": "academic",
    "weibo": "social",
    "x_twitter": "social",
    "rss": "industry",
}

TYPE_TO_DB_ID = {
    "tech_ai": NOTION_DB_TECH_AI,
    "finance": NOTION_DB_FINANCE,
    "academic": NOTION_DB_ACADEMIC,
    "social": NOTION_DB_SOCIAL,
    "industry": NOTION_DB_INDUSTRY,
}


def get_database_id_for_source(source: str) -> str:
    """Route source to appropriate database with fallback"""
    db_type = SOURCE_DB_MAP.get(source, "default")
    db_id = TYPE_TO_DB_ID.get(db_type, "")
    return db_id if db_id else NOTION_DATABASE_ID


def sync_batch(items, category):
    """Sync items with per-database statistics"""
    success = 0
    db_stats = defaultdict(lambda: {"success": 0, "total": 0})
    
    for item in items:
        source = item.get("source", "unknown")
        db_type = SOURCE_DB_MAP.get(source, "default")
        db_stats[db_type]["total"] += 1
        
        if sync_item(item, category):  # sync_item uses get_database_id_for_source internally
            success += 1
            db_stats[db_type]["success"] += 1
    
    # Print per-database summary
    print(f"\n📊 Notion Sync [{category}]: {success}/{len(items)} total")
    for db_type, stats in sorted(db_stats.items()):
        db_id = get_database_id_for_source(db_type)[:8]
        print(f"  • {db_type:12} → {db_id}...: {stats['success']}/{stats['total']}")
    
    return success
```

**Benefits of type-based archiving:**
- Different content types go to different databases (better organization)
- Backward compatible: unconfigured types fall back to default database
- Clean separation between routing logic and database configuration
- Per-database statistics for monitoring

**Environment setup:**
```bash
# ~/.knowledge-radar-env
export NOTION_DATABASE_ID="xxx"          # Required: default database
export NOTION_DB_TECH_AI="xxx"           # Optional: Tech/AI database
export NOTION_DB_FINANCE="xxx"           # Optional: Finance database
# ... etc
```

### Loading Env Vars in Cron

Add to your main script to load from file when env vars not available:

```python
def run_category(category):
    # Load env vars from file for cron environment
    env_file = Path.home() / ".knowledge-radar-env"
    if env_file.exists() and not os.getenv("NOTION_TOKEN"):
        with open(env_file) as f:
            for line in f:
                if line.startswith("export ") and "=" in line:
                    key, val = line.replace("export ", "").strip().split("=", 1)
                    val = val.strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val
    # ... rest of function
```

## Pitfalls

- **X API Free tier is 500 reads/month** - implement quota tracking file to avoid hitting limit mid-month
- **X API OAuth 1.0a** requires all 5 credentials (consumer_key, consumer_secret, access_token, access_token_secret, bearer_token)
- **X API query must be URL encoded** - use `urllib.parse.quote()` to avoid "control characters" error
- **Heat threshold may need tuning per source** (HN scores vs X likes are different scales)
- **Notion API field names** - if your database uses Chinese field names (名称, 来源, 分类), map them properly
- **Notion multi_select vs select** - "分类" is often multi_select, not select - check your database structure
- **Notion API has rate limits** (~3 req/sec) - add delays for bulk imports
- **Cron environment** may not have same PATH or env vars as interactive shell - use full paths and load from file
- **GitHub API has 60 req/hour limit** for unauthenticated requests - fine for cron every 12 hours
- **Discovering Notion database structure** - If you have existing pages, search for them and inspect `properties` to find correct field names

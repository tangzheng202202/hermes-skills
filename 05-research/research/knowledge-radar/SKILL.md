---
name: knowledge-radar
description: "Multi-domain information collection system with automated crawling, local storage, and Notion backup. Collects Tech/AI, Finance, Industry, Academic, and Social data every 12 hours."
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [knowledge-base, information-collection, notion, automation, research]
---

# Knowledge Radar System

Five-domain automated information collection with dual storage (local + Notion).

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Data Sources  │────▶│   Hermes     │────▶│  Local Storage  │
│                 │     │  (cronjob)   │     │  ~/knowledge/   │
│ - Hacker News   │     └──────────────┘     └─────────────────┘
│ - GitHub        │              │
│ - HF Papers     │              ▼
│ - WallStreetCN  │     ┌─────────────────┐
│ - Weibo/V2EX    │────▶│  Notion Backup  │
│ - arXiv         │     │  (5 databases)  │
│ - RSS feeds     │     └─────────────────┘
└─────────────────┘
```

## Two Operating Modes

### Mode 1: Multi-Radar System (Default)
Five independent radars (Tech/AI, Finance, Industry, Academic, Social) each with their own schedule and database.

**Best for**: Broad monitoring across multiple domains

### Mode 2: Deep Research Daily Report 🔬
Single comprehensive daily report with AI-curated deep analysis.

**Best for**: Focused research with high signal-to-noise ratio

---

## Mode 2: Deep Research Daily Report

Instead of five separate radars, create ONE high-quality daily report:

### Workflow

```
08:00  Fetch from multiple sources
       ├─ HackerNews (tech trends)
       ├─ GitHub Trending (open source)
       ├─ HuggingFace Papers (AI research)
       └─ AI Newsletters (industry insights)

09:00  AI Analysis & Curation
       ├─ Filter by research value criteria
       ├─ Deep dive into 3-5 selected items
       └─ Generate structured report

09:30  Sync to Notion
       └─ Create single comprehensive page
```

### Research Value Criteria

AI filters content based on:

| Criteria | Weight | Description |
|----------|--------|-------------|
| **技术创新性** | ⭐⭐⭐⭐⭐ | New methods, architectures, or breakthroughs |
| **实用价值** | ⭐⭐⭐⭐ | Solves real problems, improves efficiency |
| **前沿程度** | ⭐⭐⭐⭐ | Represents latest advances in the field |
| **可扩展性** | ⭐⭐⭐ | Has broad application potential |
| **学术/工业影响** | ⭐⭐⭐ | From top institutions or influential teams |

### Report Structure

```markdown
# 📊 深度研究日报 - YYYY-MM-DD

## 🎯 今日精选 (3-5项)
### 1. [Title](link) - ⭐⭐⭐⭐⭐
**Source**: HN/GitHub/HF | **Field**: AI/Systems/Tools
**Core Contribution**: One-sentence summary of value
**Technical Depth**: Innovation points and technical details
**Use Cases**: Potential applications
**Resources**: Links to code, papers, demos
**Follow-up**: Recommended actions

## 📚 Paper Deep Dive
### Paper Title
**Authors/Institution**: 
**Core Innovation**: 
**Method Overview**: 
**Experimental Results**: 
**Personal Assessment**: Why it matters

## 🛠️ Open Source Spotlight
### Project Name
**GitHub**: 
**Stars/Trend**: 
**Core Features**: 
**Technical Highlights**: 
**Use Cases**: 
**Recommendation**: 

## 💡 Tech Trend Insights
1. **Hot Directions**: Emerging technologies
2. **Paradigm Shifts**: New methodologies
3. **Tool Evolution**: Development tool progress
4. **Industry Dynamics**: Commercial trends

## 🎯 Tomorrow's Watchlist
- [ ] Follow-up item 1
- [ ] Follow-up item 2
```

### Setup: Deep Research Daily Report

```bash
# Create single daily report job (09:00 daily)
openclaw cron add \
  --name "🔬 深度研究日报" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --agent main-agent \
  --session isolated \
  --message "执行每日深度研究分析任务：

## 阶段一：数据抓取
cd ~/.hermes/skills/openclaw-imports/news-aggregator-skill
export -n NO_PROXY && export -n no_proxy

# Core sources
python3 scripts/fetch_news.py --source hackernews --limit 20 --deep --save --outdir /tmp/radar/$(date +%Y%m%d)
python3 scripts/fetch_news.py --source github --limit 15 --deep --save --outdir /tmp/radar/$(date +%Y%m%d)
python3 scripts/fetch_news.py --source huggingface --limit 15 --deep --save --outdir /tmp/radar/$(date +%Y%m%d)
python3 scripts/fetch_news.py --source ai_newsletters --limit 10 --deep --save --outdir /tmp/radar/$(date +%Y%m%d)

## 阶段二：深度分析
读取所有JSON，按5维标准筛选高价值内容，深度分析3-5项

## 阶段三：生成报告
创建结构化Markdown报告：今日精选、论文精读、开源项目、趋势洞察

## 阶段四：同步Notion
创建页面：📊 深度研究日报 - YYYY-MM-DD
标签：#研究 #日报 #科技

## 完成通知
Telegram推送：精选数量、重点推荐、Notion链接" \
  --channel telegram \
  --announce \
  --timeout-seconds 600
```

### Comparison

| Aspect | Multi-Radar (Mode 1) | Deep Research (Mode 2) |
|--------|---------------------|------------------------|
| **Frequency** | 2×/day per category | 1×/day |
| **Volume** | 50+ items/day | 3-5 curated items |
| **Depth** | Basic summaries | Deep analysis (200+ words/item) |
| **AI Cost** | Higher (process everything) | Lower (selective analysis) |
| **Best For** | Broad monitoring | Focused research |
| **Notion** | 5 databases | 1 database |
| **Time** | 5 min read/category | 10 min comprehensive read |

**Recommendation**: Start with Mode 2 (Deep Research) for personal use. Switch to Mode 1 (Multi-Radar) if you need comprehensive market monitoring.

---

## Five Radar Categories

| Category | Sources | Source Keys | Update Times (UTC+8) | Storage Path |
|----------|---------|-------------|---------------------|--------------|
| **🤖 Tech/AI** | Hacker News, GitHub, Hugging Face Papers | `hackernews`, `github`, `huggingface` | 08:00, 20:00 | `~/knowledge/tech-ai/` |
| **💰 Finance** | 华尔街见闻, 36氪 | `wallstreetcn`, `36kr` | 09:00, 21:00 | `~/knowledge/finance/` |
| **📊 Industry** | RSS feeds, Tech Blogs | `rss` (custom parser) | 10:00, 22:00 | `~/knowledge/industry/` |
| **📚 Academic** | arXiv, Hugging Face Papers | `arxiv`, `huggingface` | 11:00, 23:00 | `~/knowledge/academic/` |
| **💬 Social** | 微博热搜, V2EX, X/Twitter | `weibo`, `v2ex`, `x_twitter` | 12:00, 00:00 | `~/knowledge/social/` |

**Why stagger by 1 hour?** Prevents API rate limits and server overload (HTTP 429 errors).

### Source Key Reference

Available source keys in `news-aggregator-skill`:

| Key | Source | Category |
|-----|--------|----------|
| `hackernews` | Hacker News | Tech |
| `github` | GitHub Trending | Tech |
| `huggingface` | Hugging Face Papers | AI/Academic |
| `arxiv` | arXiv Papers | Academic |
| `wallstreetcn` | 华尔街见闻 | Finance |
| `36kr` | 36氪 | Finance/Tech |
| `weibo` | 微博热搜 | Social |
| `v2ex` | V2EX | Tech/Social |
| `producthunt` | Product Hunt | Tech |
| `ai_newsletters` | AI Newsletters aggregate | AI |
| `podcasts` | Tech Podcasts | Audio |
| `essays` | Essays (PG, etc.) | Reading |
| `x_twitter` | X/Twitter (read-only) | Social/Tech/Finance |

**⚠️ X/Twitter API Limits:**
- **Free tier**: 500 reads/month (~16/day), cannot post
- **Basic**: $100/month, 10K reads/month
- **Pro**: $5000/month, 1M reads/month

With Free tier and 5 categories updating every 12 hours:
- 5 categories × 2×/day × 5 accounts × 3 tweets = 150 tweets/day
- **Quota runs out in 3-4 days!**

**Solutions**:
1. Reduce X fetches to once per day (5 × 1 × 5 × 3 = 75/day = ~6 days)
2. Reduce accounts per category (3 instead of 5)
3. Upgrade to Basic tier ($100/month)
4. Skip X entirely, use other sources

## Prerequisites

1. **news-aggregator-skill** - for data collection
2. **croniter** package - for scheduling
3. **notion** skill + API key - for backup

## Setup

### 1. Create Local Directory Structure

```python
from pathlib import Path

base_dir = Path.home() / "knowledge"
categories = ["tech-ai", "finance", "industry", "academic", "social"]

for cat in categories:
    (base_dir / cat / "raw").mkdir(parents=True, exist_ok=True)
    (base_dir / cat / "reports").mkdir(parents=True, exist_ok=True)
    (base_dir / cat / "summaries").mkdir(parents=True, exist_ok=True)
```

Directory layout:
```
~/knowledge/
├── tech-ai/
│   ├── raw/          # Original crawled data (JSON)
│   ├── reports/      # Analysis reports (Markdown)
│   └── summaries/    # Digest summaries
├── finance/
├── industry/
├── academic/
└── social/
```

### 2. Configure Notion Backup

**Step 2.1: Create Integration**
1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it (e.g., "Hermes Knowledge Radar")
4. Copy the **Internal Integration Token** (starts with `ntn_`)
5. Add to `~/.hermes/.env`:
   ```
   NOTION_API_KEY=ntn_xxxxx
   ```

**Step 2.2: Create Parent Page**
1. In Notion, create a new page titled "📡 知识雷达"
2. The page can be empty or have introductory text

**Step 2.3: Share Page with Integration (CRITICAL)**
This step is often missed and causes 404/validation errors:
1. Open your "📡 知识雷达" page
2. Click the **...** (three dots) in the top right
3. Scroll down to **Add connections** (or "Connect to")
4. Search for your integration name (e.g., "Hermes Knowledge Radar")
5. Click **Confirm**

**Step 2.4: Get Page ID**
1. Copy the page URL: `https://www.notion.so/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
2. The 32-character string is your `parent_page_id`
3. Create 5 sub-pages or databases for each category

**Common Error**: "Could not find page with ID" means you forgot Step 2.3 (sharing).

### 3. Setup X/Twitter (Optional, Read-only)

If using X as a data source:

**Step 3.1: Get X API Credentials**
1. Go to https://developer.x.com/en/portal/projects-and-apps
2. Create app with OAuth 1.0a enabled
3. Set permissions to "Read and Write" (required for access tokens)
4. Generate Access Token and Secret
5. Note: Free tier only supports READ operations

**Step 3.2: Install x-cli**
```bash
uv tool install git+https://github.com/Infatoshi/x-cli.git
```

**Step 3.3: Configure Credentials**
```bash
mkdir -p ~/.config/x-cli
cat > ~/.config/x-cli/.env <<'EOF'
X_API_KEY=your_consumer_key
X_API_SECRET=your_consumer_secret
X_BEARER_TOKEN=your_bearer_token
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_secret
EOF
chmod 600 ~/.config/x-cli/.env
```

**Step 3.4: Create Fetch Script**
Save as `scripts/fetch_x.py`:
```python
#!/usr/bin/env python3
import subprocess, json, sys
from datetime import datetime

ACCOUNTS = {
    "tech_ai": ["OpenAI", "DeepMind", "ylecun", "karpathy"],
    "finance": ["naval", "ID_AA_Carmack"],
    "industry": ["paulg", "sama", "elonmusk"],
    "academic": ["hardmaru", "goodfellow_ian"],
    "social": ["BreakingNews", "TechCrunch"]
}

def fetch_user_tweets(username, limit=3):
    try:
        result = subprocess.run(
            ["x-cli", "-j", "user", "timeline", username, "--max", str(limit)],
            capture_output=True, text=True, timeout=30
        )
        return json.loads(result.stdout) if result.returncode == 0 else []
    except:
        return []

category = sys.argv[1]
for account in ACCOUNTS.get(category, []):
    tweets = fetch_user_tweets(account, limit=3)
    # Process and save tweets...
```

### 4. Create Cron Jobs (Every 12 Hours, Staggered)

**⚠️ Important: Choose the Right Scheduler**

There are TWO cron systems available:

| System | Command | Reliability | Use Case |
|--------|---------|-------------|----------|
| **OpenClaw Cron** | `openclaw cron add` | ✅ High - Integrated with OpenClaw gateway, proven stable | Production daily tasks |
| **Hermes Cronjob** | `cronjob create` | ⚠️ Lower - Separate tool, may have scheduling issues | Quick testing only |

**Recommendation**: Use `openclaw cron` for all production knowledge radar tasks.

#### Option A: OpenClaw Cron (Recommended for Production)

```bash
# Tech/AI - 08:00 and 20:00
openclaw cron add \
  --name "📡 知识雷达-科技AI" \
  --cron "0 8,20 * * *" \
  --tz "Asia/Shanghai" \
  --agent main-agent \
  --session isolated \
  --message "抓取科技/AI资讯并同步到Notion。任务: 1) 使用 news-aggregator-skill 抓取: hackernews, github, huggingface 2) 生成中文分析报告 3) 保存到本地: ~/knowledge/tech-ai/ 4) 同步到Notion" \
  --channel telegram \
  --announce \
  --timeout-seconds 600
```

#### Option B: Hermes Cronjob Tool (For Testing Only)

**Note**: If `cronjob` tool fails with "croniter not found", install it first:
```bash
python3 -m pip install --target=~/.hermes/hermes-agent/venv/lib/python3.x/site-packages croniter
```

```bash
# Tech/AI - 08:00 and 20:00
cronjob create \
  --name "📡 知识雷达-科技AI" \
  --schedule "0 8,20 * * *" \
  --skill news-aggregator-skill \
  --prompt "抓取科技/AI资讯并同步到Notion。任务: 1) 使用 news-aggregator-skill 抓取: hackernews, github, huggingface 2) 生成中文分析报告 3) 保存到本地: ~/knowledge/tech-ai/ 4) 同步到Notion数据库 'rader'。Notion Database ID: <your_db_id>" \
  --deliver telegram

# Finance - 09:00 and 21:00  
cronjob create \
  --name "📡 知识雷达-财经市场" \
  --schedule "0 9,21 * * *" \
  --skill news-aggregator-skill \
  --prompt "抓取财经/市场资讯并同步到Notion。任务: 1) 抓取: wallstreetcn, 36kr 2) 生成中文分析报告 3) 保存到本地: ~/knowledge/finance/ 4) 同步到Notion" \
  --deliver telegram

# Industry - 10:00 and 22:00
cronjob create \
  --name "📡 知识雷达-行业追踪" \
  --schedule "0 10,22 * * *" \
  --skill news-aggregator-skill \
  --prompt "抓取行业动态并同步到Notion。任务: 1) 抓取: RSS订阅源, 技术博客 2) 生成中文分析报告 3) 保存到本地: ~/knowledge/industry/ 4) 同步到Notion" \
  --deliver telegram

# Academic - 11:00 and 23:00
cronjob create \
  --name "📡 知识雷达-学术研究" \
  --schedule "0 11,23 * * *" \
  --skill news-aggregator-skill \
  --prompt "抓取学术研究资讯并同步到Notion。任务: 1) 抓取: huggingface papers, arxiv 2) 生成中文分析报告(论文摘要、关键创新点) 3) 保存到本地: ~/knowledge/academic/ 4) 同步到Notion" \
  --deliver telegram

# Social - 12:00 and 00:00
cronjob create \
  --name "📡 知识雷达-社交媒体" \
  --schedule "0 12,0 * * *" \
  --skill news-aggregator-skill \
  --prompt "抓取社交媒体热点并同步到Notion。任务: 1) 抓取: 微博, V2EX 2) 生成中文分析报告 3) 保存到本地: ~/knowledge/social/ 4) 同步到Notion" \
  --deliver telegram
```

**Manual Creation** (if cronjob tool fails):
Edit `~/.hermes/cron/jobs.json` directly with the job definitions.

## Data Flow

1. **Fetch**: `fetch_news.py --source <source> --save`
2. **Process**: Generate markdown reports with analysis
3. **Store Local**: Save to `~/knowledge/<category>/`
4. **Backup Notion**: Create/update database entries

## Notion Database Schema

Each category database should have these fields (adjust for your workspace language):

### For Chinese Workspaces:
| Field Name (Chinese) | Type | Description |
|---------------------|------|-------------|
| 名称 | Title | Article/paper title |
| 来源 | Select | Hacker News, GitHub, Hugging Face, arXiv, 华尔街见闻, 36氪, 微博, V2EX, etc. |
| 分类 | Multi-select | Tech, AI/ML, Finance, Academic, Social |
| 链接 | URL | Original source URL |
| 热度 | Number | Score/stars/upvotes/heat |
| 摘要 | Rich text | Brief Chinese summary |
| 深度分析 | Rich text | Deep analysis and insights |
| 标签 | Multi-select | Custom tags for filtering |
| 状态 | Select | 🆕 新抓取 / ✅ 已阅读 / 📦 已归档 |
| 创建时间 | Date | When the entry was created |
| 本地路径 | Rich text | Path to local markdown file |

### For English Workspaces:
| Field Name | Type | Description |
|------------|------|-------------|
| Name | Title | Article/paper title |
| Source | Select | HN, GitHub, HF, arXiv, etc. |
| Category | Multi-select | Tech, AI/ML, Finance, etc. |
| URL | URL | Original source URL |
| Heat Score | Number | Popularity metric |
| Summary | Rich text | Brief summary |
| Deep Analysis | Rich text | Detailed insights |
| Tags | Multi-select | Custom tags |
| Status | Select | 🆕 New / ✅ Read / 📦 Archived |
| Created | Date | Timestamp |
| Local Path | Rich text | File path |

**Important**: Notion uses localized field names. For Chinese workspaces, the title field is "名称" not "Name". Check your workspace language settings.

## Configuration File

The system saves configuration to:
```
~/.hermes/knowledge_radar_config.json
```

Example structure:
```json
{
  "notion": {
    "api_key": "ntn_...",
    "database_id": "33c6a09f-...",
    "categories": {
      "tech_ai": {"name": "🤖 科技/AI 资讯", "page_id": "..."},
      "finance": {"name": "💰 财经/市场", "page_id": "..."},
      "industry": {"name": "📊 行业追踪", "page_id": "..."},
      "academic": {"name": "📚 学术研究", "page_id": "..."},
      "social": {"name": "💬 社交媒体", "page_id": "..."}
    }
  },
  "local": {
    "base_dir": "~/knowledge",
    "categories": ["tech-ai", "finance", "industry", "academic", "social"]
  },
  "sources": {
    "tech_ai": ["hackernews", "github", "huggingface", "x_twitter"],
    "finance": ["wallstreetcn", "36kr", "x_twitter"],
    "industry": ["rss", "x_twitter"],
    "academic": ["arxiv", "huggingface"],
    "social": ["weibo", "v2ex", "x_twitter"]
  },
  "x_api": {
    "enabled": true,
    "tier": "free",
    "monthly_limit": 500,
    "warning": "Free tier depletes fast with 5 categories. Reduce frequency or accounts.",
    "accounts": {
      "tech_ai": ["OpenAI", "karpathy", "ylecun"],
      "finance": ["naval", "ID_AA_Carmack"],
      "industry": ["paulg", "sama"],
      "academic": ["hardmaru", "goodfellow_ian"],
      "social": ["BreakingNews"]
    }
  },
  "schedule": {
    "tech_ai": ["08:00", "20:00"],
    "finance": ["09:00", "21:00"],
    "industry": ["10:00", "22:00"],
    "academic": ["11:00", "23:00"],
    "social": ["12:00", "00:00"]
  }
}
```

## Troubleshooting

### Jobs Not Running (cronjob vs openclaw cron)

**Problem**: Tasks created with `cronjob` tool don't execute

**Root Cause**: Two separate cron systems exist:
1. `cronjob` tool - Hermes standalone scheduler (less reliable)
2. `openclaw cron` - OpenClaw integrated scheduler (production-grade)

**Solution**: Migrate to OpenClaw cron:

```bash
# Check which scheduler your job is using
cronjob list          # Shows Hermes cron jobs
openclaw cron list    # Shows OpenClaw cron jobs

# Delete from Hermes cronjob
cronjob remove --job-id <id>

# Recreate in OpenClaw cron (stable)
openclaw cron add \
  --name "任务名称" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --agent main-agent \
  --session isolated \
  --message "任务内容..." \
  --channel telegram \
  --announce
```

**Verification**: After migration, job appears in `openclaw cron list` with status `idle` or `ok`.

### Cronjob fails with "croniter not found"\nInstall croniter in the correct Python environment:
```bash
# Find your venv
ls ~/.hermes/hermes-agent/venv/lib/python*/site-packages/

# Install croniter
python3 -m pip install --target=/Users/mac/.hermes/hermes-agent/venv/lib/python3.11/site-packages croniter
```

### Notion "Could not find page with ID"
**Cause**: Page not shared with integration
**Fix**: 
1. Open the Notion page in browser
2. Click **...** → **Add connections** → Select your integration
3. Retry the API call

### Notion "Name is not a property that exists"
**Cause**: Field name mismatch due to workspace language
**Fix**: Use localized field names:
- Chinese workspaces: "名称" not "Name"
- English workspaces: "Name" not "名称"
- Check existing fields with: `GET /v1/databases/{database_id}`

### Notion 401 Unauthorized
**Causes**:
- Invalid API key
- Integration doesn't have page access
- Token expired (re-copy from my-integrations)

### API 429 Rate Limit (Engine Overloaded)
**Cause**: Too many requests at once
**Fix**: Jobs are staggered by 1 hour in the schedule. If still hitting limits:
- Reduce `limit` parameter in fetch_news.py
- Add delay between requests
- Use `--no-save` for testing
### X API "CreditsDepleted" Error

**Cause**: Free tier only allows 500 reads/month
**Error**: `RuntimeError: API error (HTTP 402): {"title":"CreditsDepleted"...}`

**Math Check**:
- 5 categories × 2×/day × 5 accounts × 3 tweets = 150 tweets/day
- 150 × 30 days = 4,500 tweets/month
- Free tier: 500/month
- **Result**: Quota exhausted in 3-4 days!

**Recommended Config (Free Tier)**:
Only enable X for 2 most important categories:

```json
{
  "x_api": {
    "enabled_for": ["tech_ai", "finance"],  // Only 2 categories
    "accounts": {
      "tech_ai": ["OpenAI", "karpathy", "ylecun"],  // 3 accounts
      "finance": ["naval", "zhusu"]  // 2 accounts
    },
    "limit_per_account": 2,  // 2 tweets each
    "schedule": {
      "tech_ai": "08:30",    // Once daily, staggered
      "finance": "09:30"
    }
  }
}
```

**Usage**: 5 accounts × 2 tweets × 30 days = 300 reads/month ✓ (fits in 500)

**Fixes**:
1. Limit to 2 categories (as shown above)
2. Reduce to daily fetches (not twice daily)
3. Reduce accounts per category to 2-3
4. Upgrade to Basic tier ($100/month for 10K reads)
5. Remove X from sources entirely

### X CLI "401 Unauthorized"
**Causes**:
- Missing or incorrect OAuth credentials
- Bearer Token contains URL-encoded characters (`%2B` instead of `+`)
- App doesn't have "Read and Write" permissions

**Fixes**:
1. Decode Bearer Token: `urllib.parse.unquote(token)`
2. Regenerate Access Token with "Read and Write" permissions
3. Verify all 5 credentials in `~/.config/x-cli/.env`

### Empty results from data sources
- Check `news-aggregator-skill` is properly installed
- Some sources require Playwright: `playwright install chromium`
- Verify source keys are correct: `hackernews`, `github`, `huggingface`, etc.
- Check network connectivity and proxy settings

### Data not syncing to Notion
1. Check local files were created: `ls ~/knowledge/tech-ai/raw/`
2. Verify Notion API key is set: `grep NOTION ~/.hermes/.env`
3. Check database ID is correct in config
4. Review cron job logs: `~/.hermes/cron/output/{job_id}/`

## Best Practices

1. **Stagger Jobs**: Never run all 5 jobs simultaneously. The 1-hour stagger prevents API overload.

2. **Local First**: Always save to local disk before Notion sync. This prevents data loss if Notion API fails.

3. **Use Categories**: Tag entries with multiple categories for cross-domain insights.

4. **Archive Old Entries**: Use the "状态" field to track read/unread status.

5. **Monitor Logs**: Check `~/.hermes/cron/output/` regularly for errors.

6. **Backup Config**: Keep a copy of `knowledge_radar_config.json` - it contains all your IDs.

## Smart Analysis Strategy (Cost Optimization)

**Problem**: Analyzing every fetched item with AI is expensive and slow.

**Solution**: Use "heat" (community engagement) as a filter.

### Heat-Based Filtering

| Heat Score | Treatment | Fields Populated | Cost |
|------------|-----------|------------------|------|
| **≥ 100** | 🔥 Full analysis | Title + Summary + Deep Analysis + Tags + Importance Score | High |
| **< 100** | 💤 Basic info only | Title + Link + Source + Heat | Low |

**Benefits**:
- 70-80% cost reduction
- Focus on community-validated content
- Faster processing

### Implementation

Add to your config:

```json
{
  "analysis_strategy": {
    "mode": "smart",
    "threshold": 100,
    "high_heat": {
      "generate_summary": true,
      "deep_analysis": true,
      "auto_tag": true,
      "importance_score": true
    },
    "low_heat": {
      "generate_summary": false,
      "deep_analysis": false,
      "auto_tag": false,
      "importance_score": false
    }
  }
}
```

### Example

**High Heat Item** (1108 points on HN):
```
Title: "Git commands I run before reading any code"
Summary: "7 essential git commands for exploring new codebases..."
Deep Analysis: "Core value for onboarding, integrates with AI tools..."
Tags: git, code-reading, developer-tools
Importance: 9/10
```

**Low Heat Item** (42 points on HN):
```
Title: "Some obscure tool release"
Summary: (empty - skipped)
Deep Analysis: (empty - skipped)
Tags: (empty - skipped)
→ User clicks link if interested
```

### Adjusting Threshold

- **Higher threshold (200+)**: Only truly viral content gets analyzed. Maximum savings.
- **Lower threshold (50+)**: More items analyzed, higher cost but better coverage.
- **Per-category thresholds**: Finance might need lower threshold than Tech.

## Keywords for Auto-Expansion

The news-aggregator-skill auto-expands keywords:
- `AI` → `AI,LLM,GPT,Claude,Agent,RAG,DeepSeek`
- `Crypto` → `Bitcoin,ETH,DeFi,Web3,Blockchain`
- `Finance` → `Stock,Market,FED,Interest,ETF`

Use these to filter relevant content.

---
name: deep-research-daily
description: "Automated deep research pipeline: fetch from tech sources (HN, GitHub, HF), apply research-value filtering, generate curated reports with analysis, sync to Notion. Use when user wants daily tech intelligence, research briefings, or knowledge radar automation."
tags: [research, automation, notion, daily-report, tech-intelligence]
---

# Deep Research Daily Pipeline

Generate high-value research reports from tech sources with personal analysis and Notion sync.

## Workflow

### Phase 1: Data Collection

Fetch from high-signal sources:

```bash
export -n NO_PROXY && export -n no_proxy
cd ~/.hermes/skills/openclaw-imports/news-aggregator-skill

# Core sources
python3 scripts/fetch_news.py --source hackernews --limit 20 --deep --save --outdir /tmp/radar_$(date +%Y%m%d)
python3 scripts/fetch_news.py --source github --limit 15 --save --outdir /tmp/radar_$(date +%Y%m%d)
python3 scripts/fetch_news.py --source huggingface --limit 15 --save --outdir /tmp/radar_$(date +%Y%m%d)
python3 scripts/fetch_news.py --source ai_newsletters --limit 10 --save --outdir /tmp/radar_$(date +%Y%m%d)
```

### Phase 2: Research Value Filtering

Apply **5-dimension scoring** (1-5 stars):

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| **Technical Innovation** | ⭐⭐⭐⭐⭐ | Novel methods, architectures, breakthroughs |
| **Practical Value** | ⭐⭐⭐⭐ | Solves real problems, improves efficiency |
| **Cutting-edge** | ⭐⭐⭐⭐ | Represents latest domain progress |
| **Scalability** | ⭐⭐⭐ | Broad application potential |
| **Impact** | ⭐⭐⭐ | From top institutions/influential teams |

**Selection target**: Top 10-20% with at least 4⭐ overall.

### Phase 3: Deep Analysis Template

For each selected item:

```markdown
### N. [Title](URL) - ⭐⭐⭐⭐⭐
**Source**: HN/GitHub/HF | **Domain**: AI/Sys/Tool

**Core Contribution**: One-sentence value prop

**Technical Depth**:
- Key innovations
- Architecture details
- Implementation highlights

**Applications**: Where/how it can be used

**Resources**: Paper, code, demo links

**Follow-up**: 🔥 Strong recommend / 👀 Worth watching / ⚡ Quick check
```

### Phase 4: Research Report Structure

```markdown
# 📊 Deep Research Daily - YYYY-MM-DD

## 🎯 Today's Picks (N items)
[Selected items with full analysis]

## 📚 Paper Deep Dive
[If relevant: detailed paper analysis]

## 🛠️ Open Source Spotlight
[Project reviews]

## 💡 Trend Insights
- **Hot Directions**: Emerging tech areas
- **Paradigm Shifts**: New methodologies
- **Tool Evolution**: Dev tool progress
- **Industry Moves**: Commercial trends

## 🎯 Tomorrow's Watchlist
- [ ] Actionable follow-ups

## 📊 Stats
| Metric | Value |
|--------|-------|
| Sources | HN, GH, HF, Newsletters |
| Crawled | N items |
| Selected | N items (X%) |
| High Value | N items |
```

### Phase 5: Notion Sync

```bash
# Requires: NOTION_API_KEY in ~/.hermes/.env
# Notion integration must be shared with target database

curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "YOUR_DB_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "📊 Research Daily - YYYY-MM-DD"}}]},
      "Tags": {"multi_select": [{"name": "研究"}, {"name": "日报"}, {"name": "科技"}]},
      "Date": {"date": {"start": "YYYY-MM-DD"}}
    }
  }'
```

### Phase 6: Delivery

Send Telegram summary with:
- Count of high-value items found
- Top 2-3 recommendations with links
- Notion page link (if synced)

## Automation Setup

```bash
# Daily at 9 AM
cronjob create \
  --name "🔬 Deep Research Daily" \
  --schedule "0 9 * * *" \
  --skill deep-research-daily \
  --deliver telegram
```

## Prerequisites

- news-aggregator-skill installed
- NOTION_API_KEY configured
- Notion database created and shared with integration
- Playwright installed (for HF Papers): `playwright install chromium`

## Output Standards

1. **Curated over comprehensive**: Quality > quantity
2. **Personal judgment**: Include opinions and insights
3. **Actionable**: Clear follow-up recommendations
4. **Visual**: Use emoji, tables, formatting
5. **Persistent**: Sync to Notion for reference

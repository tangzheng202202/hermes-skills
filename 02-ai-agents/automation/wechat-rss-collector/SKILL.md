---
name: wechat-rss-collector
description: Collect WeChat public account articles via RSSHub and publish to Feishu Docs. Includes RSS mirror discovery, deduplication, markdown generation, and automated cron scheduling.
version: 2.0.0
triggers:
  - "监控公众号"
  - "RSS抓取"
  - "飞书知识库"
  - "定时收集文章"
  - "wechat articles"
  - "公众号文章采集"
prerequisites:
  - RSSHub mirror availability
  - Feishu App credentials (APP_ID, APP_SECRET)
  - Feishu chat_id for notifications
  - Python 3.8+
  - feedparser, requests, beautifulsoup4
---

# WeChat RSS Collector + Feishu Publisher

## Overview

Complete pipeline for monitoring WeChat public accounts via RSS and publishing to Feishu.

## Architecture

1. **RSS Discovery**: Find working RSSHub mirror (rsshub.pseudoyu.com recommended)
2. **Collection**: Python script fetches RSS, parses XML, filters by date, deduplicates
3. **Storage**: Local markdown files + Feishu Docs upload
4. **Scheduling**: Daily cron at 09:00 with Telegram notifications

## Key Implementation Details

### RSS Route (Verified Working)
- Primary: `https://rsshub.app/wechat/mp/wx_zbus_xcbmtyn/{biz_or_id}`
- Alternative: `https://rsshub.app/wechat/feeddd/{id}` (for full text)
- Old route: `https://rsshub.pseudoyu.com/wechat/sogou/{encoded_name}` (may be deprecated)
- Returns: XML with item (title, link, pubDate, description, content)
- Date format: `Fri, 27 Mar 2026 08:11:04 GMT`

**Getting RSS URL for a WeChat Account:**
1. Open the public account's history page
2. Extract `__biz` parameter from URL (base64 encoded)
3. Format: `https://rsshub.app/wechat/mp/wx_zbus_xcbmtyn/{biz_value}`

### Feishu API Strategy

**1. Docs API** (`docx/v1/documents`)
- Creates cloud documents in "My Documents"
- Requires: `docs:doc:write` permission
- Document URL format: `https://feishu.cn/docx/{document_id}`
- **Note**: Creates empty documents; content requires Block API

**2. Wiki API** (`wiki/v2/spaces/{space_id}/nodes`)
- Creates documents directly in Wiki knowledge base
- Requires: `wiki:wiki:write` permission
- **Critical**: App must be added as member to Wiki space with "Can Edit" permission
- Space ID format: `space_xxxxxxxx` (from Wiki settings URL)

**3. IM Message API** (`im/v1/messages`)
- Send notifications to P2P chats or groups
- Requires: `im:message:send`, `im:message.group_msg` permissions
- chat_id can be P2P (starts with `oc_`) or Group (starts with `oc_`)

### Feishu Docx Block API Format (Critical)

**Block Type Values (must be integers, not strings):**
- `1` - Page (document root)
- `2` - Text (standard paragraph)
- `3` - Heading 1
- `4` - Heading 2
- `5` - Heading 3
- `6` - Heading 4
- `7` - Heading 5
- `8` - Heading 6
- `9` - Heading 7
- `10` - Heading 8
- `11` - Heading 9
- `12-46` - Other block types (list, code, quote, etc.)
- `999` - Callout

**Example: Adding text content to document:**
```python
def add_text_block(token: str, doc_id: str, parent_block_id: str, content: str):
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    data = {
        "children": [
            {
                "block_type": 2,  # Integer! Not "text"
                "text": {
                    "elements": [
                        {
                            "type": "text_run",
                            "text_run": {
                                "content": content,
                                "text_style": {}
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    resp = requests.post(url, headers=headers, json=data)
    return resp.json()
```

**Common error:** Using `"block_type": "text"` returns `field validation failed` with code 99992402. Must use integer values.

### Authentication
```python
def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
    return resp.json()["tenant_access_token"]
```

### Deduplication
- History file: `~/.wechat_articles/.history.json`
- Key: Article link URL
- Value: {title, date, source}
- Alternative: MD5 hash of article title + date

### Multi-Platform Notifications
**Telegram:**
```python
def send_telegram_message(bot_token: str, chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})
```

**Feishu:**
```python
def send_feishu_message(token: str, chat_id: str, message: str):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    requests.post(url, headers={"Authorization": f"Bearer {token}"},
                  params={"receive_id_type": "chat_id"},
                  json={"receive_id": chat_id, "msg_type": "text",
                        "content": json.dumps({"text": message})})
```

## Commands

```bash
# Normal run (today's articles only)
python3 ~/wechat_collector.py

# Test mode (3 articles per account)
python3 ~/wechat_collector.py --all

# Local only (no Feishu)
python3 ~/wechat_collector.py --no-feishu

# Specific date
python3 ~/wechat_collector.py --date 2026-04-11
```

## Pitfalls

1. **RSSHub timeouts**: Public instances block; use mirrors or add delays between requests
2. **RSSHub route deprecation**: As of 2026-04-11, the following routes return NotFound errors on tested mirrors (pseudoyu.com, rssforever.com, rsshub.app):
   - `/wechat/mp/wx_zbus_xcbmtyn/{id}` - Returns "NotFoundError"
   - `/wechat/feeddd/{id}` - Returns "NotFoundError"
   - `/wechat/sogou/{encoded_name}` - May be deprecated
3. **Fallback when RSS unavailable**: Use local history file as fallback:
   ```python
   HISTORY_FILE = Path.home() / "wechat_articles" / ".history.json"
   # Parse history file for today's articles when RSSHub fails
   ```
4. **Feishu 400 errors**: App permissions need republishing in Feishu Developer Console
5. **Wiki permission denied**: App must be added to Wiki space members with "Can Edit" permission
   - Error: `permission denied: wiki space permission denied, tenant needs edit permission`
   - Fix: Wiki Settings → Member Management → Add App → Grant Edit Permission
6. **Date parsing**: GMT dates need conversion to local time
7. **Content writing**: Docx block API is complex; documents created empty by default
8. **chat_id format**: P2P and Group chat_ids both start with `oc_`, distinguish by context
9. **History stale**: Clear .history.json if reprocessing needed
10. **RSS feed content**: Some routes return summary only; use `feeddd` route for full content (when available)

## Working Example Configuration

```python
# Account RSS mapping (verified working as of 2026-04-11)
ACCOUNTS = {
    "Draco正在VibeCoding": "https://rsshub.app/wechat/mp/wx_zbus_xcbmtyn/Draco_Daily",
    "AI寒武纪": "https://rsshub.app/wechat/mp/wx_zbus_xcbmtyn/AI_himao",
    "左岸AI": "https://rsshub.app/wechat/mp/wx_zbus_xcbmtyn/leftbankai",
    "老金带你玩AI": "https://rsshub.app/wechat/mp/wx_zbus_xcbmtyn/wlaixkj"
}

# Notification targets
FEISHU_CHAT_ID = "oc_f9135e7516510373d91fed5756d62d7d"  # P2P with Ningyao
TELEGRAM_CHAT_ID = "813280132"  # Your Telegram chat ID

# Cron schedule
# 0 9 * * * /usr/bin/python3 /path/to/wechat_collector.py >> /var/log/wechat.log 2>&1
```

## Fallback Strategies When RSS Fails

### Option 1: Browser Automation (Recommended for Single Articles)

When `web_extract` returns "Unauthorized" for WeChat MP URLs (common as of 2026-04-11), use browser automation:

```python
# Step 1: Navigate to article
browser_navigate(url="https://mp.weixin.qq.com/s/xxxxx")

# Step 2: Get full content as accessible tree
browser_snapshot(full=True)
# Returns parsed structure with headings, paragraphs, lists

# Step 3: Convert to markdown and save locally
# Title is in heading level 1
# Author is typically in text after "原创" or first text node
# Content follows paragraph structure
```

**Key findings from 2026-04-11:**
- WeChat MP articles are heavily protected against direct HTTP fetch
- `web_extract` consistently fails with "Unauthorized: Invalid token"
- Browser automation with stealth features works reliably
- Content structure: heading[1] = title, following paragraphs = author/date, then body content

### Option 2: History File Parsing

When RSSHub sources are unavailable, extract articles from local history:

```python
from pathlib import Path
import json

def extract_from_history(target_date: str = None):
    '''Extract today's articles from history file when RSS fails'''
    from datetime import datetime
    
    target_date = target_date or datetime.now().strftime("%Y-%m-%d")
    history_file = Path.home() / "wechat_articles" / ".history.json"
    
    if not history_file.exists():
        return []
    
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    articles = []
    for link, info in history.items():
        if info.get('date') == target_date:
            articles.append({
                'source': info.get('source'),
                'title': info.get('title'),
                'link': link,
                'date': target_date
            })
    
    return articles

# Usage when RSSHub fails
articles = extract_from_history("2026-04-11")
for article in articles:
    print(f"{article['source']}|{article['link']}")
```

## Manual Article Archiving Workflow

When user provides a single WeChat article URL for immediate archiving:

1. **Try web_extract first** (fastest)
   - If succeeds: use extracted markdown content
   - If fails with 401/Unauthorized: proceed to browser

2. **Browser fallback** (when extract fails)
   ```python
   browser_navigate(url=article_url)
   snapshot = browser_snapshot(full=True)
   # Parse snapshot['snapshot'] for content tree
   # Extract: title (heading level 1), author (first text node), date (emphasis/em), body (paragraphs)
   ```

3. **Save locally**
   ```python
   output_path = f"~/wechat_articles/YYYY-MM-DD_{source}_{title}.md"
   # Write markdown with metadata header
   ```

4. **Upload to Feishu**
   ```python
   # Create document
   doc = create_doc(token, title=f"[{source}] {title}")
   doc_id = doc['data']['document']['document_id']
   
   # Add content block (CRITICAL: use integer block_type, not string)
   add_block(token, doc_id, block_id, content, block_type=2)  # 2 = text
   ```

## File Locations

- Main script: `~/wechat_collector.py`
- Feishu module: `~/feishu_docs_uploader.py`
- Output: `~/wechat_articles/YYYY-MM-DD/`
- History: `~/.wechat_articles/.history.json`
- Logs: `/var/log/wechat_collector.log` (when using cron)

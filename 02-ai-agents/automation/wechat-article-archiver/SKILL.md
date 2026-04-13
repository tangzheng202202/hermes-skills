---
name: wechat-article-archiver
title: WeChat Article to Feishu Archiver
description: Extract WeChat public account articles and archive them to Feishu documents with full formatting
version: 1.0.0
trigger: when asked to save, archive, or backup WeChat articles to Feishu
---

# WeChat Article to Feishu Archiver

## Goal
Extract content from WeChat public account articles and save them as formatted documents in Feishu (Lark).

## Prerequisites
- Feishu App credentials (APP_ID and APP_SECRET)
- Browser automation available (browser_navigate, browser_snapshot)
- Feishu API access for document creation

## Workflow

### 1. Extract Article Content

WeChat articles block standard web scraping, use browser automation:

```python
# Navigate to WeChat article URL
browser_navigate(url="https://mp.weixin.qq.com/s/xxxxx")

# Get full content
browser_snapshot(full=True)
```

**Content to extract:**
- Article title (heading level 1)
- Public account name (公众号)
- Author name
- Publication date
- Article body content
- Original URL

### 2. Convert to Markdown

Structure the extracted content:

```markdown
# {article_title}

**公众号**: {account_name}  
**作者**: {author}  
**发布时间**: {date}  
**原文链接**: {url}

---

{article_content}

---

*归档时间: {current_date}*  
*来源: {account_name}公众号*
```

### 3. Create Feishu Document

**Step 1: Get tenant access token**
```python
import requests

def get_tenant_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
    return resp.json()["tenant_access_token"]
```

**Step 2: Create document**
```python
def create_feishu_doc(token, title):
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, headers=headers, json={"title": title})
    return resp.json()['data']['document']['document_id']
```

**Step 3: Add content (block_type 2 = text)**
```python
def add_content_to_doc(token, doc_id, content):
    # Get first block ID
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    first_block_id = resp.json()['data']['items'][0]['block_id']
    
    # Add content as text block
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{first_block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "children": [{
            "block_type": 2,
            "text": {
                "elements": [{
                    "type": "text_run",
                    "text_run": {"content": content, "text_style": {}}
                }]
            }
        }]
    }
    resp = requests.post(url, headers=headers, json=data)
    return resp.json()
```

### 4. Complete Archive Flow

```python
import os
import requests
from datetime import datetime

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")

def archive_wechat_article(article_url, account_name):
    # 1. Extract via browser
    # browser_navigate, browser_snapshot...
    
    # 2. Format as markdown
    markdown_content = format_article(title, author, date, content, url)
    
    # 3. Save locally (backup)
    filename = f"{date}_{account_name}_{title[:20]}.md"
    with open(filename, "w") as f:
        f.write(markdown_content)
    
    # 4. Upload to Feishu
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    doc_id = create_feishu_doc(token, f"[{account_name}] {title}")
    add_content_to_doc(token, doc_id, markdown_content)
    
    return f"https://feishu.cn/docx/{doc_id}"
```

## Handling Multiple Articles

For batch processing:

```python
articles = [
    "https://mp.weixin.qq.com/s/xxxxx",
    "https://mp.weixin.qq.com/s/yyyyy",
]

for url in articles:
    try:
        result = archive_wechat_article(url, account_name)
        print(f"✅ Archived: {result}")
    except Exception as e:
        print(f"❌ Failed: {url} - {e}")
```

## Error Handling

**Common issues:**
1. **Browser extraction fails** - WeChat may block; try stealth mode or refresh
2. **Feishu API rate limits** - Add delays between requests
3. **Content too long** - Feishu has block size limits; may need to split
4. **Auth expiration** - Token expires in 2 hours; refresh if needed

## Output Format

Generated Feishu document includes:
- Properly formatted title and metadata
- Original article content preserved
- Source attribution
- Archive timestamp
- Link to original article

## Variations

- **Append to existing doc** instead of creating new
- **Organize by folder** by date or category
- **Extract images** and upload separately
- **Notify users** via Telegram/voice after archiving

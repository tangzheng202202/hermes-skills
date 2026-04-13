#!/usr/bin/env python3
"""Notion sync module for Knowledge Radar
Supports Chinese field names and multi_select categories.
Supports archiving by source type (multiple databases).
"""

import os
import json
from datetime import datetime
from pathlib import Path

try:
    from notion_client import Client
except ImportError:
    Client = None

# Legacy single database (fallback)
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Type-based archiving database IDs
# Each content type can be archived to its own database for better organization
NOTION_DB_TECH_AI = os.getenv("NOTION_DB_TECH_AI", "")   # Tech/AI content
NOTION_DB_FINANCE = os.getenv("NOTION_DB_FINANCE", "")   # Finance content  
NOTION_DB_ACADEMIC = os.getenv("NOTION_DB_ACADEMIC", "") # Academic content
NOTION_DB_SOCIAL = os.getenv("NOTION_DB_SOCIAL", "")     # Social media content
NOTION_DB_INDUSTRY = os.getenv("NOTION_DB_INDUSTRY", "") # Industry news

# Source to database TYPE mapping (decouples source from specific DB ID)
# This makes it easy to: (1) see routing logic, (2) change DBs without touching code
SOURCE_DB_MAP = {
    # Tech/AI
    "hackernews": "tech_ai",
    "github": "tech_ai",
    "huggingface": "tech_ai",
    "producthunt": "tech_ai",
    # Finance
    "wallstreetcn": "finance",
    "36kr": "finance",
    # Academic
    "arxiv": "academic",
    "hf_papers": "academic",
    # Social
    "weibo": "social",
    "v2ex": "social",
    "x_twitter": "social",
    "reddit": "social",
    # Industry
    "rss": "industry",
    "ai_newsletters": "industry",
}

# Type to database ID resolution (environment-based configuration)
TYPE_TO_DB_ID = {
    "tech_ai": NOTION_DB_TECH_AI,
    "finance": NOTION_DB_FINANCE,
    "academic": NOTION_DB_ACADEMIC,
    "social": NOTION_DB_SOCIAL,
    "industry": NOTION_DB_INDUSTRY,
}

# Source name mapping (English -> Chinese)
SOURCE_MAP = {
    "hackernews": "Hacker News",
    "github": "GitHub",
    "huggingface": "Hugging Face",
    "arxiv": "arXiv",
    "x_twitter": "X/Twitter",
    "wallstreetcn": "华尔街见闻",
    "36kr": "36氪",
    "weibo": "微博",
    "v2ex": "V2EX",
    "reddit": "Reddit",
    "rss": "RSS",
    "producthunt": "Product Hunt",
    "ai_newsletters": "AI Newsletter",
}

# Category mapping to multi_select options
CATEGORY_MAP = {
    "tech-ai": [{"name": "科技"}, {"name": "AI/ML"}],
    "finance": [{"name": "财经"}],
    "industry": [{"name": "科技"}, {"name": "行业"}],
    "academic": [{"name": "学术"}, {"name": "论文"}],
    "social": [{"name": "社交媒体"}, {"name": "热门话题"}],
}

# Source to category mapping (for determining category tags)
SOURCE_TO_CATEGORY = {
    "hackernews": "tech-ai",
    "github": "tech-ai",
    "huggingface": "tech-ai",
    "wallstreetcn": "finance",
    "36kr": "finance",
    "arxiv": "academic",
    "weibo": "social",
    "v2ex": "social",
    "x_twitter": "social",
    "reddit": "social",
    "rss": "industry",
    "producthunt": "industry",
    "ai_newsletters": "industry",
}


def init_notion():
    """Initialize Notion client"""
    if not Client:
        print("notion-client not installed. Run: pip install notion-client")
        return None
    if not NOTION_TOKEN:
        print("NOTION_TOKEN not set")
        return None
    return Client(auth=NOTION_TOKEN)


def get_database_id_for_source(source: str) -> str:
    """
    Get database ID for a source.
    Flow: source -> db_type -> db_id, with fallback to default database.
    """
    # 1. Get database type from source
    db_type = SOURCE_DB_MAP.get(source, "default")
    
    # 2. Get database ID from type (handles env var lookup)
    db_id = TYPE_TO_DB_ID.get(db_type, "")
    
    # 3. Fall back to default database if type-specific not configured
    return db_id if db_id else NOTION_DATABASE_ID


def get_database_id_for_item(item, category):
    """
    Determine which database to use based on item source.
    Maintains backward compatibility with old signature.
    """
    source = item.get("source", "unknown").lower()
    return get_database_id_for_source(source)


def get_category_for_item(item, fallback_category):
    """Determine category tags based on item source"""
    source = item.get("source", "unknown").lower()
    category = SOURCE_TO_CATEGORY.get(source, fallback_category)
    return CATEGORY_MAP.get(category, [{"name": "科技"}])


def discover_database_structure(database_id=None):
    """Discover existing Notion database structure"""
    notion = init_notion()
    if not notion:
        return None
    
    target_id = database_id or NOTION_DATABASE_ID
    if not target_id:
        return None
    
    try:
        # Search for pages in the database to see structure
        search_results = notion.search(query="", page_size=10)
        for page in search_results.get("results", []):
            parent = page.get("parent", {})
            if parent.get("type") == "database_id":
                db_id = parent.get("database_id", "").replace("-", "")
                check_id = target_id.replace("-", "")
                if db_id == check_id:
                    return page.get("properties", {})
        return None
    except Exception as e:
        print(f"Discovery error: {e}")
        return None


def sync_item(item, category, database_id=None):
    """
    Sync a single item to Notion database
    
    Args:
        item: The item to sync
        category: The category (tech-ai, finance, etc.)
        database_id: Optional specific database ID (auto-determined if not provided)
    """
    notion = init_notion()
    if not notion:
        return False
    
    # Determine target database
    target_db_id = database_id or get_database_id_for_item(item, category)
    if not target_db_id:
        print(f"No database configured for item from source '{item.get('source')}'")
        return False
    
    try:
        # Map source name to Chinese
        source = SOURCE_MAP.get(item.get("source", "unknown"), "其他")
        
        # Map category to multi_select (based on item source)
        categories = get_category_for_item(item, category)
        
        properties = {
            "名称": {"title": [{"text": {"content": item["title"][:100]}}]},
            "来源": {"select": {"name": source}},
            "分类": {"multi_select": categories},
            "链接": {"url": item.get("url", "")},
            "热度": {"number": item.get("heat", 0)},
            "状态": {"select": {"name": "🆕 新抓取"}},
            "创建时间": {"date": {"start": item.get("collected_at", datetime.now().isoformat())}},
        }
        
        # Add description for high-heat items
        if item.get("needs_deep_analysis"):
            desc = item.get("description", "")
            if desc:
                properties["摘要"] = {"rich_text": [{"text": {"content": desc[:500]}}]}
        
        notion.pages.create(
            parent={"database_id": target_db_id},
            properties=properties
        )
        return True
    except Exception as e:
        print(f"Notion sync error: {e}")
        return False


def sync_batch(items, category):
    """
    Sync multiple items to Notion with per-database statistics.
    
    Args:
        items: List of items to sync
        category: The category (tech-ai, finance, etc.)
    """
    from collections import defaultdict
    
    success = 0
    db_stats = defaultdict(lambda: {"success": 0, "total": 0})
    
    for item in items:
        source_key = item.get("source", "unknown")
        db_type = SOURCE_DB_MAP.get(source_key, "default")
        db_stats[db_type]["total"] += 1
        
        if sync_item(item, category):
            success += 1
            db_stats[db_type]["success"] += 1
    
    # Print summary with database IDs
    print(f"\n📊 Notion Sync Summary [{category}]: {success}/{len(items)} total")
    for db_type, stats in sorted(db_stats.items()):
        db_id = get_database_id_for_source(db_type)[:8] if db_type != "default" else (NOTION_DATABASE_ID[:8] if NOTION_DATABASE_ID else "N/A")
        print(f"  • {db_type:12} → {db_id}...: {stats['success']}/{stats['total']}")
    
    return success


def get_sync_config():
    """Get current sync configuration summary"""
    config = {
        "token_set": bool(NOTION_TOKEN),
        "default_db": NOTION_DATABASE_ID,
        "source_dbs": {
            "Tech/AI (hackernews, github, huggingface)": NOTION_DB_TECH_AI,
            "Finance (wallstreetcn, 36kr)": NOTION_DB_FINANCE,
            "Academic (arxiv)": NOTION_DB_ACADEMIC,
            "Social (weibo, v2ex, x_twitter, reddit)": NOTION_DB_SOCIAL,
            "Industry (rss, producthunt)": NOTION_DB_INDUSTRY,
        }
    }
    return config


if __name__ == "__main__":
    print("Notion sync module")
    print("=" * 50)
    
    config = get_sync_config()
    print(f"NOTION_TOKEN: {'✓ Set' if config['token_set'] else '✗ Not set'}")
    print(f"\nDatabase Configuration:")
    print(f"  Default DB: {config['default_db'] or 'Not set'}")
    print(f"\n  Source-specific DBs:")
    for name, db_id in config['source_dbs'].items():
        status = "✓" if db_id else "✗"
        display_id = db_id[:20] + "..." if db_id else "Not configured"
        print(f"    {status} {name}: {display_id}")
    
    print("\n" + "=" * 50)
    print("\nTo enable type-based archiving, set these environment variables:")
    print("  export NOTION_DB_TECH_AI='your-tech-db-id'")
    print("  export NOTION_DB_FINANCE='your-finance-db-id'")
    print("  export NOTION_DB_ACADEMIC='your-academic-db-id'")
    print("  export NOTION_DB_SOCIAL='your-social-db-id'")
    print("  export NOTION_DB_INDUSTRY='your-industry-db-id'")
    print("\nOr add them to ~/.knowledge-radar-env")

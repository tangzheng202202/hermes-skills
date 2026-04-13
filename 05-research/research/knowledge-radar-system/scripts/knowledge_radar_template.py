#!/usr/bin/env python3
"""Knowledge Radar - Multi-source information gathering system
Template implementation with HN, GitHub, and X sources.
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path

HEAT_THRESHOLD = 100
BASE_PATH = Path.home() / "knowledge"

CATEGORIES = {
    "tech-ai": {"schedule": ["08:00", "20:00"], "sources": ["hackernews", "github", "x_twitter"]},
    "finance": {"schedule": ["09:00", "21:00"], "sources": ["wallstreetcn", "36kr"]},
    "industry": {"schedule": ["10:00", "22:00"], "sources": ["rss"]},
    "academic": {"schedule": ["11:00", "23:00"], "sources": ["arxiv"]},
    "social": {"schedule": ["12:00", "00:00"], "sources": ["weibo", "v2ex"]}
}

def load_x_config():
    """Load X API config from ~/.config/x-cli/config.yaml"""
    config_path = Path.home() / ".config/x-cli/config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

def collect_hackernews(limit=10):
    """Fetch HN top stories"""
    import urllib.request
    try:
        req = urllib.request.Request(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers={"User-Agent": "KnowledgeRadar/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            top_ids = json.loads(response.read())[:limit]
        
        stories = []
        for story_id in top_ids:
            req = urllib.request.Request(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                headers={"User-Agent": "KnowledgeRadar/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                story = json.loads(response.read())
                stories.append({
                    "title": story.get("title", ""),
                    "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "score": story.get("score", 0),
                    "source": "hackernews",
                    "collected_at": datetime.now().isoformat()
                })
        return stories
    except Exception as e:
        print(f"HN error: {e}")
        return []

def collect_github_trending(limit=10):
    """Fetch GitHub trending repos"""
    import urllib.request
    try:
        req = urllib.request.Request(
            f"https://api.github.com/search/repositories?q=created:>2024-01-01&sort=stars&order=desc&per_page={limit}",
            headers={"User-Agent": "KnowledgeRadar/1.0", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            return [{
                "title": item["full_name"],
                "url": item["html_url"],
                "score": item["stargazers_count"],
                "source": "github",
                "description": item.get("description", ""),
                "collected_at": datetime.now().isoformat()
            } for item in data.get("items", [])]
    except Exception as e:
        print(f"GitHub error: {e}")
        return []

def collect_x_tweets(limit=10):
    """Fetch X tweets with quota management"""
    import urllib.request
    
    # Check quota
    quota_file = BASE_PATH / "x_api_quota.json"
    quota = {"used": 0, "month": datetime.now().month}
    if quota_file.exists():
        with open(quota_file) as f:
            quota = json.load(f)
            if quota.get("month") != datetime.now().month:
                quota = {"used": 0, "month": datetime.now().month}
    
    if quota["used"] >= 450:
        print(f"X API quota: {quota['used']}/500")
        return []
    
    config = load_x_config()
    bearer = config.get("bearer_token", "")
    if not bearer:
        return []
    
    try:
        req = urllib.request.Request(
            f"https://api.twitter.com/2/tweets/search/recent?query=AI OR tech&max_results={limit}&tweet.fields=public_metrics",
            headers={"Authorization": f"Bearer {bearer}"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            tweets = data.get("data", [])
            
            quota["used"] += limit
            with open(quota_file, "w") as f:
                json.dump(quota, f)
            
            return [{
                "title": tweet["text"][:100] + "..." if len(tweet["text"]) > 100 else tweet["text"],
                "url": f"https://twitter.com/i/web/status/{tweet['id']}",
                "score": tweet.get("public_metrics", {}).get("like_count", 0),
                "source": "x_twitter",
                "collected_at": datetime.now().isoformat()
            } for tweet in tweets]
    except Exception as e:
        print(f"X error: {e}")
        return []

def analyze_content(items):
    """Apply heat-based analysis"""
    for item in items:
        score = item.get("score", 0)
        item["heat"] = score
        item["needs_deep_analysis"] = score >= HEAT_THRESHOLD
    return items

def save_local(category, items):
    """Save to local storage"""
    raw_path = BASE_PATH / category / "raw"
    raw_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = raw_path / f"{timestamp}.json"
    
    with open(filepath, "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    return filepath

def run_category(category):
    """Run collection for a category"""
    print(f"\n[{datetime.now()}] Collecting: {category}")
    
    all_items = []
    
    if category == "tech-ai":
        all_items.extend(collect_hackernews())
        all_items.extend(collect_github_trending())
        all_items.extend(collect_x_tweets())
    
    if not all_items:
        print(f"No items for {category}")
        return
    
    analyzed = analyze_content(all_items)
    filepath = save_local(category, analyzed)
    
    high_heat = [i for i in analyzed if i.get("needs_deep_analysis")]
    print(f"Saved {len(analyzed)} items ({len(high_heat)} high-heat) to {filepath}")

if __name__ == "__main__":
    import sys
    category = sys.argv[1] if len(sys.argv) > 1 else "tech-ai"
    if category in CATEGORIES:
        run_category(category)
    else:
        print(f"Unknown: {category}")

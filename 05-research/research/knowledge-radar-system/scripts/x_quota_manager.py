#!/usr/bin/env python3
"""X API Quota Manager - tracks 500/month limit"""
import json
from datetime import datetime
from pathlib import Path

QUOTA_FILE = Path.home() / "knowledge/x_api_quota.json"
MONTHLY_LIMIT = 500
SAFETY_MARGIN = 450

def check_quota(cost=10):
    """Check if API call is within quota. Returns True if allowed."""
    quota = {"used": 0, "month": datetime.now().month}
    
    if QUOTA_FILE.exists():
        with open(QUOTA_FILE) as f:
            quota = json.load(f)
            if quota.get("month") != datetime.now().month:
                quota = {"used": 0, "month": datetime.now().month}
    
    if quota["used"] + cost > SAFETY_MARGIN:
        print(f"X API quota almost exhausted: {quota['used']}/{MONTHLY_LIMIT}")
        return False
    
    return True

def record_usage(cost=10):
    """Record API usage"""
    quota = {"used": 0, "month": datetime.now().month}
    
    if QUOTA_FILE.exists():
        with open(QUOTA_FILE) as f:
            quota = json.load(f)
            if quota.get("month") != datetime.now().month:
                quota = {"used": 0, "month": datetime.now().month}
    
    quota["used"] += cost
    QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUOTA_FILE, "w") as f:
        json.dump(quota, f)
    
    return quota["used"]

def get_quota_status():
    """Get current quota status"""
    if not QUOTA_FILE.exists():
        return {"used": 0, "limit": MONTHLY_LIMIT, "remaining": MONTHLY_LIMIT}
    
    with open(QUOTA_FILE) as f:
        quota = json.load(f)
        if quota.get("month") != datetime.now().month:
            return {"used": 0, "limit": MONTHLY_LIMIT, "remaining": MONTHLY_LIMIT}
        
        return {
            "used": quota["used"],
            "limit": MONTHLY_LIMIT,
            "remaining": MONTHLY_LIMIT - quota["used"]
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        status = get_quota_status()
        print(f"X API Quota: {status['used']}/{status['limit']} used, {status['remaining']} remaining")

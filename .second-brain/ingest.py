#!/usr/bin/env python3
"""
摄取模块 - Ingest
负责把任意格式的内容收集到知识库

支持：
- 微信文章
- 网页文章
- 视频（需要字幕）
- PDF/EPUB
- 图片/OCR
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

SECOND_BRAIN_HOME = Path(os.getenv("SECOND_BRAIN_HOME", "~/second-brain")).expanduser()
INGEST_DIR = SECOND_BRAIN_HOME / "00-ingest"
QUEUE_FILE = SECOND_BRAIN_HOME / ".queue.json"


def init_directories():
    """初始化目录结构"""
    dirs = [
        SECOND_BRAIN_HOME,
        INGEST_DIR,
        SECOND_BRAIN_HOME / "01-raw",
        SECOND_BRAIN_HOME / "02-processed",
        SECOND_BRAIN_HOME / "03-output",
        SECOND_BRAIN_HOME / ".meta"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def add_to_queue(url: str, source_type: str, metadata: dict = None):
    """
6dfb加到处理队列"""
    queue = []
    if QUEUE_FILE.exists():
        queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    
    queue.append({
        "url": url,
        "type": source_type,
        "added_at": datetime.now().isoformat(),
        "metadata": metadata or {},
        "status": "pending"
    })
    
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ 已添加到队列: {url}")


def detect_source_type(url: str) -> str:
    """检测来源类型"""
    if "mp.weixin.qq.com" in url:
        return "wechat"
    elif "douyin.com" in url or "tiktok.com" in url:
        return "video"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif url.endswith(".pdf"):
        return "pdf"
    elif url.endswith(".epub"):
        return "epub"
    else:
        return "webpage"


def ingest_wechat(url: str):
    """摄取微信文章"""
    print(f"📱 微信文章: {url}")
    # 调用已有的微信文章归档skill
    add_to_queue(url, "wechat")


def ingest_webpage(url: str):
    """摄取网页"""
    print(f"🌐 网页: {url}")
    add_to_queue(url, "webpage")


def ingest_video(url: str):
    """摄取视频"""
    print(f"📹 视频: {url}")
    add_to_queue(url, "video")


def main():
    parser = argparse.ArgumentParser(description="Second Brain - 摄取模块")
    parser.add_argument("url", help="要摄取的URL")
    parser.add_argument("-t", "--type", help="指定类型（auto/wechat/webpage/video/pdf）", default="auto")
    parser.add_argument("--tags", help="标签（逗号分隔）", default="")
    
    args = parser.parse_args()
    
    init_directories()
    
    # 检测类型
    source_type = args.type
    if source_type == "auto":
        source_type = detect_source_type(args.url)
    
    print(f"\n📥 摄取: {args.url}")
    print(f"   类型: {source_type}")
    
    metadata = {"tags": args.tags.split(",") if args.tags else []}
    
    # 路由到对应处理器
    if source_type == "wechat":
        ingest_wechat(args.url)
    elif source_type == "video":
        ingest_video(args.url)
    elif source_type == "youtube":
        ingest_video(args.url)
    else:
        ingest_webpage(args.url)
    
    print(f"\n📊 队列状态：")
    if QUEUE_FILE.exists():
        queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        pending = [q for q in queue if q["status"] == "pending"]
        print(f"   待处理: {len(pending)} 项")


if __name__ == "__main__":
    main()

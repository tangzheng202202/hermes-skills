#!/usr/bin/env python3
"""
输出模块 - Output
负责将消化后的知识输出成各种格式：
1. 知识卡片（HTML/Markdown）
2. 文章汇编
3. PDF报告
4. 视频脚本
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

SECOND_BRAIN_HOME = Path(os.getenv("SECOND_BRAIN_HOME", "~/second-brain")).expanduser()
OUTPUT_DIR = SECOND_BRAIN_HOME / "03-output"
QUEUE_FILE = SECOND_BRAIN_HOME / ".queue.json"
KNOWLEDGE_GRAPH = SECOND_BRAIN_HOME / ".meta" / "knowledge_graph.json"


def load_processed_items() -> List[Dict]:
    """加载已处理的条目"""
    if not QUEUE_FILE.exists():
        return []
    queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    return [q for q in queue if q.get("status") == "processed"]


def load_knowledge_graph() -> Dict:
    """加载知识图谱"""
    if not KNOWLEDGE_GRAPH.exists():
        return {"nodes": [], "edges": []}
    return json.loads(KNOWLEDGE_GRAPH.read_text(encoding="utf-8"))


def generate_knowledge_card(item: Dict, output_format: str = "markdown") -> str:
    """生成知识卡片"""
    if output_format == "markdown":
        card = f"""# {item.get('title', 'Untitled')}

## 摘要
{item.get('summary', '暂无摘要')}

## 标签
{', '.join(item.get('tags', []))}

## 核心概念
{chr(10).join(['- ' + c for c in item.get('concepts', [])])}

## 来源
- URL: {item.get('url', '')}
- 类型: {item.get('type', 'unknown')}
- 处理时间: {item.get('processed_at', '')}

---
*自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
        return card
    
    elif output_format == "html":
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{item.get('title', 'Knowledge Card')}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        .card {{ border: 1px solid #e0e0e0; border-radius: 8px; padding: 24px; }}
        .tag {{ display: inline-block; background: #f0f0f0; padding: 4px 12px; border-radius: 12px; margin: 4px; font-size: 14px; }}
        .concept {{ color: #0066cc; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>{item.get('title', 'Untitled')}</h1>
        <h3>摘要</h3>
        <p>{item.get('summary', '暂无摘要')}</p>
        
        <h3>标签</h3>
        <div>{''.join([f'<span class="tag">{t}</span>' for t in item.get('tags', [])])}</div>
        
        <h3>核心概念</h3>
        <ul>{''.join([f'<li class="concept">{c}</li>' for c in item.get('concepts', [])])}</ul>
        
        <p><small>来源: <a href="{item.get('url', '')}">{item.get('url', '')[:60]}...</a></small></p>
    </div>
</body>
</html>"""


def generate_article(topic: str = None, tags: List[str] = None, days: int = 30) -> str:
    """生成主题文章"""
    items = load_processed_items()
    
    # 过滤
    cutoff = datetime.now() - __import__('datetime').timedelta(days=days)
    filtered = [
        item for item in items
        if datetime.fromisoformat(item.get('processed_at', '2000-01-01')) > cutoff
    ]
    
    if tags:
        filtered = [
            item for item in filtered
            if any(tag in item.get('tags', []) for tag in tags)
        ]
    
    if not filtered:
        return "没有找到匹配的内容"
    
    # 生成文章
    title = topic or f"{tags[0] if tags else 'AI'}知识汇编"
    
    article = f"""# {title}

> 自动生成于 {datetime.now().strftime("%Y年%m月%d日")}
> 共汇集 {len(filtered)} 篇文章

## 目录

"""
    
    for i, item in enumerate(filtered, 1):
        article += f"{i}. [{item.get('title', 'Untitled')}](#{i})\n"
    
    article += "\n---\n\n"
    
    for i, item in enumerate(filtered, 1):
        article += f"## {i}. {item.get('title', 'Untitled')}\n\n"
        article += f"来源: [{item.get('url', '')}]({item.get('url', '')})\n\n"
        article += f"{item.get('summary', '')}\n\n"
        article += f"**标签**: {', '.join(item.get('tags', []))}\n\n"
        article += f"**关键词**: {', '.join(item.get('concepts', [])[:5])}\n\n---\n\n"
    
    return article


def generate_report(report_type: str = "weekly") -> str:
    """生成报告"""
    items = load_processed_items()
    graph = load_knowledge_graph()
    
    if report_type == "weekly":
        days = 7
    elif report_type == "monthly":
        days = 30
    else:
        days = 7
    
    cutoff = datetime.now() - __import__('datetime').timedelta(days=days)
    recent_items = [
        item for item in items
        if datetime.fromisoformat(item.get('processed_at', '2000-01-01')) > cutoff
    ]
    
    # 统计
    tag_counts = {}
    concept_counts = {}
    
    for item in recent_items:
        for tag in item.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        for concept in item.get('concepts', []):
            concept_counts[concept] = concept_counts.get(concept, 0) + 1
    
    report = f"""# Second Brain {report_type.capitalize()} Report

## 概览

- 期间: 最近{days}天
- 摄取内容: {len(recent_items)} 篇
- 知识图谱节点: {len(graph.get('nodes', []))}
- 知识图谱关联: {len(graph.get('edges', []))}

## 热门标签

| 标签 | 数量 |
|------|------|
"""
    
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        report += f"| {tag} | {count} |\n"
    
    report += """
## 核心概念

"""
    
    for concept, count in sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        report += f"- **{concept}**: 出现 {count} 次\n"
    
    report += """
## 新增内容

"""
    
    for item in recent_items[:5]:
        report += f"- [{item.get('title', 'Untitled')}]({item.get('url', '')})\n"
    
    return report


def output_cards(format: str = "markdown"):
    """输出知识卡片"""
    items = load_processed_items()
    
    output_path = OUTPUT_DIR / f"cards_{datetime.now().strftime('%Y%m%d')}"
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📄 生成知识卡片 ({format})...")
    
    for item in items:
        card = generate_knowledge_card(item, format)
        filename = f"{hash(item['url']) % 10000:04d}.{format}"
        
        filepath = output_path / filename
        filepath.write_text(card, encoding="utf-8")
    
    print(f"   ✅ 已生成 {len(items)} 个卡片到: {output_path}")


def output_article(topic: str = None, tags: str = None):
    """输出主题文章"""
    tag_list = tags.split(",") if tags else None
    
    article = generate_article(topic=topic, tags=tag_list)
    
    filename = f"article_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    filepath = OUTPUT_DIR / filename
    filepath.write_text(article, encoding="utf-8")
    
    print(f"\n📝 主题文章已生成: {filepath}")


def output_report(report_type: str = "weekly"):
    """输出报告"""
    report = generate_report(report_type)
    
    filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d')}.md"
    filepath = OUTPUT_DIR / filename
    filepath.write_text(report, encoding="utf-8")
    
    print(f"\n📊 {report_type.capitalize()} 报告已生成: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Second Brain - 输出模块")
    parser.add_argument("--cards", action="store_true", help="生成知识卡片")
    parser.add_argument("--format", default="markdown", help="输出格式 (markdown/html)")
    parser.add_argument("--article", action="store_true", help="生成主题文章")
    parser.add_argument("--topic", help="文章主题")
    parser.add_argument("--tags", help="过滤标签（逗号分隔）")
    parser.add_argument("--report", choices=["weekly", "monthly"], help="生成报告")
    
    args = parser.parse_args()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.cards:
        output_cards(format=args.format)
    elif args.article:
        output_article(topic=args.topic, tags=args.tags)
    elif args.report:
        output_report(args.report)
    else:
        # 默认输出报告
        output_report("weekly")


if __name__ == "__main__":
    main()

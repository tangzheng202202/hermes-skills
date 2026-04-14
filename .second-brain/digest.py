#!/usr/bin/env python3
"""
消化模块 - Digest
负责自动处理队列中的内容，进行：
1. 标签自动生成
2. 摘要生成
3. 建立知识关联
4. 更新知识图谱
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

SECOND_BRAIN_HOME = Path(os.getenv("SECOND_BRAIN_HOME", "~/second-brain")).expanduser()
QUEUE_FILE = SECOND_BRAIN_HOME / ".queue.json"
PROCESSED_DIR = SECOND_BRAIN_HOME / "02-processed"
KNOWLEDGE_GRAPH = SECOND_BRAIN_HOME / ".meta" / "knowledge_graph.json"


def load_queue() -> list:
    """加载队列"""
    if not QUEUE_FILE.exists():
        return []
    return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))


def save_queue(queue: list):
    """保存队列"""
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")


def auto_tag(content: str) -> list:
    """
    自动标签生成（简化版）
    完整版需要调用AI进行实体提取
    """
    # 关键词匹配
    keywords = {
        "AI": ["AI", "人工智能", "大模型", "LLM", "机器学习"],
        "编程": ["代码", "编程", "开发", "程序员", "Python", "JavaScript"],
        "产品": ["产品", "设计", "用户体验", "UX", "UI"],
        "效率": ["效率", "自动化", "工作流", "时间管理"],
        "创业": ["创业", "商业", "商业模式", "增长", "变现"],
    }
    
    tags = []
    content_lower = content.lower()
    
    for tag, words in keywords.items():
        if any(word.lower() in content_lower for word in words):
            tags.append(tag)
    
    return tags


def generate_summary(content: str, max_length: int = 500) -> str:
    """
    生成摘要（简化版）
    完整版需要调用AI进行摘要生成
    """
    lines = content.split("\n")
    summary_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and len(line) > 20:
            summary_lines.append(line)
            if len("\n".join(summary_lines)) > max_length:
                break
    
    summary = "\n".join(summary_lines)[:max_length]
    if len(summary) == max_length:
        summary += "..."
    
    return summary


def extract_key_concepts(content: str) -> list:
    """提取核心概念"""
    # 简化版：提取被引号包围的内容或全大写词汇
    import re
    concepts = []
    
    # 引号内容
    quoted = re.findall(r'["""]([^"""]+)["""]', content)
    concepts.extend(quoted)
    
    # 英文术语（首字母大写的连续词）
    terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
    concepts.extend([t for t in terms if len(t) > 3])
    
    return list(set(concepts))[:10]


def update_knowledge_graph(item: dict, tags: list, concepts: list):
    """更新知识图谱"""
    graph = {"nodes": [], "edges": []}
    
    if KNOWLEDGE_GRAPH.exists():
        graph = json.loads(KNOWLEDGE_GRAPH.read_text(encoding="utf-8"))
    
    # 添加节点
    node_id = f"{item['type']}_{hash(item['url']) % 10000}"
    graph["nodes"].append({
        "id": node_id,
        "type": item["type"],
        "url": item["url"],
        "title": item.get("title", "Untitled"),
        "tags": tags,
        "concepts": concepts,
        "processed_at": datetime.now().isoformat()
    })
    
    # 建立关联（相同标签或概念）
    for existing_node in graph["nodes"]:
        if existing_node["id"] == node_id:
            continue
        
        # 检查标签重叠
        common_tags = set(tags) & set(existing_node.get("tags", []))
        if common_tags:
            graph["edges"].append({
                "source": node_id,
                "target": existing_node["id"],
                "type": "tag",
                "weight": len(common_tags)
            })
        
        # 检查概念重叠
        common_concepts = set(concepts) & set(existing_node.get("concepts", []))
        if common_concepts:
            graph["edges"].append({
                "source": node_id,
                "target": existing_node["id"],
                "type": "concept",
                "weight": len(common_concepts)
            })
    
    # 去重边
    seen = set()
    unique_edges = []
    for edge in graph["edges"]:
        key = (edge["source"], edge["target"], edge["type"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(edge)
    graph["edges"] = unique_edges
    
    KNOWLEDGE_GRAPH.parent.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")


def process_item(item: dict) -> dict:
    """处理单个项目"""
    print(f"\n  处理: {item['url'][:60]}...")
    
    # 这里需要调用AI进行深度处理
    # 简化版：模拟处理结果
    
    # 1. 获取内容（实际需要web提取）
    content = f"Sample content from {item['url']}"
    
    # 2. 自动标签
    tags = auto_tag(content)
    print(f"    标签: {', '.join(tags)}")
    
    # 3. 生成摘要
    summary = generate_summary(content)
    print(f"    摘要: {summary[:80]}...")
    
    # 4. 提取概念
    concepts = extract_key_concepts(content)
    print(f"    概念: {', '.join(concepts[:5])}")
    
    # 5. 更新知识图谱
    update_knowledge_graph(item, tags, concepts)
    
    return {
        **item,
        "status": "processed",
        "processed_at": datetime.now().isoformat(),
        "tags": tags,
        "summary": summary,
        "concepts": concepts
    }


def digest_all():
    """消化所有待处理内容"""
    queue = load_queue()
    pending = [q for q in queue if q["status"] == "pending"]
    
    if not pending:
        print("✅ 队列为空，无需处理")
        return
    
    print(f"\n🔄 开始消化 {len(pending)} 个待处理项目...")
    
    processed_count = 0
    for item in pending:
        try:
            processed = process_item(item)
            
            # 更新队列状态
            for q in queue:
                if q["url"] == item["url"] and q["status"] == "pending":
                    q.update(processed)
            
            processed_count += 1
            
        except Exception as e:
            print(f"    ❌ 处理失败: {e}")
            item["status"] = "error"
            item["error"] = str(e)
    
    save_queue(queue)
    
    print(f"\n✅ 完成: {processed_count}/{len(pending)} 个项目已消化")


def digest_recent(days: int = 7):
    """消化最近的内容"""
    queue = load_queue()
    cutoff = datetime.now() - timedelta(days=days)
    
    recent_pending = [
        q for q in queue 
        if q["status"] == "pending" 
        and datetime.fromisoformat(q["added_at"]) > cutoff
    ]
    
    if not recent_pending:
        print(f"✅ 最近{days}天内无待处理内容")
        return
    
    print(f"\n🔄 处理最近{days}天的 {len(recent_pending)} 个项目...")
    
    # 复用消化逻辑
    for item in recent_pending:
        process_item(item)
        for q in queue:
            if q["url"] == item["url"]:
                q["status"] = "processed"
    
    save_queue(queue)


def main():
    parser = argparse.ArgumentParser(description="Second Brain - 消化模块")
    parser.add_argument("--all", action="store_true", help="处理所有待处理内容")
    parser.add_argument("--recent", type=int, metavar="DAYS", help="处理最近N天的内容")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    
    args = parser.parse_args()
    
    if args.stats:
        queue = load_queue()
        total = len(queue)
        pending = len([q for q in queue if q["status"] == "pending"])
        processed = len([q for q in queue if q["status"] == "processed"])
        
        print("\n📊 消化统计")
        print(f"  总计: {total}")
        print(f"  待处理: {pending}")
        print(f"  已处理: {processed}")
        
        if KNOWLEDGE_GRAPH.exists():
            graph = json.loads(KNOWLEDGE_GRAPH.read_text(encoding="utf-8"))
            print(f"  知识图谱节点: {len(graph.get('nodes', []))}")
            print(f"  知识图谱关联: {len(graph.get('edges', []))}")
    
    elif args.all:
        digest_all()
    
    elif args.recent:
        digest_recent(args.recent)
    
    else:
        # 默认处理所有
        digest_all()


if __name__ == "__main__":
    main()

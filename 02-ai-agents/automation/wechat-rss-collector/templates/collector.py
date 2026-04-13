#!/usr/bin/env python3
"""
微信公众号文章自动收集脚本
- 从RSSHub抓取4个公众号的最新文章
- 保存到 ~/wechat_articles/YYYY-MM-DD/
- 上传到飞书知识库「AI」
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib import request, error

# 导入飞书上传模块
from feishu_docs_uploader import FeishuDocsUploader

# ============ 配置 ============
RSS_MIRROR = "https://rsshub.pseudoyu.com"

PUBLIC_ACCOUNTS = [
    {"name": "Draco正在VibeCoding", "encoded": "Draco%E6%AD%A3%E5%9C%A8VibeCoding"},
    {"name": "AI寒武纪", "encoded": "AI%E5%AF%92%E6%AD%A6%E7%BA%AA"},
    {"name": "左岸AI", "encoded": "%E5%B7%A6%E5%B2%B8AI"},
    {"name": "老金带你玩AI", "encoded": "%E8%80%81%E9%87%91%E5%B8%A6%E4%BD%A0%E7%8E%A9AI"}
]

# 本地存储路径
BASE_DIR = Path.home() / "wechat_articles"
HISTORY_FILE = BASE_DIR / ".history.json"

class WeChatCollector:
    def __init__(self, target_date: str = None):
        self.history = self.load_history()
        self.today = target_date or datetime.now().strftime("%Y-%m-%d")
        self.output_dir = BASE_DIR / self.today
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_history(self) -> dict:
        """加载抓取历史"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_history(self):
        """保存抓取历史"""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def fetch_rss(self, account: dict) -> list:
        """抓取单个公众号的RSS"""
        url = f"{RSS_MIRROR}/wechat/sogou/{account['encoded']}"
        articles = []
        
        try:
            req = request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            with request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                # 解析XML
                root = ET.fromstring(content)
                channel = root.find('channel')
                if channel is None:
                    return articles
                
                # 提取文章
                for item in channel.findall('item'):
                    article = {
                        'title': self.get_text(item, 'title'),
                        'link': self.get_text(item, 'link'),
                        'pub_date': self.get_text(item, 'pubDate'),
                        'author': self.get_text(item, 'author') or account['name'],
                        'description': self.get_text(item, 'description'),
                        'source': account['name']
                    }
                    articles.append(article)
                    
        except Exception as e:
            print(f"   ❌ 抓取失败: {e}")
            
        return articles
    
    def get_text(self, element, tag: str) -> str:
        """安全获取XML文本"""
        elem = element.find(tag)
        if elem is not None and elem.text:
            return elem.text.strip()
        return ""
    
    def is_today(self, pub_date: str) -> bool:
        """判断文章是否为今天发布"""
        if not pub_date:
            return False
        try:
            # 格式: Thu, 09 Apr 2026 21:06:12 GMT
            pub_dt = datetime.strptime(pub_date.strip(), "%a, %d %b %Y %H:%M:%S %Z")
            return pub_dt.strftime("%Y-%m-%d") == self.today
        except:
            # 解析失败时尝试宽松匹配
            try:
                pub_dt = datetime.strptime(pub_date[:16], "%a, %d %b %Y")
                return pub_dt.strftime("%Y-%m-%d") == self.today
            except:
                return False
    
    def clean_html(self, html: str) -> str:
        """简单清理HTML标签"""
        # 移除script和style
        html = re.sub(r'<(script|style)[^>]*>[^<]*</\1>', '', html, flags=re.I|re.S)
        # 转换常见标签
        html = re.sub(r'<br\s*/?>', '\n', html, flags=re.I)
        html = re.sub(r'<p[^>]*>', '\n', html, flags=re.I)
        html = re.sub(r'</p>', '', html, flags=re.I)
        # 移除其他标签
        html = re.sub(r'<[^>]+>', '', html)
        # 解码HTML实体
        html = html.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        html = html.replace('&quot;', '"').replace('&nbsp;', ' ')
        return html.strip()
    
    def to_markdown(self, article: dict) -> str:
        """生成Markdown格式"""
        description = self.clean_html(article['description'])
        md = f"""# {article['title']}

**来源**: {article['source']}  
**作者**: {article['author']}  
**发布时间**: {article['pub_date']}  
**原文链接**: {article['link']}

---

{description}

---
*自动收集于 {self.today}*
"""
        return md
    
    def collect_from_history(self) -> list:
        """当RSS抓取失败时，从历史记录中提取今日文章"""
        articles = []
        for link, info in self.history.items():
            if info.get('date') == self.today:
                articles.append({
                    'title': info.get('title', '无标题'),
                    'link': link,
                    'pub_date': self.today,
                    'source': info.get('source', '未知')
                })
        return articles
    
    def collect_all(self, all_days: bool = False, use_fallback: bool = True) -> dict:
        """收集所有公众号文章"""
        results = {
            'date': self.today,
            'total': 0,
            'articles': [],
            'by_source': {}
        }
        
        rss_failed = False
        
        for account in PUBLIC_ACCOUNTS:
            print(f"\n📱 {account['name']}")
            articles = self.fetch_rss(account)
            
            if not articles:
                rss_failed = True
            
            if all_days:
                # 测试模式：抓取所有文章
                target_articles = articles[:3]  # 每个号取最近3篇
                print(f"   测试模式: 抓取最近 {len(target_articles)} 篇")
            else:
                # 正常模式：只抓今天
                target_articles = [a for a in articles if self.is_today(a['pub_date'])]
                print(f"   总文章: {len(articles)} | 今日更新: {len(target_articles)}")
            
            # 去重并保存
            new_count = 0
            for article in target_articles:
                if article['link'] not in self.history:
                    self.history[article['link']] = {
                        'title': article['title'],
                        'date': self.today,
                        'source': article['source']
                    }
                    results['articles'].append(article)
                    results['by_source'][account['name']] = results['by_source'].get(account['name'], 0) + 1
                    new_count += 1
                    
                    # 保存到文件
                    safe_title = re.sub(r'[\\/:*?"<>|]', '_', article['title'])[:40]
                    filename = f"{article['source']}_{safe_title}.md"
                    filepath = self.output_dir / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(self.to_markdown(article))
            
            if new_count > 0:
                print(f"   ✅ 新增 {new_count} 篇已保存")
        
        # Fallback: if RSS failed and no articles found, try history
        if rss_failed and use_fallback and results['total'] == 0:
            print(f"\n⚠️ RSS抓取失败，尝试从历史记录提取...")
            history_articles = self.collect_from_history()
            if history_articles:
                print(f"   从历史记录找到 {len(history_articles)} 篇文章")
                for article in history_articles:
                    results['articles'].append(article)
                    results['by_source'][article['source']] = results['by_source'].get(article['source'], 0) + 1
            
        results['total'] = len(results['articles'])
        self.save_history()
        return results
def main():
    import argparse
    parser = argparse.ArgumentParser(description='微信公众号文章收集器')
    parser.add_argument('--all', action='store_true', help='测试模式：抓取所有文章')
    parser.add_argument('--no-feishu', action='store_true', help='不上传到飞书')
    parser.add_argument('--date', type=str, help='指定日期(YYYY-MM-DD)，抓取该日期文章')
    args = parser.parse_args()
    
    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("微信公众号文章收集器")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标日期: {target_date}")
    print(f"保存路径: {BASE_DIR}")
    print(f"飞书知识库: AI (Space: 7627160660329139165)")
    if args.all:
        print("模式: 测试模式（抓取最近3篇）")
    print("=" * 60)
    
    # 1. 收集文章
    collector = WeChatCollector(target_date=target_date)
    results = collector.collect_all(all_days=args.all)
    
    # 2. 上传到飞书（如果配置了且未禁用）
    feishu_result = None
    if not args.no_feishu and results['total'] > 0:
        print("\n" + "-" * 60)
        uploader = FeishuDocsUploader()
        feishu_result = uploader.upload_articles(
            date_str=results['date'],
            articles=results['articles'],
            local_dir=collector.output_dir
        )
        print("-" * 60)
    
    # 3. 输出报告
    print("\n" + "=" * 60)
    print(f"📦 收集完成!")
    print(f"日期: {results['date']}")
    print(f"文章总数: {results['total']} 篇")
    
    if results['by_source']:
        print("\n来源分布:")
        for source, count in sorted(results['by_source'].items()):
            print(f"  • {source}: {count} 篇")
    
    if results['total'] > 0:
        print(f"\n本地保存: {collector.output_dir}")
        
        if feishu_result:
            if feishu_result.get('success'):
                print(f"飞书上传: ✅ 成功 {feishu_result['uploaded']}/{feishu_result['total']} 篇")
                if feishu_result.get('failed', 0) > 0:
                    print(f"         ⚠️ 失败 {feishu_result['failed']} 篇")
            else:
                print(f"飞书上传: ❌ 失败 - {feishu_result.get('error', '未知错误')}")
        
        print("\n文章列表:")
        for article in results['articles'][:10]:
            print(f"  - [{article['source']}] {article['title'][:50]}...")
        if len(results['articles']) > 10:
            print(f"  ... 还有 {len(results['articles'])-10} 篇")
    
    # 4. 生成通知消息
    if feishu_result and feishu_result.get('success'):
        notify_msg = f"""📦 今日公众号更新已收集完毕

日期: {results['date']}
文章数: {results['total']} 篇
状态: 已写入知识库「AI/{results['date']}/」

详细来源:
"""
        for source, count in sorted(results['by_source'].items()):
            notify_msg += f"  • {source}: {count} 篇\n"
        
        notify_msg += "\n请宁瑶开始研报工作。"
        print("\n" + "=" * 60)
        print("通知消息:")
        print(notify_msg)
        # TODO: 发送给宁瑶
    
    print("=" * 60)
    
    return results['total']

if __name__ == "__main__":
    count = main()
    sys.exit(0)

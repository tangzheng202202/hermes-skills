#!/usr/bin/env python3
"""
飞书云文档上传模块（替代Wiki API）
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from urllib import request, error

class FeishuDocsUploader:
    def __init__(self):
        self.app_id = os.getenv('FEISHU_APP_ID', '')
        self.app_secret = os.getenv('FEISHU_APP_SECRET', '')
        self.token = None
        
    def get_access_token(self) -> bool:
        """获取飞书tenant_access_token"""
        if not self.app_id or not self.app_secret:
            print("❌ 未配置FEISHU_APP_ID或FEISHU_APP_SECRET")
            return False
            
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        data = json.dumps({
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }).encode('utf-8')
        
        try:
            req = request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                if result.get('code') == 0:
                    self.token = result['tenant_access_token']
                    return True
                else:
                    print(f"❌ 获取token失败: {result.get('msg', '未知错误')}")
                    return False
        except Exception as e:
            print(f"❌ 请求token失败: {e}")
            return False
    
    def create_document(self, title: str, content: str, folder_token: str = None) -> dict:
        """
        创建飞书文档
        """
        if not self.token:
            print("❌ 未获取token")
            return None
        
        # 1. 先创建空文档
        url = "https://open.feishu.cn/open-apis/docx/v1/documents"
        data = {"title": title}
        if folder_token:
            data["folder_token"] = folder_token
        
        try:
            req = request.Request(
                url,
                data=json.dumps(data).encode(),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                },
                method='POST'
            )
            with request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode())
                if result.get('code') == 0:
                    doc_data = result.get('data', {}).get('document', {})
                    document_id = doc_data.get('document_id')
                    print(f"   ✅ 创建文档: {title}")
                    print(f"   文档ID: {document_id}")
                    
                    # 生成文档链接
                    doc_url = f"https://feishu.cn/docx/{document_id}"
                    doc_data['url'] = doc_url
                    print(f"   文档链接: {doc_url}")
                    
                    # 注意：飞书Docx API写入内容较复杂，先创建空文档
                    # 内容可以通过其他方式补充，或在后续版本中完善
                    return doc_data
                else:
                    print(f"   ❌ 创建文档失败: {result.get('msg', '未知错误')}")
                    return None
        except error.HTTPError as e:
            error_body = e.read().decode()
            print(f"   ❌ HTTP {e.code}: {error_body[:200]}")
            return None
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            return None
    
    def write_document_content(self, document_id: str, content: str) -> bool:
        """
        向文档写入内容
        使用飞书Docx Block API添加子块
        
        关键学习点 (2026-04-11):
        - block_type 必须是整数: 2表示text, 3表示heading1等
        - element type 必须是 "text_run" (带下划线)
        - 使用 POST /blocks/{id}/children 添加子块
        """
        # 1. 获取文档块结构，找到根块ID (page block)
        blocks_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks"
        try:
            req = request.Request(blocks_url, headers={'Authorization': f'Bearer {self.token}'})
            with request.urlopen(req, timeout=10) as response:
                blocks_result = json.loads(response.read().decode())
                if blocks_result.get('code') == 0:
                    items = blocks_result.get('data', {}).get('items', [])
                    if items:
                        root_block_id = items[0].get('block_id')
                        print(f"   根块ID: {root_block_id}")
                    else:
                        print("   未找到根块")
                        return False
                else:
                    print(f"   获取块失败: {blocks_result.get('msg')}")
                    return False
        except Exception as e:
            print(f"   获取块失败: {e}")
            return False
        
        # 2. 使用POST添加子块 (不是PATCH)
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{root_block_id}/children"
        print(f"   写入URL: {url[:70]}...")
        
        # 正确的block结构: block_type用整数, text_run格式
        batch_data = {
            "children": [
                {
                    "block_type": 2,  # 2 = text block
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
        print(f"   请求体: {json.dumps(batch_data, ensure_ascii=False)[:100]}...")
        
        try:
            req = request.Request(
                url,
                data=json.dumps(batch_data).encode(),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                },
                method='POST'
            )
            with request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode())
                print(f"   写入结果: {result.get('code')} - {result.get('msg', 'success')}")
                if result.get('code') == 0:
                    return True
                else:
                    print(f"   ⚠️ 写入失败: {result.get('msg')}")
                    return False
        except error.HTTPError as e:
            error_body = e.read().decode()
            print(f"   ⚠️ HTTP {e.code}: {error_body[:200]}")
            return False
        except Exception as e:
            print(f"   ⚠️ 写入异常: {e}")
            return False
    
    def upload_articles(self, date_str: str, articles: list, local_dir: Path) -> dict:
        """
        批量上传文章到飞书文档
        """
        if not self.token and not self.get_access_token():
            return {'success': False, 'error': '认证失败'}
        
        print(f"\n📝 开始上传 {len(articles)} 篇文章到飞书文档...")
        
        results = {
            'success': True,
            'total': len(articles),
            'uploaded': 0,
            'failed': 0,
            'items': []
        }
        
        for article in articles:
            title = article['title']
            source = article['source']
            
            print(f"\n   📝 上传: {title[:40]}...")
            
            # 读取本地文件
            safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:40]
            filename = f"{source}_{safe_title}.md"
            filepath = local_dir / filename
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"   ❌ 读取文件失败: {e}")
                results['failed'] += 1
                continue
            
            # 创建文档
            doc_title = f"[{source}] {title[:50]}"
            doc_data = self.create_document(doc_title, content)
            
            if doc_data:
                results['uploaded'] += 1
                results['items'].append({
                    'title': title,
                    'status': 'success',
                    'document_id': doc_data.get('document_id'),
                    'url': doc_data.get('url', '')
                })
            else:
                results['failed'] += 1
                results['items'].append({
                    'title': title,
                    'status': 'failed'
                })
        
        return results

def test_docs_api():
    """测试Docs API"""
    print("=" * 60)
    print("飞书Docs API连接测试")
    print("=" * 60)
    
    uploader = FeishuDocsUploader()
    
    print(f"\n配置信息:")
    print(f"  App ID: {uploader.app_id[:10]}..." if uploader.app_id else "  App ID: 未设置")
    print(f"  App Secret: {'已设置' if uploader.app_secret else '未设置'}")
    
    if uploader.get_access_token():
        print("\n✅ 连接成功!")
        
        # 测试创建文档
        print("\n测试创建文档...")
        test_content = "# 测试文档\n\n这是一个测试文档，由公众号收集器自动创建。\n\n---\n*自动创建于 {}*".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        result = uploader.create_document(
            title="公众号收集器测试文档",
            content=test_content
        )
        
        if result:
            print(f"\n✅ 测试文档创建成功!")
            print(f"   文档ID: {result.get('document_id')}")
            print(f"   文档链接: {result.get('url', 'N/A')}")
        else:
            print("\n❌ 测试文档创建失败")
        
        return True
    else:
        print("\n❌ 连接失败!")
        return False

if __name__ == "__main__":
    test_docs_api()

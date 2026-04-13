#!/usr/bin/env python3
"""
Server Manager - MCP 服务器管理模块
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional


class ServerManager:
    """MCP 服务器管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path(__file__).parent.parent / "config.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            return {'servers': {}}
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {'servers': {}}
    
    def _save_config(self):
        """保存配置文件"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def list_servers(self) -> Dict[str, Dict[str, Any]]:
        """列出所有服务器配置"""
        return self.config.get('servers', {})
    
    def get_server(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定服务器配置"""
        return self.config.get('servers', {}).get(name)
    
    def add_stdio_server(self, name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        """添加 stdio 类型服务器"""
        if 'servers' not in self.config:
            self.config['servers'] = {}
        
        self.config['servers'][name] = {
            'type': 'stdio',
            'command': command,
            'args': args
        }
        
        if env:
            self.config['servers'][name]['env'] = env
        
        self._save_config()
    
    def add_http_server(self, name: str, url: str, headers: Optional[Dict[str, str]] = None):
        """添加 HTTP 类型服务器"""
        if 'servers' not in self.config:
            self.config['servers'] = {}
        
        self.config['servers'][name] = {
            'type': 'http',
            'url': url
        }
        
        if headers:
            self.config['servers'][name]['headers'] = headers
        
        self._save_config()
    
    def remove_server(self, name: str) -> bool:
        """删除服务器配置"""
        if name in self.config.get('servers', {}):
            del self.config['servers'][name]
            self._save_config()
            return True
        return False
    
    def update_server(self, name: str, updates: Dict[str, Any]) -> bool:
        """更新服务器配置"""
        if name not in self.config.get('servers', {}):
            return False
        
        self.config['servers'][name].update(updates)
        self._save_config()
        return True
    
    def get_server_types(self) -> Dict[str, int]:
        """统计服务器类型分布"""
        servers = self.list_servers()
        types = {}
        for config in servers.values():
            server_type = config.get('type', 'stdio')
            types[server_type] = types.get(server_type, 0) + 1
        return types


def main():
    """CLI 测试"""
    manager = ServerManager()
    
    print("MCP Server Manager")
    print("==================")
    print(f"\nConfig file: {manager.config_path}")
    print(f"\nServers:")
    
    servers = manager.list_servers()
    if not servers:
        print("  (none configured)")
    else:
        for name, config in servers.items():
            server_type = config.get('type', 'stdio')
            print(f"  - {name} ({server_type})")
            if server_type == 'stdio':
                print(f"    Command: {config.get('command')} {' '.join(config.get('args', []))}")
            elif server_type == 'http':
                print(f"    URL: {config.get('url')}")


if __name__ == "__main__":
    main()
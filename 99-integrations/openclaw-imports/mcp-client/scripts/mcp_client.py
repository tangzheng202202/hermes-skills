#!/usr/bin/env python3
"""
MCP Client - 主客户端模块
支持 stdio 和 HTTP 传输方式
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.types import TextContent, Tool, Resource


class MCPClient:
    """MCP 客户端主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or Path(__file__).parent.parent / "config.yaml"
        self.config = self._load_config()
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_servers(self) -> Dict[str, Dict[str, Any]]:
        """获取所有配置的服务器"""
        return self.config.get('servers', {})
    
    async def connect_stdio(self, name: str, server_config: Dict[str, Any]) -> ClientSession:
        """连接 stdio 模式的 MCP 服务器"""
        command = server_config['command']
        args = server_config.get('args', [])
        env = server_config.get('env')
        
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()
        
        self.sessions[name] = session
        return session
    
    async def connect_http(self, name: str, server_config: Dict[str, Any]) -> ClientSession:
        """连接 HTTP/SSE 模式的 MCP 服务器"""
        url = server_config['url']
        headers = server_config.get('headers', {})
        
        # 使用 SSE 客户端
        sse_transport = await self.exit_stack.enter_async_context(sse_client(url, headers=headers))
        read, write = sse_transport
        session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        
        self.sessions[name] = session
        return session
    
    async def connect(self, name: str) -> ClientSession:
        """连接到指定 MCP 服务器"""
        if name in self.sessions:
            return self.sessions[name]
        
        servers = self.get_servers()
        if name not in servers:
            raise ValueError(f"Server '{name}' not found in config")
        
        server_config = servers[name]
        server_type = server_config.get('type', 'stdio')
        
        if server_type == 'stdio':
            return await self.connect_stdio(name, server_config)
        elif server_type == 'http':
            return await self.connect_http(name, server_config)
        else:
            raise ValueError(f"Unsupported server type: {server_type}")
    
    async def list_tools(self, server_name: str) -> List[Tool]:
        """列出服务器可用工具"""
        session = await self.connect(server_name)
        result = await session.list_tools()
        return result.tools
    
    async def call_tool(self, server_name: str, tool_name: str, params: Dict[str, Any]) -> List[TextContent]:
        """调用指定工具"""
        session = await self.connect(server_name)
        result = await session.call_tool(tool_name, params)
        return result.content
    
    async def list_resources(self, server_name: str) -> List[Resource]:
        """列出服务器可用资源"""
        session = await self.connect(server_name)
        result = await session.list_resources()
        return result.resources
    
    async def read_resource(self, server_name: str, uri: str) -> str:
        """读取指定资源"""
        session = await self.connect(server_name)
        result = await session.read_resource(uri)
        return result.contents[0].text if result.contents else ""
    
    async def test_connection(self, server_name: str) -> bool:
        """测试服务器连接"""
        try:
            session = await self.connect(server_name)
            # 尝试获取服务器信息
            await session.list_tools()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    async def close(self):
        """关闭所有连接"""
        await self.exit_stack.aclose()
        self.sessions.clear()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def main():
    """测试主函数"""
    client = MCPClient()
    
    # 列出所有服务器
    print("Configured servers:")
    for name, config in client.get_servers().items():
        print(f"  - {name} ({config.get('type', 'stdio')})")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
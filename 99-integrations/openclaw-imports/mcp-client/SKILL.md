# MCP Client Skill

MCP (Model Context Protocol) Client for OpenClaw - 连接和调用外部 MCP 服务器。

## 功能

- 连接 MCP 服务器（stdio 和 HTTP 模式）
- 发现并调用 MCP Tools
- 读取 MCP Resources
- 管理 MCP 服务器配置

## 安装依赖

```bash
cd ~/.openclaw/workspace/skills/mcp-client
pip install -r requirements.txt
```

## 使用方法

### 1. 配置 MCP 服务器

编辑 `config.yaml`：

```yaml
servers:
  filesystem:
    type: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
  
  fetch:
    type: stdio
    command: uvx
    args: ["mcp-server-fetch"]
  
  remote-server:
    type: http
    url: https://api.example.com/mcp
    headers:
      Authorization: Bearer YOUR_TOKEN
```

### 2. 列出可用工具

```bash
python scripts/mcp_client.py --server filesystem list-tools
```

### 3. 调用工具

```bash
python scripts/mcp_client.py --server filesystem call-tool read_file --params '{"path": "/path/to/file"}'
```

### 4. 读取资源

```bash
python scripts/mcp_client.py --server filesystem read-resource resource://file/path
```

## CLI 命令

```
Usage: mcp_client.py [OPTIONS] COMMAND [ARGS]...

Options:
  --server TEXT  MCP server name (from config)
  --config PATH  Config file path
  --help         Show this message and exit.

Commands:
  list-servers      列出所有配置的 MCP 服务器
  list-tools        列出服务器可用工具
  call-tool         调用指定工具
  read-resource     读取指定资源
  test-connection   测试服务器连接
```

## 在 OpenClaw 中使用

```python
# 通过 OpenClaw 工具调用
from skills.mcp_client.scripts.mcp_client import MCPClient

client = MCPClient()
result = await client.call_tool("filesystem", "read_file", {"path": "/path/to/file"})
```

## 支持的传输方式

- **stdio**: 本地命令行工具（如 npx、uvx、python 脚本）
- **http**: 远程 HTTP API 服务器

## 参考

- [MCP Protocol](https://modelcontextprotocol.io/)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
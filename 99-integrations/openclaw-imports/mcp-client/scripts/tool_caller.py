#!/usr/bin/env python3
"""
Tool Caller - MCP 工具调用 CLI 模块
"""

import asyncio
import json
import click
from pathlib import Path
from typing import Any, Dict

from mcp_client import MCPClient
from server_manager import ServerManager


@click.group()
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.pass_context
def cli(ctx, config):
    """MCP Client CLI - 调用外部 MCP 服务器工具"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config


@cli.command()
@click.pass_context
def list_servers(ctx):
    """列出所有配置的 MCP 服务器"""
    manager = ServerManager(ctx.obj.get('config'))
    servers = manager.list_servers()
    
    if not servers:
        click.echo("No servers configured.")
        return
    
    click.echo("Configured MCP servers:")
    click.echo("-" * 40)
    
    for name, config in servers.items():
        server_type = config.get('type', 'stdio')
        click.echo(f"\n📡 {name} ({server_type})")
        
        if server_type == 'stdio':
            cmd = config.get('command', '')
            args = ' '.join(config.get('args', []))
            click.echo(f"   Command: {cmd} {args}")
        elif server_type == 'http':
            click.echo(f"   URL: {config.get('url', 'N/A')}")


@cli.command()
@click.option('--server', '-s', required=True, help='Server name')
@click.pass_context
def list_tools(ctx, server):
    """列出服务器可用工具"""
    async def _list():
        async with MCPClient(ctx.obj.get('config')) as client:
            try:
                tools = await client.list_tools(server)
                
                if not tools:
                    click.echo(f"No tools available on server '{server}'.")
                    return
                
                click.echo(f"Tools on '{server}':")
                click.echo("-" * 40)
                
                for tool in tools:
                    click.echo(f"\n🔧 {tool.name}")
                    if tool.description:
                        click.echo(f"   Description: {tool.description}")
                    if tool.inputSchema:
                        click.echo(f"   Parameters: {json.dumps(tool.inputSchema, indent=2, ensure_ascii=False)}")
                        
            except Exception as e:
                click.echo(f"Error: {e}", err=True)
    
    asyncio.run(_list())


@cli.command()
@click.option('--server', '-s', required=True, help='Server name')
@click.option('--tool', '-t', 'tool_name', required=True, help='Tool name')
@click.option('--params', '-p', default='{}', help='Tool parameters as JSON string')
@click.pass_context
def call_tool(ctx, server, tool_name, params):
    """调用指定工具"""
    async def _call():
        async with MCPClient(ctx.obj.get('config')) as client:
            try:
                params_dict = json.loads(params)
                result = await client.call_tool(server, tool_name, params_dict)
                
                click.echo(f"Result from '{tool_name}':")
                click.echo("-" * 40)
                
                for content in result:
                    if hasattr(content, 'text'):
                        click.echo(content.text)
                    else:
                        click.echo(str(content))
                        
            except json.JSONDecodeError:
                click.echo(f"Error: Invalid JSON in params: {params}", err=True)
            except Exception as e:
                click.echo(f"Error: {e}", err=True)
    
    asyncio.run(_call())


@cli.command()
@click.option('--server', '-s', required=True, help='Server name')
@click.pass_context
def list_resources(ctx, server):
    """列出服务器可用资源"""
    async def _list():
        async with MCPClient(ctx.obj.get('config')) as client:
            try:
                resources = await client.list_resources(server)
                
                if not resources:
                    click.echo(f"No resources available on server '{server}'.")
                    return
                
                click.echo(f"Resources on '{server}':")
                click.echo("-" * 40)
                
                for resource in resources:
                    click.echo(f"\n📄 {resource.uri}")
                    if resource.name:
                        click.echo(f"   Name: {resource.name}")
                    if resource.description:
                        click.echo(f"   Description: {resource.description}")
                        
            except Exception as e:
                click.echo(f"Error: {e}", err=True)
    
    asyncio.run(_list())


@cli.command()
@click.option('--server', '-s', required=True, help='Server name')
@click.option('--uri', '-u', required=True, help='Resource URI')
@click.pass_context
def read_resource(ctx, server, uri):
    """读取指定资源"""
    async def _read():
        async with MCPClient(ctx.obj.get('config')) as client:
            try:
                content = await client.read_resource(server, uri)
                
                click.echo(f"Content of '{uri}':")
                click.echo("-" * 40)
                click.echo(content)
                        
            except Exception as e:
                click.echo(f"Error: {e}", err=True)
    
    asyncio.run(_read())


@cli.command()
@click.option('--server', '-s', required=True, help='Server name')
@click.pass_context
def test_connection(ctx, server):
    """测试服务器连接"""
    async def _test():
        async with MCPClient(ctx.obj.get('config')) as client:
            click.echo(f"Testing connection to '{server}'...")
            
            if await client.test_connection(server):
                click.echo(f"✅ Successfully connected to '{server}'")
            else:
                click.echo(f"❌ Failed to connect to '{server}'")
    
    asyncio.run(_test())


@cli.command()
@click.option('--name', '-n', required=True, help='Server name')
@click.option('--command', '-c', help='Command for stdio server')
@click.option('--args', '-a', help='Arguments (comma-separated)')
@click.option('--url', '-u', help='URL for HTTP server')
@click.option('--type', 'server_type', type=click.Choice(['stdio', 'http']), default='stdio', help='Server type')
@click.pass_context
def add_server(ctx, name, command, args, url, server_type):
    """添加新服务器配置"""
    manager = ServerManager(ctx.obj.get('config'))
    
    if server_type == 'stdio':
        if not command:
            click.echo("Error: --command is required for stdio servers", err=True)
            return
        
        args_list = args.split(',') if args else []
        manager.add_stdio_server(name, command, args_list)
        click.echo(f"✅ Added stdio server '{name}'")
        
    elif server_type == 'http':
        if not url:
            click.echo("Error: --url is required for HTTP servers", err=True)
            return
        
        manager.add_http_server(name, url)
        click.echo(f"✅ Added HTTP server '{name}'")


@cli.command()
@click.option('--name', '-n', required=True, help='Server name')
@click.pass_context
def remove_server(ctx, name):
    """删除服务器配置"""
    manager = ServerManager(ctx.obj.get('config'))
    
    if manager.remove_server(name):
        click.echo(f"✅ Removed server '{name}'")
    else:
        click.echo(f"❌ Server '{name}' not found")


if __name__ == '__main__':
    cli()
"""
MCP (Model Context Protocol) Integration Module

This module provides integration with MCP servers for enhanced context management
and tool calling capabilities as required by the assignment.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class MCPServer:
    """Represents an MCP server configuration"""
    name: str
    url: str
    capabilities: List[str]
    description: str

class MCPManager:
    """Manages MCP server connections and tool execution"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.active_connections: Dict[str, Any] = {}
        self._initialize_default_servers()
    
    def _initialize_default_servers(self):
        """Initialize default MCP servers"""
        default_servers = [
            MCPServer(
                name="filesystem",
                url="mcp://localhost:3001",
                capabilities=["file_read", "file_write", "file_list"],
                description="File system operations"
            ),
            MCPServer(
                name="git",
                url="mcp://localhost:3002", 
                capabilities=["git_status", "git_commit", "git_push"],
                description="Git repository management"
            ),
            MCPServer(
                name="http",
                url="mcp://localhost:3003",
                capabilities=["http_get", "http_post", "http_put"],
                description="HTTP request handling"
            ),
            MCPServer(
                name="database",
                url="mcp://localhost:3004",
                capabilities=["db_query", "db_insert", "db_update"],
                description="Database operations"
            )
        ]
        
        for server in default_servers:
            self.servers[server.name] = server
    
    async def connect_to_server(self, server_name: str) -> bool:
        """Connect to an MCP server"""
        try:
            if server_name not in self.servers:
                logger.error(f"Unknown MCP server: {server_name}")
                return False
            
            server = self.servers[server_name]
            
            # Simulate connection (in real implementation, this would use actual MCP protocol)
            self.active_connections[server_name] = {
                "connected": True,
                "server": server,
                "last_used": asyncio.get_event_loop().time()
            }
            
            logger.info(f"Connected to MCP server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            return False
    
    async def execute_tool(self, server_name: str, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on an MCP server"""
        try:
            if server_name not in self.active_connections:
                await self.connect_to_server(server_name)
            
            if server_name not in self.active_connections:
                return {"error": f"Could not connect to MCP server: {server_name}"}
            
            # Simulate tool execution (in real implementation, this would use actual MCP protocol)
            server = self.servers[server_name]
            
            # Update last used time
            self.active_connections[server_name]["last_used"] = asyncio.get_event_loop().time()
            
            # Simulate different tool responses based on server and tool
            if server_name == "filesystem":
                return await self._execute_filesystem_tool(tool_name, params)
            elif server_name == "git":
                return await self._execute_git_tool(tool_name, params)
            elif server_name == "http":
                return await self._execute_http_tool(tool_name, params)
            elif server_name == "database":
                return await self._execute_database_tool(tool_name, params)
            else:
                return {"error": f"Unknown server: {server_name}"}
                
        except Exception as e:
            logger.error(f"Error executing MCP tool {tool_name} on {server_name}: {e}")
            return {"error": str(e)}
    
    async def _execute_filesystem_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute filesystem-related tools"""
        if tool_name == "file_read":
            path = params.get("path", "")
            return {
                "success": True,
                "data": f"Simulated file read from: {path}",
                "content": "This is simulated file content from MCP filesystem server."
            }
        elif tool_name == "file_list":
            path = params.get("path", ".")
            return {
                "success": True,
                "data": f"Files in {path}:",
                "files": ["file1.txt", "file2.py", "directory1/"]
            }
        else:
            return {"error": f"Unknown filesystem tool: {tool_name}"}
    
    async def _execute_git_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git-related tools"""
        if tool_name == "git_status":
            return {
                "success": True,
                "data": "Git repository status:",
                "status": "clean",
                "changes": []
            }
        elif tool_name == "git_commit":
            message = params.get("message", "Update")
            return {
                "success": True,
                "data": f"Committed with message: {message}",
                "commit_hash": "abc123def456"
            }
        else:
            return {"error": f"Unknown git tool: {tool_name}"}
    
    async def _execute_http_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP-related tools"""
        url = params.get("url", "")
        
        if tool_name == "http_get":
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as response:
                        content = await response.text()
                        return {
                            "success": True,
                            "data": f"HTTP GET response from {url}",
                            "status": response.status,
                            "content": content[:500] + "..." if len(content) > 500 else content
                        }
                except Exception as e:
                    return {"error": f"HTTP GET failed: {e}"}
        else:
            return {"error": f"Unknown HTTP tool: {tool_name}"}
    
    async def _execute_database_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database-related tools"""
        if tool_name == "db_query":
            query = params.get("query", "")
            return {
                "success": True,
                "data": f"Database query executed: {query}",
                "results": [{"id": 1, "name": "example"}]
            }
        else:
            return {"error": f"Unknown database tool: {tool_name}"}
    
    def get_available_servers(self) -> List[Dict[str, Any]]:
        """Get list of available MCP servers"""
        return [
            {
                "name": server.name,
                "url": server.url,
                "capabilities": server.capabilities,
                "description": server.description,
                "connected": server.name in self.active_connections
            }
            for server in self.servers.values()
        ]
    
    def get_server_capabilities(self, server_name: str) -> List[str]:
        """Get capabilities of a specific MCP server"""
        if server_name in self.servers:
            return self.servers[server_name].capabilities
        return []
    
    async def disconnect_from_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        try:
            if server_name in self.active_connections:
                del self.active_connections[server_name]
                logger.info(f"Disconnected from MCP server: {server_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {server_name}: {e}")
            return False

# Global MCP manager instance
mcp_manager = MCPManager()

async def get_mcp_response(message: str) -> str:
    """Get response using MCP servers"""
    try:
        # Check if message contains MCP-related requests
        mcp_patterns = {
            r'\b(file|read|write|list)\s+(.+?)\b': ("filesystem", "file_read"),
            r'\bgit\s+(status|commit|push)\b': ("git", "git_status"),
            r'\bhttp\s+(get|post)\s+(https?://\S+)': ("http", "http_get"),
            r'\b(database|db|query)\s+(.+?)\b': ("database", "db_query")
        }
        
        for pattern, (server_name, tool_name) in mcp_patterns.items():
            import re
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                # Extract parameters based on the pattern
                params = {}
                if server_name == "filesystem":
                    params["path"] = match.group(2)
                elif server_name == "git":
                    params["action"] = match.group(1)
                elif server_name == "http":
                    params["url"] = match.group(2)
                elif server_name == "database":
                    params["query"] = match.group(2)
                
                # Execute the MCP tool
                result = await mcp_manager.execute_tool(server_name, tool_name, params)
                
                if "error" in result:
                    return f"❌ MCP Error: {result['error']}"
                else:
                    return f"✅ MCP {server_name} result: {result.get('data', 'Operation completed')}"
        
        return "I can help you with MCP operations! Try asking about files, git, HTTP requests, or database queries."
        
    except Exception as e:
        logger.error(f"Error in MCP response: {e}")
        return f"❌ MCP Error: {str(e)}" 
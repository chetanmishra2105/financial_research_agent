"""
MCP Client - Client for interacting with MCP servers
"""
from typing import Any, Dict, List, Optional
from src.utils.logger import logger, log_input, log_output
import asyncio


class MCPClient:
    """
    Client for Model Context Protocol servers
    
    Provides interface for agents to discover and use tools
    from MCP servers.
    """
    
    def __init__(self, server_manager=None):
        self.server_manager = server_manager
        self.connected_servers: Dict[str, Any] = {}
        self.tool_cache: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, server_name: str, server_instance: Any) -> bool:
        """
        Connect to an MCP server
        
        Args:
            server_name: Name of the server
            server_instance: Server instance
            
        Returns:
            Connection success status
        """
        try:
            log_input("MCPClient.connect", {"server_name": server_name})
            self.connected_servers[server_name] = server_instance
            
            # Cache available tools
            tools = server_instance.list_tools()
            for tool in tools:
                self.tool_cache[f"{server_name}:{tool['name']}"] = tool
                
            logger.info(f"Connected to MCP server: {server_name}")
            log_output("MCPClient.connect", {"server_name": server_name, "tool_count": len(tools)})
            return True
            
        except Exception as e:
            logger.exception(f"Failed to connect to server {server_name}: {str(e)}")
            return False
    
    async def list_tools(self, server_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available tools
        
        Args:
            server_name: Optional server name to filter tools
            
        Returns:
            List of tool definitions
        """
        if server_name:
            server = self.connected_servers.get(server_name)
            if server:
                return server.list_tools()
            return []
        
        # Return all tools from all connected servers
        all_tools = []
        for name, server in self.connected_servers.items():
            tools = server.list_tools()
            for tool in tools:
                tool["server"] = name
                all_tools.append(tool)
                
        return all_tools
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on an MCP server
        
        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        server = self.connected_servers.get(server_name)
        
        if not server:
            return {
                "success": False,
                "error": f"Server {server_name} not connected"
            }
        
        try:
            log_input("MCPClient.call_tool", {"server_name": server_name, "tool_name": tool_name, "arguments": arguments})
            result = await server.call_tool(tool_name, arguments)
            log_output("MCPClient.call_tool", {"server_name": server_name, "tool_name": tool_name, "result": result})
            return result
            
        except Exception as e:
            logger.exception(f"Tool call failed: {str(e)}")
            error_result = {
                "success": False,
                "error": str(e)
            }
            log_output("MCPClient.call_tool", {"server_name": server_name, "tool_name": tool_name, "result": error_result})
            return error_result
    
    def get_tool_info(self, server_name: str, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        cache_key = f"{server_name}:{tool_name}"
        return self.tool_cache.get(cache_key)
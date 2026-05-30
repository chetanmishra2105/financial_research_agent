"""
MCP Server implementation following Model Context Protocol
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import asyncio
import json
from src.utils.logger import logger, log_input, log_output


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Any = None  # Will be set dynamically


class MCPServer:
    """
    Model Context Protocol Server
    
    Provides standardized interface for AI agents to discover and use tools.
    Think of it as "USB-C for AI agents and tools"
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.capabilities: Dict[str, Any] = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }
        
    def register_tool(self, tool: MCPTool) -> None:
        """Register a new tool with the MCP server"""
        self.tools[tool.name] = tool
        self.capabilities["tools"][tool.name] = {
            "description": tool.description,
            "input_schema": tool.input_schema
        }
        logger.info(f"Registered tool: {tool.name}")
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": name,
                "description": tool.description,
                "input_schema": tool.input_schema
            }
            for name, tool in self.tools.items()
        ]
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a specific tool with arguments
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool {tool_name} not found"
            }
        
        tool = self.tools[tool_name]
        
        try:
            log_input(f"{self.name}.call_tool", {"tool_name": tool_name, "arguments": arguments})
            # Validate input against schema
            self._validate_input(arguments, tool.input_schema)
            
            # Execute tool
            result = await tool.handler(**arguments)
            output = {
                "success": True,
                "result": result,
                "tool": tool_name
            }
            log_output(f"{self.name}.call_tool", output)
            return output
            
        except Exception as e:
            logger.exception(f"Tool execution failed: {str(e)}")
            error_output = {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
            log_output(f"{self.name}.call_tool", error_output)
            return error_output
    
    def _validate_input(
        self,
        arguments: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> None:
        """Validate input arguments against schema"""
        # Basic validation - can be enhanced with JSON Schema validation
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in arguments:
                raise ValueError(f"Missing required field: {field}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        return {
            "server_name": self.name,
            "version": self.version,
            "capabilities": self.capabilities
        }


class MCPServerManager:
    """Manages multiple MCP servers"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        
    def register_server(self, server: MCPServer) -> None:
        """Register an MCP server"""
        self.servers[server.name] = server
        logger.info(f"Registered MCP server: {server.name}")
        
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get a specific MCP server"""
        return self.servers.get(name)
    
    def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List tools from all servers"""
        return {
            server_name: server.list_tools()
            for server_name, server in self.servers.items()
        }
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool from a specific server"""
        server = self.get_server(server_name)
        if not server:
            return {"success": False, "error": f"Server {server_name} not found"}
        
        return await server.call_tool(tool_name, arguments)
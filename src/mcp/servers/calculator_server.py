"""
Financial Calculator MCP Server
"""
from src.mcp.mcp_server import MCPServer, MCPTool
from src.utils.logger import logger


class CalculatorServer(MCPServer):
    """MCP Server for financial calculations"""
    
    def __init__(self):
        super().__init__("CalculatorServer", "1.0.0")
        self._register_tools()
    
    def _register_tools(self):
        """Register calculator tools"""
        
        self.register_tool(MCPTool(
            name="calculate_ratio",
            description="Calculate financial ratio",
            input_schema={
                "type": "object",
                "properties": {
                    "ratio_type": {"type": "string", "description": "Type of ratio (PE, ROE, etc.)"},
                    "values": {"type": "object", "description": "Input values"}
                },
                "required": ["ratio_type", "values"]
            },
            handler=self.calculate_ratio
        ))
    
    async def calculate_ratio(self, ratio_type: str, values: dict) -> dict:
        """Calculate financial ratio"""
        logger.info(f"Calculating {ratio_type}")
        
"""
Market Data MCP Server
"""
from src.mcp.mcp_server import MCPServer, MCPTool
from src.utils.logger import logger


class MarketDataServer(MCPServer):
    """MCP Server for market data"""
    
    def __init__(self):
        super().__init__("MarketDataServer", "1.0.0")
        self._register_tools()
    
    def _register_tools(self):
        """Register market data tools"""
        
        self.register_tool(MCPTool(
            name="get_stock_price",
            description="Get current stock price",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            },
            handler=self.get_stock_price
        ))
    
    async def get_stock_price(self, ticker: str) -> dict:
        """Get stock price"""
        logger.info(f"Getting stock price for {ticker}")
        
        # Simulate stock price
        return {
            "ticker": ticker.upper(),
            "price": 150.00,
            "currency": "USD",
            "timestamp": "2024-01-15T10:30:00Z"
        }
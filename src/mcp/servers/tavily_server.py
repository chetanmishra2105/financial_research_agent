"""
Tavily News Search MCP Server
"""
from src.mcp.mcp_server import MCPServer, MCPTool
from src.utils.logger import logger


class TavilyServer(MCPServer):
    """MCP Server for Tavily news search"""
    
    def __init__(self):
        super().__init__("TavilyServer", "1.0.0")
        self._register_tools()
    
    def _register_tools(self):
        """Register Tavily-related tools"""
        
        self.register_tool(MCPTool(
            name="search_news",
            description="Search latest financial news",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            },
            handler=self.search_news
        ))
    
    async def search_news(self, query: str, max_results: int = 10) -> dict:
        """Search for news"""
        logger.info(f"Searching news for: {query}")
        
        # Simulate news search
        return {
            "query": query,
            "results": [
                {
                    "title": f"Latest news about {query}",
                    "url": "https://example.com/news",
                    "source": "Reuters",
                    "date": "2024-01-15"
                }
            ]
        }
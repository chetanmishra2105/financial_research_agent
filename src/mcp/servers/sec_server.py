"""
SEC EDGAR MCP Server
"""
from src.mcp.mcp_server import MCPServer, MCPTool
from src.utils.logger import logger


class SECServer(MCPServer):
    """MCP Server for SEC EDGAR database access"""
    
    def __init__(self):
        super().__init__("SECServer", "1.0.0")
        self._register_tools()
    
    def _register_tools(self):
        """Register SEC-related tools"""
        
        # Register filing retrieval tool
        self.register_tool(MCPTool(
            name="get_sec_filing",
            description="Retrieve SEC filing for a company",
            input_schema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name or ticker"},
                    "filing_type": {"type": "string", "description": "Filing type (10-K, 10-Q, 8-K)"},
                    "year": {"type": "integer", "description": "Filing year"}
                },
                "required": ["company"]
            },
            handler=self.get_sec_filing
        ))
        
        # Register company search tool
        self.register_tool(MCPTool(
            name="search_company",
            description="Search for company by name or ticker",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            },
            handler=self.search_company
        ))
    
    async def get_sec_filing(self, company: str, filing_type: str = "10-K", year: int = 2024) -> dict:
        """Get SEC filing for a company"""
        logger.info(f"Retrieving {filing_type} for {company} ({year})")
        
        # Simulate SEC filing retrieval
        return {
            "company": company,
            "filing_type": filing_type,
            "year": year,
            "document_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={company}",
            "sections": {
                "business": "Company business description...",
                "risk_factors": "Risk factors section...",
                "financial_data": "Financial statements..."
            }
        }
    
    async def search_company(self, query: str) -> dict:
        """Search for company"""
        logger.info(f"Searching for company: {query}")
        
        return {
            "query": query,
            "results": [
                {"name": query.upper(), "cik": "0000789019"}
            ]
        }
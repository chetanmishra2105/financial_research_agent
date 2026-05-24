"""
Tavily News Search MCP Tool
"""
from typing import Any, Dict, Optional
from tavily import TavilyClient
from src.mcp.mcp_server import MCPTool
from config.settings import settings
from src.utils.logger import logger
from datetime import datetime, timedelta


class NewsSearchTool:
    """Tool for searching latest financial news using Tavily"""
    
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        
    async def search(
        self,
        query: str,
        max_results: int = 10,
        include_domains: Optional[list] = None,
        exclude_domains: Optional[list] = None,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Search for latest news
        
        Args:
            query: Search query
            max_results: Maximum number of results
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            days_back: Number of days to look back
            
        Returns:
            Search results with sentiment analysis
        """
        try:
            # Enhance query for financial context
            enhanced_query = f"{query} financial news stock market"
            
            # Execute search
            response = self.client.search(
                query=enhanced_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=include_domains or [
                    "reuters.com",
                    "bloomberg.com",
                    "wsj.com",
                    "ft.com",
                    "cnbc.com"
                ]
            )
            
            # Process and analyze results
            results = []
            for article in response.get("results", []):
                # Simple sentiment analysis (can be enhanced with NLP)
                sentiment = self._analyze_sentiment(article.get("content", ""))
                
                results.append({
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "content": article.get("content", "")[:500],  # Truncate
                    "published_date": article.get("published_date"),
                    "source": article.get("source"),
                    "sentiment": sentiment,
                    "relevance_score": self._calculate_relevance(
                        article.get("content", ""),
                        query
                    )
                })
            
            # Sort by relevance
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return {
                "success": True,
                "query": query,
                "total_results": len(results),
                "results": results,
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"News search failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple rule-based sentiment analysis"""
        positive_words = [
            "growth", "profit", "increase", "positive", "strong",
            "opportunity", "innovation", "leadership", "expansion"
        ]
        negative_words = [
            "decline", "loss", "risk", "concern", "weak",
            "threat", "challenge", "investigation", "fine"
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate relevance score based on keyword matches"""
        query_terms = query.lower().split()
        content_lower = content.lower()
        
        matches = sum(1 for term in query_terms if term in content_lower)
        return matches / len(query_terms) if query_terms else 0.0
    
    def get_mcp_tool(self) -> MCPTool:
        """Get MCP tool definition"""
        return MCPTool(
            name="news_search",
            description="Search latest financial news and market updates",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "default": 10},
                    "days_back": {"type": "integer", "default": 7}
                },
                "required": ["query"]
            },
            handler=self.search
        )
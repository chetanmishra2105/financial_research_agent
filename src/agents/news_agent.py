"""
News Research Agent
"""
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from src.agents.base_agent import BaseAgent
from src.utils.logger import logger, log_agent_io, log_input, log_output
from datetime import datetime


class NewsResearchAgent(BaseAgent):
    """Agent responsible for searching and analyzing latest news"""
    
    def __init__(self, llm: ChatOpenAI = None):
        super().__init__(
            name="NewsResearchAgent",
            description="Searches and analyzes latest market news and developments",
            llm=llm
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process news search request"""
        company = input_data.get("company", "Unknown")
        
        try:
            log_input(f"{self.name}.process", input_data)
            log_agent_io(self.name, "input", input_data)
            logger.info(f"News Agent searching for {company} news")
            
            # Simulate news search results
            news_data = {
                "company": company,
                "search_timestamp": datetime.now().isoformat(),
                "articles": [
                    {
                        "title": f"{company} Announces Record Quarterly Results",
                        "source": "Reuters",
                        "date": "2024-01-15",
                        "sentiment": "positive",
                        "summary": f"{company} reported better-than-expected earnings..."
                    },
                    {
                        "title": f"AI Demand Drives {company} Growth",
                        "source": "Bloomberg",
                        "date": "2024-01-14",
                        "sentiment": "positive",
                        "summary": "Growing AI adoption continues to benefit..."
                    },
                    {
                        "title": f"Regulatory Concerns for {company}",
                        "source": "WSJ",
                        "date": "2024-01-13",
                        "sentiment": "negative",
                        "summary": "New export restrictions may impact..."
                    }
                ],
                "overall_sentiment": "positive",
                "key_themes": ["AI Growth", "Regulatory Risk", "Market Leadership"]
            }
            
            result = {
                "success": True,
                "agent": self.name,
                "data": news_data,
                "message": f"Latest news retrieved for {company}"
            }
            log_output(f"{self.name}.process", result)
            return result
        except Exception as e:
            logger.exception(f"Error in {self.name}.process: {str(e)}")
            error_result = {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "message": f"Failed to retrieve news for {company}"
            }
            log_output(f"{self.name}.process", error_result)
            return error_result
"""
Financial Metrics Analysis Agent
"""
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from src.agents.base_agent import BaseAgent
from src.utils.logger import logger, log_agent_io, log_input, log_output


class FinancialMetricsAgent(BaseAgent):
    """Agent responsible for calculating and analyzing financial metrics"""
    
    def __init__(self, llm: ChatOpenAI = None):
        super().__init__(
            name="FinancialMetricsAgent",
            description="Calculates and analyzes financial KPIs and ratios",
            llm=llm
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process financial metrics calculation"""
        company = input_data.get("company", "Unknown")
        sec_data = input_data.get("sec_data", {})
        
        try:
            log_input(f"{self.name}.process", input_data)
            log_agent_io(self.name, "input", input_data)
            logger.info(f"Metrics Agent analyzing {company}")
            
            # Simulate financial metrics calculation
            metrics = {
                "company": company,
                "revenue_growth": "+126%",
                "gross_margin": "74%",
                "operating_margin": "54%",
                "net_margin": "48%",
                "pe_ratio": "65.2",
                "eps_growth": "+128%",
                "roe": "92.3%",
                "debt_to_equity": "0.28",
                "free_cash_flow": "$27.5B",
                "cash_flow_growth": "+145%",
                "market_cap": "$1.2T",
                "dividend_yield": "0.04%"
            }
            
            output = {
                "success": True,
                "agent": self.name,
                "data": metrics,
                "message": f"Financial metrics calculated for {company}"
            }
            log_agent_io(self.name, "output", output)
            log_output(f"{self.name}.process", output)
            return output
        except Exception as e:
            logger.exception(f"Error in {self.name}.process: {str(e)}")
            error_result = {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "message": f"Financial metrics calculation failed for {company}"
            }
            log_output(f"{self.name}.process", error_result)
            return error_result
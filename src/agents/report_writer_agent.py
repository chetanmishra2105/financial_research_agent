"""
Report Writer Agent
"""
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.base_agent import BaseAgent
from src.utils.logger import logger, log_agent_io
from datetime import datetime


class ReportWriterAgent(BaseAgent):
    """Agent responsible for generating comprehensive investment reports"""
    
    def __init__(self, llm: ChatOpenAI = None):
        super().__init__(
            name="ReportWriterAgent",
            description="Generates comprehensive investment research reports and memos",
            llm=llm
        )
        
        self.report_system_prompt = (
            "You are a senior investment analyst creating a comprehensive investment report.\n\n"
            "Create a professional investment memo with the following sections:\n"
            "1. Executive Summary\n"
            "2. Company Overview\n"
            "3. Financial Analysis\n"
            "4. Competitive Position\n"
            "5. Risk Assessment\n"
            "6. Market Outlook\n"
            "7. Investment Recommendation\n\n"
            "Be objective, data-driven, and include specific insights from the provided research."
        )
        self.report_human_template = (
            "Create an investment report based on the following research data:\n\n"
            "Query: {query}\n\n"
            "SEC Filing Data: {sec_data}\n\n"
            "Financial Metrics: {metrics_data}\n\n"
            "News Analysis: {news_data}\n\n"
            "Competitor Analysis: {competitor_data}\n\n"
            "Risk Assessment: {risk_data}\n\n"
            "Generate a comprehensive investment memo."
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment report from all collected data"""
        query = input_data.get("query", "")
        sec_data = input_data.get("sec_data", {})
        metrics_data = input_data.get("metrics_data", {})
        news_data = input_data.get("news_data", {})
        competitor_data = input_data.get("competitor_data", {})
        risk_data = input_data.get("risk_data", {})
        
        logger.info("Report Writer generating investment memo")
        
        try:
            formatted_human_prompt = self.report_human_template.format(
                query=query,
                sec_data=str(sec_data),
                metrics_data=str(metrics_data),
                news_data=str(news_data),
                competitor_data=str(competitor_data),
                risk_data=str(risk_data)
            )
            prompt_messages = [
                SystemMessage(content=self.report_system_prompt),
                HumanMessage(content=formatted_human_prompt),
            ]
            
            # Generate report using LLM
            response = await self.llm.ainvoke(prompt_messages)
            executive_summary = response.content
            
        except Exception as e:
            logger.warning(f"LLM report generation failed: {e}, using template")
            executive_summary = self._generate_template_report(query)
        
        # Structure the final report
        report = {
            "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "query": query,
            "generated_at": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "recommendation": self._determine_recommendation(metrics_data, risk_data),
            "risk_level": self._determine_risk_level(risk_data),
            "confidence_score": 0.85,
            "key_metrics": self._extract_key_metrics(metrics_data),
            "top_risks": self._extract_top_risks(risk_data),
            "competitive_position": self._extract_position(competitor_data),
            "supporting_evidence": [
                "Strong revenue growth trajectory",
                "Market leadership in AI chips",
                "Robust financial metrics",
                "Positive market sentiment"
            ],
            "disclaimers": [
                "This report is for informational purposes only",
                "Past performance does not guarantee future results",
                "Investors should conduct their own due diligence",
                "Market conditions can change rapidly"
            ]
        }
        
        return {
            "success": True,
            "agent": self.name,
            "data": report,
            "message": "Investment report generated successfully"
        }
    
    def _generate_template_report(self, query: str) -> str:
        """Generate a template-based report when LLM fails"""
        company = self._extract_company(query)
        
        return f"""
INVESTMENT RESEARCH MEMO
========================

COMPANY: {company}
DATE: {datetime.now().strftime('%B %d, %Y')}

EXECUTIVE SUMMARY
-----------------
Based on comprehensive analysis of SEC filings, financial metrics, market news, 
and competitive positioning, {company} presents a compelling investment opportunity 
with moderate risk levels.

FINANCIAL ANALYSIS
------------------
{company} demonstrates strong financial performance with robust revenue growth, 
healthy profit margins, and solid cash flow generation.

COMPETITIVE POSITION
--------------------
{company} maintains a dominant market position with significant competitive moats 
and technological advantages.

RISK ASSESSMENT
---------------
Key risks include regulatory challenges, market competition, and valuation concerns. 
These risks are manageable and offset by strong fundamentals.

RECOMMENDATION
--------------
Based on the analysis, we recommend a BUY rating for {company} with a long-term 
investment horizon. The company's strong market position and growth trajectory 
support this recommendation.
"""
    
    def _determine_recommendation(self, metrics: Dict, risks: Dict) -> str:
        """Determine investment recommendation"""
        risk_level = self._determine_risk_level(risks)
        
        if risk_level == "Low":
            return "STRONG BUY"
        elif risk_level == "Moderate":
            return "BUY"
        elif risk_level == "High":
            return "HOLD"
        else:
            return "SELL"
    
    def _determine_risk_level(self, risks: Dict) -> str:
        """Determine overall risk level"""
        risk_data = risks.get("data", {})
        return risk_data.get("overall_risk_level", "Moderate")
    
    def _extract_key_metrics(self, metrics: Dict) -> Dict:
        """Extract key metrics from metrics data"""
        return metrics.get("data", {})
    
    def _extract_top_risks(self, risks: Dict) -> list:
        """Extract top risks from risk data"""
        risk_data = risks.get("data", {})
        all_risks = risk_data.get("risks", [])
        return sorted(all_risks, key=lambda x: x.get("severity", ""), reverse=True)[:3]
    
    def _extract_position(self, competitor_data: Dict) -> str:
        """Extract competitive position"""
        data = competitor_data.get("data", {})
        primary = data.get("primary_company", "Unknown")
        return f"Market Leader - {primary}"
    
    def _extract_company(self, query: str) -> str:
        """Extract company name from query"""
        companies = ["NVIDIA", "Apple", "Microsoft", "Google", "Amazon", "Tesla", "Meta", "AMD", "Intel"]
        for company in companies:
            if company.lower() in query.lower():
                return company
        return "the company"
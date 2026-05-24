"""
Planner Agent - Breaks down user queries into actionable tasks
"""
from typing import Any, Dict, List
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from src.agents.base_agent import BaseAgent
from src.utils.logger import log_agent_io
import json


class Task(BaseModel):
    """Individual task model"""
    task_id: str = Field(description="Unique task identifier")
    description: str = Field(description="Task description")
    agent_type: str = Field(description="Type of agent needed")
    priority: int = Field(description="Task priority (1-5)")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    required_data: List[str] = Field(default_factory=list, description="Required data sources")


class ExecutionPlan(BaseModel):
    """Complete execution plan"""
    original_query: str = Field(description="Original user query")
    intent: str = Field(description="Detected user intent")
    tasks: List[Task] = Field(description="List of tasks to execute")
    parallel_groups: List[List[str]] = Field(description="Groups of tasks that can run in parallel")
    final_synthesis: str = Field(description="How to combine results")


class PlannerAgent(BaseAgent):
    """Agent responsible for planning the execution workflow"""
    
    def __init__(self, llm: ChatGroq = None):
        super().__init__(
            name="PlannerAgent",
            description="Analyzes user queries and creates execution plans",
            llm=llm
        )
        self.output_parser = PydanticOutputParser(pydantic_object=ExecutionPlan)
        self.planning_prompt = (
            "You are a financial research planning expert.\n\n"
            "Analyze user investment questions and create structured execution plans.\n\n"
            "Available specialized agents:\n"
            "1. SECRetrievalAgent - Fetches and analyzes SEC filings\n"
            "2. FinancialMetricsAgent - Calculates financial KPIs\n"
            "3. NewsResearchAgent - Searches latest market news\n"
            "4. RiskAnalysisAgent - Identifies investment risks\n"
            "5. CompetitorAnalysisAgent - Compares company with competitors\n"
            "6. ReportWriterAgent - Generates investment memos\n\n"
            "Create plans that maximize parallel execution while respecting dependencies.\n\n"
            "{format_instructions}"
        )
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user query and create execution plan"""
        query = input_data.get("query", "")
        
        formatted_system_prompt = self.planning_prompt.format(
            format_instructions=self.output_parser.get_format_instructions()
        )
        prompt_messages = [
            SystemMessage(content=formatted_system_prompt),
            HumanMessage(content=query),
        ]
        
        # Get planning response
        log_agent_io(self.name, "input", {"query": query})
        response = await self.llm.ainvoke(prompt_messages)
        
        try:
            execution_plan = self.output_parser.parse(response.content)
            output = {
                "success": True,
                "execution_plan": execution_plan.dict(),
                "agent": self.name
            }
            log_agent_io(self.name, "output", output)
            return output
            
        except Exception as e:
            # Fallback planning
            output = {
                "success": True,
                "execution_plan": self._create_fallback_plan(query),
                "agent": self.name
            }
            log_agent_io(self.name, "output", output, {"fallback": True, "error": str(e)})
            return output
    
    def _create_fallback_plan(self, query: str) -> Dict[str, Any]:
        """Create a default execution plan when parsing fails"""
        return {
            "original_query": query,
            "intent": "investment_analysis",
            "tasks": [
                {
                    "task_id": "T1",
                    "description": "Retrieve SEC filings",
                    "agent_type": "SECRetrievalAgent",
                    "priority": 1,
                    "dependencies": [],
                    "required_data": ["company_name"]
                },
                {
                    "task_id": "T2",
                    "description": "Search latest news",
                    "agent_type": "NewsResearchAgent",
                    "priority": 1,
                    "dependencies": [],
                    "required_data": ["company_name"]
                },
                {
                    "task_id": "T3",
                    "description": "Analyze financial metrics",
                    "agent_type": "FinancialMetricsAgent",
                    "priority": 2,
                    "dependencies": ["T1"],
                    "required_data": ["sec_data"]
                },
                {
                    "task_id": "T4",
                    "description": "Compare competitors",
                    "agent_type": "CompetitorAnalysisAgent",
                    "priority": 2,
                    "dependencies": ["T1"],
                    "required_data": ["company_name"]
                },
                {
                    "task_id": "T5",
                    "description": "Risk analysis",
                    "agent_type": "RiskAnalysisAgent",
                    "priority": 3,
                    "dependencies": ["T1", "T2", "T4"],
                    "required_data": ["sec_data", "news_data", "competitor_data"]
                },
                {
                    "task_id": "T6",
                    "description": "Generate investment report",
                    "agent_type": "ReportWriterAgent",
                    "priority": 4,
                    "dependencies": ["T3", "T5"],
                    "required_data": ["metrics_data", "risk_data"]
                }
            ],
            "parallel_groups": [
                ["T1", "T2"],
                ["T3", "T4"],
                ["T5"],
                ["T6"]
            ],
            "final_synthesis": "Combine all analyses into comprehensive investment recommendation"
        }
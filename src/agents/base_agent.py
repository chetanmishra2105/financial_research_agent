"""
Base agent class with REACT pattern implementation
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import BaseTool
from src.utils.logger import logger, log_input, log_output
from config.settings import settings
import time
from datetime import datetime


class BaseAgent(ABC):
    """Abstract base class for all specialized agents"""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm: Optional[ChatGroq] = None,
        tools: Optional[List[BaseTool]] = None,
        verbose: bool = False
    ):
        self.name = name
        self.description = description
        self.llm = llm or ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
        self.tools = tools or []
        self.verbose = verbose
        self.execution_history: List[Dict[str, Any]] = []
        
        # REACT Prompt Template
        self.system_prompt = self._get_react_template()
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )
        
    def _get_react_template(self) -> str:
        """REACT framework template"""
        tool_names = ", ".join(tool.name for tool in self.tools) if self.tools else ""
        tools_description = "\n".join(
            f"{tool.name}: {getattr(tool, 'description', 'No description available')}"
            for tool in self.tools
        ) if self.tools else "No tools available."

        return f"""You are {self.name}, {self.description}

You have access to the following tools:
{tools_description}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!"""
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results"""
        pass
    
    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute agent with REACT pattern
        
        Args:
            query: Input query string
            
        Returns:
            Dictionary containing execution results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Agent {self.name} starting execution")
            log_input(f"{self.name}.execute", {"query": query})
            
            result = await self.agent.ainvoke({"input": query})
            
            execution_time = time.time() - start_time
            
            # Record execution history
            execution_record = {
                "agent": self.name,
                "query": query,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(execution_record)
            
            logger.info(f"Agent {self.name} completed in {execution_time:.2f}s")

            output = ""
            intermediate_steps = []
            if isinstance(result, dict):
                output = result.get("output", result.get("text", ""))
                intermediate_steps = result.get("intermediate_steps", [])
            else:
                output = str(result)
            
            log_output(
                f"{self.name}.execute",
                {
                    "success": True,
                    "output": output,
                    "intermediate_steps": intermediate_steps,
                    "execution_time": execution_time
                },
            )
            
            return {
                "success": True,
                "agent": self.name,
                "output": output,
                "intermediate_steps": intermediate_steps,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Agent {self.name} failed: {str(e)}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def add_tool(self, tool: BaseTool) -> None:
        """Add a new tool to the agent"""
        self.tools.append(tool)
        # Recreate agent with new tools
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get agent execution history"""
        return self.execution_history
    
    def __repr__(self) -> str:
        return f"<Agent: {self.name}>"
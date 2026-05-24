"""
LangGraph Workflow Orchestration
"""
import uuid
from pathlib import Path
from typing import Any, Dict, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.graph import Graph
import operator
from src.utils.logger import logger
import asyncio


def _keep_last_value(_: Any, value: Any) -> Any:
    return value


class WorkflowState(TypedDict):
    """State for the workflow graph"""
    query: Annotated[str, _keep_last_value]
    messages: Annotated[list[str], operator.add]
    execution_plan: Annotated[Dict[str, Any], _keep_last_value]
    sec_data: Annotated[Dict[str, Any], operator.or_]
    news_data: Annotated[Dict[str, Any], operator.or_]
    metrics_data: Annotated[Dict[str, Any], operator.or_]
    competitor_data: Annotated[Dict[str, Any], operator.or_]
    risk_data: Annotated[Dict[str, Any], operator.or_]
    final_report: Annotated[Dict[str, Any], operator.or_]
    current_step: Annotated[str, _keep_last_value]
    errors: Annotated[list[str], operator.add]


class FinancialResearchWorkflow:
    """
    LangGraph-based workflow orchestrator
    
    Controls the execution flow:
    START → Planner → Parallel Agents → Risk Analysis → Report Writer → END
    """
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.memory = MemorySaver()
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create and preserve the original state graph
        workflow = StateGraph(WorkflowState)
        self.state_graph = workflow
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("sec_agent", self._sec_agent_node)
        workflow.add_node("news_agent", self._news_agent_node)
        workflow.add_node("metrics_agent", self._metrics_agent_node)
        workflow.add_node("competitor_agent", self._competitor_agent_node)
        workflow.add_node("risk_agent", self._risk_agent_node)
        workflow.add_node("report_writer", self._report_writer_node)
        
        # Add edges
        workflow.set_entry_point("planner")
        
        # Planner routes to parallel agents
        workflow.add_conditional_edges(
            "planner",
            self._route_after_planning
        )
        
        # All parallel agents converge to risk agent
        workflow.add_edge("sec_agent", "risk_agent")
        workflow.add_edge("news_agent", "risk_agent")
        workflow.add_edge("metrics_agent", "risk_agent")
        workflow.add_edge("competitor_agent", "risk_agent")
        
        # Risk agent to report writer
        workflow.add_edge("risk_agent", "report_writer")
        workflow.add_edge("report_writer", END)
        
        # Compile with memory and keep the original state graph for visualization
        return workflow.compile(checkpointer=self.memory)
    
    async def _planner_node(self, state: WorkflowState) -> WorkflowState:
        """Planner agent node"""
        logger.info("Executing planner agent...")
        
        planner = self.agents["planner"]
        result = await planner.process({"query": state["query"]})
        
        state["execution_plan"] = result.get("execution_plan", {})
        state["current_step"] = "planning_complete"
        state["messages"].append(f"Created execution plan with {len(result.get('execution_plan', {}).get('tasks', []))} tasks")
        
        return state
    
    async def _sec_agent_node(self, state: WorkflowState) -> WorkflowState:
        """SEC retrieval agent node"""
        logger.info("Executing SEC agent...")
        
        try:
            sec_agent = self.agents["sec_agent"]
            company = self._extract_company(state["query"])
            result = await sec_agent.process({"company": company})
            state["sec_data"] = result
            
            if result.get("success"):
                state["messages"].append("SEC filings retrieved and analyzed")
            else:
                state["errors"].append(f"SEC agent error: {result.get('error')}")
                
        except Exception as e:
            state["errors"].append(f"SEC agent failed: {str(e)}")
            
        return state
    
    async def _news_agent_node(self, state: WorkflowState) -> WorkflowState:
        """News research agent node"""
        logger.info("Executing news agent...")
        
        try:
            news_agent = self.agents["news_agent"]
            company = self._extract_company(state["query"])
            result = await news_agent.process({"company": company})
            state["news_data"] = result
            
            if result.get("success"):
                state["messages"].append("Latest news retrieved")
            else:
                state["errors"].append(f"News agent error: {result.get('error')}")
                
        except Exception as e:
            state["errors"].append(f"News agent failed: {str(e)}")
            
        return state
    
    async def _metrics_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Financial metrics agent node"""
        logger.info("Executing metrics agent...")
        
        try:
            metrics_agent = self.agents["metrics_agent"]
            company = self._extract_company(state["query"])
            result = await metrics_agent.process({
                "company": company,
                "sec_data": state.get("sec_data", {})
            })
            state["metrics_data"] = result
            
            if result.get("success"):
                state["messages"].append("Financial metrics calculated")
            else:
                state["errors"].append(f"Metrics agent error: {result.get('error')}")
                
        except Exception as e:
            state["errors"].append(f"Metrics agent failed: {str(e)}")
            
        return state
    
    async def _competitor_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Competitor analysis agent node"""
        logger.info("Executing competitor agent...")
        
        try:
            competitor_agent = self.agents["competitor_agent"]
            company = self._extract_company(state["query"])
            result = await competitor_agent.process({"company": company})
            state["competitor_data"] = result
            
            if result.get("success"):
                state["messages"].append("Competitor analysis completed")
            else:
                state["errors"].append(f"Competitor agent error: {result.get('error')}")
                
        except Exception as e:
            state["errors"].append(f"Competitor agent failed: {str(e)}")
            
        return state
    
    async def _risk_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Risk analysis agent node"""
        logger.info("Executing risk analysis agent...")
        
        try:
            risk_agent = self.agents["risk_agent"]
            result = await risk_agent.process({
                "sec_data": state.get("sec_data", {}),
                "news_data": state.get("news_data", {}),
                "metrics_data": state.get("metrics_data", {}),
                "competitor_data": state.get("competitor_data", {})
            })
            state["risk_data"] = result
            
            if result.get("success"):
                state["messages"].append("Risk analysis completed")
            else:
                state["errors"].append(f"Risk agent error: {result.get('error')}")
                
        except Exception as e:
            state["errors"].append(f"Risk agent failed: {str(e)}")
            
        return state
    
    async def _report_writer_node(self, state: WorkflowState) -> WorkflowState:
        """Report writer agent node"""
        logger.info("Generating final report...")
        
        try:
            report_writer = self.agents["report_writer"]
            result = await report_writer.process({
                "query": state["query"],
                "sec_data": state.get("sec_data", {}),
                "news_data": state.get("news_data", {}),
                "metrics_data": state.get("metrics_data", {}),
                "competitor_data": state.get("competitor_data", {}),
                "risk_data": state.get("risk_data", {})
            })
            state["final_report"] = result
            
            if result.get("success"):
                state["messages"].append("Final investment report generated")
            else:
                state["errors"].append(f"Report writer error: {result.get('error')}")
                
        except Exception as e:
            state["errors"].append(f"Report writer failed: {str(e)}")
            
        return state
    
    def _route_after_planning(self, state: WorkflowState) -> list[str] | str:
        """Determine next step after planning"""
        if state.get("errors") and len(state["errors"]) > 0:
            return END
        return ["sec_agent", "news_agent", "metrics_agent", "competitor_agent"]
    
    def _extract_company(self, query: str) -> str:
        """Extract company name from query"""
        # Simple extraction - can be enhanced with NER
        company_keywords = [
            "NVIDIA", "Apple", "Microsoft", "Google", "Amazon",
            "Tesla", "Meta", "AMD", "Intel"
        ]
        
        for company in company_keywords:
            if company.lower() in query.lower():
                return company
                
        return "Unknown"
    
    async def execute(self, query: str) -> Dict[str, Any]:
        """Execute the complete workflow"""
        logger.info(f"Starting workflow for query: {query}")
        
        initial_state = WorkflowState(
            query=query,
            messages=[],
            execution_plan={},
            sec_data={},
            news_data={},
            metrics_data={},
            competitor_data={},
            risk_data={},
            final_report={},
            current_step="start",
            errors=[]
        )
        
        try:
            # Execute workflow
            final_state = await self.workflow.ainvoke(
                initial_state,
                config={
                    "thread_id": "financial_research_workflow",
                    "checkpoint_ns": "workflow",
                    "checkpoint_id": str(uuid.uuid4())
                }
            )
            
            return {
                "success": True,
                "query": query,
                "execution_plan": final_state.get("execution_plan", {}),
                "final_report": final_state.get("final_report", {}),
                "execution_steps": final_state.get("messages", []),
                "errors": final_state.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "final_report": {}
            }

    def _create_render_graph(self) -> Graph:
        """Create a renderable graph with explicit branch edges."""
        render_graph = Graph()

        node_names = ["__start__"] + list(self.state_graph.nodes.keys()) + ["__end__"]
        for node_name in node_names:
            render_graph.add_node(None, node_name)

        for source, target in self.state_graph.edges:
            render_graph.add_edge(render_graph.nodes[source], render_graph.nodes[target])

        next_nodes = self._route_after_planning({"errors": []})
        if isinstance(next_nodes, list):
            for target in next_nodes:
                if target in render_graph.nodes:
                    render_graph.add_edge(
                        render_graph.nodes["planner"],
                        render_graph.nodes[target],
                        conditional=True
                    )

        return render_graph

    def save_graph(self, output_dir: str = "./graphs") -> Dict[str, str]:
        """Save the workflow graph image and diagram files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        graph = self._create_render_graph()
        paths: Dict[str, str] = {}

        try:
            png_path = output_path / "workflow_graph.png"
            with open(png_path, "wb") as f:
                f.write(graph.draw_mermaid_png())
            paths["png"] = str(png_path)
        except Exception as exc:
            logger.error(f"Failed to save workflow graph PNG: {str(exc)}")

        try:
            mermaid_path = output_path / "workflow_graph.mmd"
            with open(mermaid_path, "w", encoding="utf-8") as f:
                f.write(graph.draw_mermaid())
            paths["mmd"] = str(mermaid_path)
        except Exception as exc:
            logger.error(f"Failed to save workflow Mermaid diagram: {str(exc)}")

        try:
            ascii_path = output_path / "workflow_graph.txt"
            with open(ascii_path, "w", encoding="utf-8") as f:
                f.write(graph.draw_ascii())
            paths["ascii"] = str(ascii_path)
        except Exception as exc:
            logger.error(f"Failed to save workflow ASCII diagram: {str(exc)}")

        return paths


if __name__ == "__main__":
    class DummyAgent:
        async def process(self, *args, **kwargs):
            return {"success": True}

    agents = {
        "planner": DummyAgent(),
        "sec_agent": DummyAgent(),
        "news_agent": DummyAgent(),
        "metrics_agent": DummyAgent(),
        "competitor_agent": DummyAgent(),
        "risk_agent": DummyAgent(),
        "report_writer": DummyAgent()
    }

    workflow = FinancialResearchWorkflow(agents)
    saved_paths = workflow.save_graph("./graphs")
    logger.info(f"Saved workflow graph files: {saved_paths}")
"""
LangGraph Supervisor - Controls agent execution flow
"""
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.utils.logger import logger
import asyncio
from datetime import datetime


class Supervisor:
    """
    Supervisor agent that manages workflow execution
    
    Responsible for:
    - Task distribution
    - Error handling
    - Retry logic
    - Progress monitoring
    - Resource management
    """
    
    def __init__(self, workflow=None):
        self.workflow = workflow
        self.memory = MemorySaver()
        self.execution_history: List[Dict[str, Any]] = []
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        
    async def execute_workflow(self, query: str) -> Dict[str, Any]:
        """
        Execute the complete workflow under supervision
        
        Args:
            query: User's research query
            
        Returns:
            Complete workflow results
        """
        job_id = f"JOB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"Supervisor starting job {job_id}")
        
        self.active_jobs[job_id] = {
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "query": query
        }
        
        try:
            if self.workflow:
                result = await self.workflow.execute(query)
            else:
                result = await self._execute_fallback(query)
            
            self.active_jobs[job_id]["status"] = "completed"
            self.active_jobs[job_id]["end_time"] = datetime.now().isoformat()
            self.active_jobs[job_id]["result"] = result
            
            self.execution_history.append({
                "job_id": job_id,
                "query": query,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "job_id": job_id,
                "success": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            
            self.active_jobs[job_id]["status"] = "failed"
            self.active_jobs[job_id]["error"] = str(e)
            
            self.execution_history.append({
                "job_id": job_id,
                "query": query,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "job_id": job_id,
                "success": False,
                "error": str(e)
            }
    
    async def _execute_fallback(self, query: str) -> Dict[str, Any]:
        """Fallback execution when workflow is not available"""
        logger.warning("Using fallback execution")
        
        # Import agents dynamically to avoid circular imports
        from src.agents.planner_agent import PlannerAgent
        
        planner = PlannerAgent()
        plan = await planner.process({"query": query})
        
        return {
            "execution_plan": plan,
            "message": "Fallback execution completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        return self.active_jobs.get(job_id)
    
    def get_active_jobs(self) -> List[str]:
        """Get list of active job IDs"""
        return [
            job_id for job_id, job in self.active_jobs.items()
            if job["status"] == "running"
        ]
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history
    
    async def retry_job(self, job_id: str) -> Dict[str, Any]:
        """Retry a failed job"""
        job = self.active_jobs.get(job_id)
        if job and job["status"] == "failed":
            return await self.execute_workflow(job["query"])
        return {"success": False, "error": "Job not found or not in failed state"}
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["status"] = "cancelled"
            return True
        return False
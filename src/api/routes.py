"""
FastAPI Routes for Financial Research Assistant
"""
from datetime import datetime
from fastapi import APIRouter, FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any
from src.api.schemas import (
    ResearchRequest,
    ResearchResponse,
    CompanyAnalysisRequest,
    ErrorResponse
)
from src.orchestrator.workflow import FinancialResearchWorkflow
from src.utils.logger import logger
import uuid


def _summarize_execution_plan(plan: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if not plan or not isinstance(plan, dict):
        return None
    if "original_query" in plan:
        tasks = plan.get("tasks", []) if isinstance(plan.get("tasks"), list) else []
        return {
            "intent": plan.get("intent", "investment_analysis"),
            "total_tasks": len(tasks),
            "parallel_groups": plan.get("parallel_groups", []),
            "estimated_time": plan.get("estimated_time", max(1, len(tasks) * 10))
        }
    tasks = plan.get("tasks", []) if isinstance(plan.get("tasks"), list) else []
    return {
        "intent": plan.get("intent", "investment_analysis"),
        "total_tasks": plan.get("total_tasks", len(tasks)),
        "parallel_groups": plan.get("parallel_groups", []),
        "estimated_time": plan.get("estimated_time", max(1, len(tasks) * 10))
    }

router = APIRouter(prefix="/api/v1", tags=["financial-research"])

app = FastAPI(
    title="AI Financial Research Assistant API",
    version="1.0.0",
    description="API for orchestrating financial research workflows"
)

# In-memory job storage (use Redis in production)
jobs = {}


@router.post("/research", response_model=ResearchResponse)
async def conduct_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Conduct comprehensive financial research
    
    Example:
    POST /api/v1/research
    {
    "query": "Should I invest in NVIDIA for long-term growth?",
    "include_news": true,
    "include_competitors": true
    }
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize workflow
        workflow = get_workflow()
        
        # Execute research
        result = await workflow.execute(request.query)
        created_at = datetime.utcnow().isoformat() + "Z"
        
        if result.get("success"):
            report = result.get("final_report") or None
            execution_plan = _summarize_execution_plan(result.get("execution_plan"))
            return {
                "job_id": job_id,
                "status": "completed",
                "query": request.query,
                "report": report,
                "execution_plan": execution_plan,
                "task_results": None,
                "execution_time": None,
                "created_at": created_at,
                "completed_at": created_at,
                "error": None
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Research failed")
            )
            
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-company")
async def analyze_company(request: CompanyAnalysisRequest):
    """Analyze a specific company"""
    try:
        workflow = get_workflow()
        result = await workflow.execute(f"Analyze {request.company} investment potential")
        
        return JSONResponse(content={
            "company": request.company,
            "analysis": result.get("final_report", {}),
            "success": result.get("success", False)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():

    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Financial Research Assistant",
        "version": "1.0.0"
    }


def get_workflow() -> FinancialResearchWorkflow:
    """Dependency injection for workflow"""
    # This would be properly initialized with all agents
    # For now, return a placeholder
    from src.agents.planner_agent import PlannerAgent

    agents = {
        "planner": PlannerAgent(),
        # Add other agents here
    }

    return FinancialResearchWorkflow(agents)

app.include_router(router)
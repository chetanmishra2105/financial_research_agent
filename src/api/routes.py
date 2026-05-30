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
from src.agents.planner_agent import PlannerAgent
from src.agents.sec_retrieval_agent import SECRetrievalAgent
from src.agents.financial_metrics_agent import FinancialMetricsAgent
from src.agents.news_agent import NewsResearchAgent
from src.agents.risk_analysis_agent import RiskAnalysisAgent
from src.agents.competitor_agent import CompetitorAnalysisAgent
from src.agents.report_writer_agent import ReportWriterAgent
from src.utils.logger import logger, setup_logging, log_input, log_output
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


@app.on_event("startup")
async def app_startup():
    setup_logging()
    logger.info("FastAPI startup complete and logging configured")

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
        log_input("conduct_research", request.dict())
        
        # Initialize workflow
        workflow = get_workflow()
        logger.info(f"Initialized workflow for request {job_id}")
        
        # Execute research
        result = await workflow.execute(request.query)
        log_output("conduct_research", result)
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
        logger.exception(f"Research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-company")
async def analyze_company(request: CompanyAnalysisRequest):
    log_input("analyze_company", request.dict())
    """Analyze a specific company"""
    try:
        workflow = get_workflow()
        result = await workflow.execute(f"Analyze {request.company} investment potential")
        log_output("analyze_company", result)
        
        return JSONResponse(content={
            "company": request.company,
            "analysis": result.get("final_report", {}),
            "success": result.get("success", False)
        })
        
    except Exception as e:
        logger.exception(f"analyze_company failed: {str(e)}")
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
    agents = {
        "planner": PlannerAgent(),
        "sec_agent": SECRetrievalAgent(),
        "metrics_agent": FinancialMetricsAgent(),
        "news_agent": NewsResearchAgent(),
        "risk_agent": RiskAnalysisAgent(),
        "competitor_agent": CompetitorAnalysisAgent(),
        "report_writer": ReportWriterAgent()
    }
    logger.info("Building FinancialResearchWorkflow with available agents")

    return FinancialResearchWorkflow(agents)

app.include_router(router)
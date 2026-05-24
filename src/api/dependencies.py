"""
FastAPI dependencies for dependency injection
"""
from functools import lru_cache
from typing import Optional
from fastapi import Depends, HTTPException, Header, Request
from config.settings import settings
from src.agents.planner_agent import PlannerAgent
from src.agents.sec_retrieval_agent import SECRetrievalAgent
from src.agents.financial_metrics_agent import FinancialMetricsAgent
from src.agents.news_agent import NewsResearchAgent
from src.agents.risk_analysis_agent import RiskAnalysisAgent
from src.agents.competitor_agent import CompetitorAnalysisAgent
from src.agents.report_writer_agent import ReportWriterAgent
from src.orchestrator.workflow import FinancialResearchWorkflow
from src.orchestrator.state_manager import StateManager
from src.mcp.mcp_server import MCPServerManager
from src.memory.vector_store import VectorStoreManager
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.utils.logger import logger
import redis
import time


# ============ LLM Dependencies ============

@lru_cache()
def get_llm() -> ChatOpenAI:
    """Get cached LLM instance"""
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        api_key=settings.OPENAI_API_KEY
    )


@lru_cache()
def get_embeddings() -> OpenAIEmbeddings:
    """Get cached embeddings instance"""
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        dimensions=settings.EMBEDDING_DIMENSIONS,
        api_key=settings.OPENAI_API_KEY
    )


# ============ Redis Dependencies ============

@lru_cache()
def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client"""
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5
        )
        client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        return None


# ============ Agent Dependencies ============

def get_planner_agent(llm: ChatOpenAI = Depends(get_llm)) -> PlannerAgent:
    """Get planner agent instance"""
    return PlannerAgent(llm=llm)


def get_sec_agent(llm: ChatOpenAI = Depends(get_llm)) -> SECRetrievalAgent:
    """Get SEC retrieval agent instance"""
    return SECRetrievalAgent(llm=llm)


def get_metrics_agent(llm: ChatOpenAI = Depends(get_llm)) -> FinancialMetricsAgent:
    """Get financial metrics agent instance"""
    return FinancialMetricsAgent(llm=llm)


def get_news_agent(llm: ChatOpenAI = Depends(get_llm)) -> NewsResearchAgent:
    """Get news research agent instance"""
    return NewsResearchAgent(llm=llm)


def get_risk_agent(llm: ChatOpenAI = Depends(get_llm)) -> RiskAnalysisAgent:
    """Get risk analysis agent instance"""
    return RiskAnalysisAgent(llm=llm)


def get_competitor_agent(llm: ChatOpenAI = Depends(get_llm)) -> CompetitorAnalysisAgent:
    """Get competitor analysis agent instance"""
    return CompetitorAnalysisAgent(llm=llm)


def get_report_writer_agent(llm: ChatOpenAI = Depends(get_llm)) -> ReportWriterAgent:
    """Get report writer agent instance"""
    return ReportWriterAgent(llm=llm)


# ============ Workflow Dependencies ============

def get_all_agents(
    planner: PlannerAgent = Depends(get_planner_agent),
    sec: SECRetrievalAgent = Depends(get_sec_agent),
    metrics: FinancialMetricsAgent = Depends(get_metrics_agent),
    news: NewsResearchAgent = Depends(get_news_agent),
    risk: RiskAnalysisAgent = Depends(get_risk_agent),
    competitor: CompetitorAnalysisAgent = Depends(get_competitor_agent),
    report_writer: ReportWriterAgent = Depends(get_report_writer_agent)
) -> dict:
    """Get all agent instances"""
    return {
        "planner": planner,
        "sec_agent": sec,
        "metrics_agent": metrics,
        "news_agent": news,
        "risk_agent": risk,
        "competitor_agent": competitor,
        "report_writer": report_writer
    }


@lru_cache()
def get_workflow(agents: dict = Depends(get_all_agents)) -> FinancialResearchWorkflow:
    """Get workflow instance with all agents"""
    return FinancialResearchWorkflow(agents=agents)


# ============ MCP Dependencies ============

@lru_cache()
def get_mcp_manager() -> MCPServerManager:
    """Get MCP server manager"""
    manager = MCPServerManager()
    
    # Register MCP servers here
    from src.mcp.servers.sec_server import SECServer
    from src.mcp.servers.tavily_server import TavilyServer
    from src.mcp.servers.calculator_server import CalculatorServer
    from src.mcp.servers.market_data_server import MarketDataServer
    
    manager.register_server(SECServer())
    manager.register_server(TavilyServer())
    manager.register_server(CalculatorServer())
    manager.register_server(MarketDataServer())
    
    return manager


# ============ Vector Store Dependencies ============

@lru_cache()
def get_vector_store(
    embeddings: OpenAIEmbeddings = Depends(get_embeddings)
) -> VectorStoreManager:
    """Get vector store manager"""
    return VectorStoreManager(embeddings=embeddings)


# ============ State Manager Dependencies ============

@lru_cache()
def get_state_manager(
    redis_client: Optional[redis.Redis] = Depends(get_redis_client)
) -> StateManager:
    """Get state manager instance"""
    return StateManager(redis_client=redis_client)


# ============ Authentication Dependencies ============

async def verify_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> bool:
    """Verify API key for authentication"""
    # Skip auth in development
    if settings.DEBUG:
        return True
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required. Use X-API-Key header."
        )
    
    # Validate API key (implement your logic here)
    valid_keys = [settings.OPENAI_API_KEY]  # Example
    
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return True


# ============ Rate Limiting Dependencies ============

class RateLimiter:
    """Simple rate limiter using Redis"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.requests_limit = settings.RATE_LIMIT_REQUESTS
        self.period = settings.RATE_LIMIT_PERIOD
    
    async def check_rate_limit(self, client_id: str) -> bool:
        """Check if rate limit is exceeded"""
        if not self.redis or settings.DEBUG:
            return True
        
        key = f"rate_limit:{client_id}"
        current = self.redis.get(key)
        
        if current and int(current) >= self.requests_limit:
            return False
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.period)
        pipe.execute()
        
        return True


async def check_rate_limit(
    request: Request,
    redis_client: Optional[redis.Redis] = Depends(get_redis_client)
) -> bool:
    """Rate limiting dependency"""
    limiter = RateLimiter(redis_client)
    client_id = request.client.host if request.client else "unknown"
    
    if not await limiter.check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    
    return True


# ============ Request Logging Dependencies ============

async def log_request(
    request: Request,
    start_time: float = None
) -> None:
    """Log API requests"""
    if start_time is None:
        start_time = time.time()
    
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {request.state.status_code if hasattr(request.state, 'status_code') else 'processing'} "
        f"- Time: {process_time:.3f}s"
    )
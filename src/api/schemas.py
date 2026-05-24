"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ResearchType(str, Enum):
    """Types of financial research"""
    INVESTMENT_ANALYSIS = "investment_analysis"
    COMPANY_DEEP_DIVE = "company_deep_dive"
    COMPETITOR_COMPARISON = "competitor_comparison"
    RISK_ASSESSMENT = "risk_assessment"
    EARNINGS_ANALYSIS = "earnings_analysis"
    MARKET_TREND = "market_trend"


class TimeHorizon(str, Enum):
    """Investment time horizons"""
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class RiskTolerance(str, Enum):
    """Risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


# ============ Request Schemas ============

class ResearchRequest(BaseModel):
    """Main research request schema"""
    query: str = Field(
        ...,
        description="Investment research question",
        min_length=10,
        max_length=500,
        example="Should I invest in NVIDIA for long-term growth?"
    )
    research_type: Optional[ResearchType] = Field(
        default=ResearchType.INVESTMENT_ANALYSIS,
        description="Type of research to conduct"
    )
    time_horizon: Optional[TimeHorizon] = Field(
        default=TimeHorizon.LONG_TERM,
        description="Investment time horizon"
    )
    risk_tolerance: Optional[RiskTolerance] = Field(
        default=RiskTolerance.MODERATE,
        description="Risk tolerance level"
    )
    include_news: bool = Field(
        default=True,
        description="Include latest news in analysis"
    )
    include_competitors: bool = Field(
        default=True,
        description="Include competitor analysis"
    )
    include_financials: bool = Field(
        default=True,
        description="Include financial metrics"
    )
    include_risk_analysis: bool = Field(
        default=True,
        description="Include risk assessment"
    )
    max_results: Optional[int] = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results"
    )
    
    @validator('query')
    def validate_query(cls, v):
        """Validate the query is meaningful"""
        if len(v.strip()) < 10:
            raise ValueError('Query must be at least 10 characters')
        # Remove any potential prompt injection
        v = v.replace('system:', '').replace('ignore:', '')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Should I invest in NVIDIA for long-term growth?",
                "research_type": "investment_analysis",
                "time_horizon": "long_term",
                "risk_tolerance": "moderate",
                "include_news": True,
                "include_competitors": True,
                "include_financials": True,
                "include_risk_analysis": True
            }
        }


class CompanyAnalysisRequest(BaseModel):
    """Company-specific analysis request"""
    company: str = Field(
        ...,
        description="Company name or ticker symbol",
        min_length=1,
        max_length=10,
        example="NVDA"
    )
    analysis_type: ResearchType = Field(
        default=ResearchType.COMPANY_DEEP_DIVE,
        description="Type of analysis"
    )
    competitors: Optional[List[str]] = Field(
        default=None,
        description="List of competitors to compare (optional)"
    )
    fiscal_year: Optional[int] = Field(
        default=None,
        description="Specific fiscal year for analysis"
    )
    
    @validator('company')
    def validate_company(cls, v):
        """Validate company name/ticker"""
        # Convert to uppercase for tickers
        return v.strip().upper()
    
    class Config:
        schema_extra = {
            "example": {
                "company": "NVDA",
                "analysis_type": "company_deep_dive",
                "competitors": ["AMD", "INTC"],
                "fiscal_year": 2024
            }
        }


class CompareCompaniesRequest(BaseModel):
    """Company comparison request"""
    primary_company: str = Field(
        ...,
        description="Primary company to analyze",
        example="AAPL"
    )
    competitors: List[str] = Field(
        ...,
        description="List of competitors to compare",
        min_items=1,
        max_items=5,
        example=["MSFT", "GOOGL", "AMZN"]
    )
    metrics: Optional[List[str]] = Field(
        default=None,
        description="Specific metrics to compare"
    )
    
    @validator('competitors')
    def validate_competitors(cls, v):
        """Ensure no duplicate competitors"""
        if len(v) != len(set(v)):
            raise ValueError('Duplicate competitors not allowed')
        return [comp.strip().upper() for comp in v]
    
    class Config:
        schema_extra = {
            "example": {
                "primary_company": "AAPL",
                "competitors": ["MSFT", "GOOGL", "AMZN"],
                "metrics": ["revenue_growth", "profit_margin", "pe_ratio"]
            }
        }


class EarningsAnalysisRequest(BaseModel):
    """Earnings call analysis request"""
    company: str = Field(..., description="Company name or ticker")
    quarter: Optional[str] = Field(
        default=None,
        description="Quarter (Q1, Q2, Q3, Q4)",
        # regex="^Q[1-4]$"
        pattern="^Q[1-4]$"
    )
    year: Optional[int] = Field(
        default=None,
        description="Fiscal year"
    )
    include_transcript: bool = Field(
        default=True,
        description="Include full transcript analysis"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "company": "NVDA",
                "quarter": "Q4",
                "year": 2024,
                "include_transcript": True
            }
        }


# ============ Response Schemas ============

class TaskResult(BaseModel):
    """Individual task execution result"""
    task_id: str
    task_description: str
    agent_type: str
    status: str
    execution_time: float
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ExecutionPlan(BaseModel):
    """Execution plan details"""
    intent: str
    total_tasks: int
    parallel_groups: List[List[str]]
    estimated_time: int


class FinancialMetrics(BaseModel):
    """Financial metrics data"""
    revenue_growth: Optional[str] = None
    gross_margin: Optional[str] = None
    pe_ratio: Optional[str] = None
    eps_growth: Optional[str] = None
    cash_flow: Optional[str] = None
    debt_to_equity: Optional[str] = None
    return_on_equity: Optional[str] = None
    profit_margin: Optional[str] = None
    market_cap: Optional[str] = None
    dividend_yield: Optional[str] = None


class RiskAssessment(BaseModel):
    """Risk assessment data"""
    risk_name: str
    severity: str  # Low, Medium, High, Critical
    impact: str
    probability: str
    mitigation: Optional[str] = None


class CompetitorData(BaseModel):
    """Competitor analysis data"""
    company_name: str
    market_position: str
    strengths: List[str]
    weaknesses: List[str]
    market_share: Optional[str] = None
    threat_level: str  # Low, Medium, High


class NewsArticle(BaseModel):
    """News article data"""
    title: str
    url: Optional[str] = None
    source: str
    published_date: str
    sentiment: str  # Positive, Negative, Neutral
    relevance_score: float
    summary: Optional[str] = None


class SECFilingData(BaseModel):
    """SEC filing data"""
    filing_type: str  # 10-K, 10-Q, 8-K
    filing_date: str
    company: str
    key_sections: Dict[str, str]
    risk_factors: Optional[List[str]] = None
    financial_highlights: Optional[Dict[str, str]] = None


class InvestmentReport(BaseModel):
    """Final investment report"""
    executive_summary: str
    company_analysis: Dict[str, Any]
    financial_health: FinancialMetrics
    risks: List[RiskAssessment]
    competitors: Optional[List[CompetitorData]] = None
    news_summary: Optional[List[NewsArticle]] = None
    recommendation: str  # BUY, HOLD, SELL
    risk_level: str  # Low, Medium, High
    confidence_score: float
    supporting_evidence: List[str]
    disclaimers: List[str]


class ResearchResponse(BaseModel):
    """Main research response"""
    job_id: str
    status: str  # completed, failed, processing
    query: str
    execution_plan: Optional[ExecutionPlan] = None
    task_results: Optional[List[TaskResult]] = None
    report: Optional[InvestmentReport] = None
    execution_time: Optional[float] = None
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "query": "Should I invest in NVIDIA for long-term growth?",
                "report": {
                    "executive_summary": "NVIDIA shows strong potential...",
                    "recommendation": "BUY",
                    "risk_level": "Medium",
                    "confidence_score": 0.85
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: str
    path: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Query must be at least 10 characters",
                "error_code": "VALIDATION_ERROR",
                "timestamp": "2024-01-15T10:30:00Z",
                "path": "/api/v1/research"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    uptime: float
    active_agents: int
    redis_connected: bool
    chromadb_connected: bool
    timestamp: str


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: float  # 0-100
    current_step: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str


# ============ WebSocket Schemas ============

class WebSocketMessage(BaseModel):
    """WebSocket message schema"""
    type: str  # progress, result, error, log
    data: Dict[str, Any]
    timestamp: str


class ProgressUpdate(BaseModel):
    """Progress update for real-time tracking"""
    job_id: str
    step: str
    progress: float  # 0-100
    message: str
    agent: Optional[str] = None
    timestamp: str


# ============ Pagination Schemas ============

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = None
    # sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


# ============ Agent Configuration Schemas ============

class AgentConfig(BaseModel):
    """Agent configuration"""
    name: str
    type: str
    enabled: bool = True
    priority: int = 1
    max_retries: int = 3
    timeout: int = 300
    tools: List[str] = []
    dependencies: List[str] = []


class MCPToolConfig(BaseModel):
    """MCP tool configuration"""
    name: str
    server: str
    enabled: bool = True
    rate_limit: Optional[int] = None
    cache_ttl: Optional[int] = None


class SystemConfig(BaseModel):
    """System configuration response"""
    version: str
    environment: str
    agents: List[AgentConfig]
    mcp_tools: List[MCPToolConfig]
    llm_model: str
    embedding_model: str
    vector_store: str
"""
Central configuration module for AI Financial Research Assistant
"""
import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Project Info
    PROJECT_NAME: str = "AI Financial Research Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")
    SECRET_KEY: str = Field(default="your_secret_key_here")
    
    # API Keys
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    TAVILY_API_KEY: Optional[str] = Field(default=None, env="TAVILY_API_KEY")
    ALPHA_VANTAGE_API_KEY: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    POLYGON_API_KEY: Optional[str] = Field(default=None, env="POLYGON_API_KEY")
    
    # LLM Configuration
    LLM_MODEL: str = Field(default="mixtral-8x7b-32768")
    LLM_TEMPERATURE: float = Field(default=0.1)
    LLM_MAX_TOKENS: int = Field(default=4000)
    
    # Embeddings
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")
    EMBEDDING_DIMENSIONS: int = Field(default=384)
    
    # Vector Store
    CHROMA_PERSIST_DIR: str = Field(default="./chroma_db")
    CHROMA_COLLECTION_NAME: str = Field(default="financial_research")
    
    # MCP Configuration
    MCP_HOST: str = Field(default="0.0.0.0")
    MCP_PORT: int = Field(default=8000)
    MCP_TRANSPORT: str = Field(default="stdio")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8001)
    API_WORKERS: int = Field(default=4)
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_PERIOD: int = Field(default=60)
    
    # File Storage
    UPLOAD_DIR: str = Field(default="./uploads")
    MAX_UPLOAD_SIZE: int = Field(default=50 * 1024 * 1024)  # 50MB
    
    # Agent Configuration
    MAX_RETRIES: int = Field(default=3)
    AGENT_TIMEOUT: int = Field(default=300)
    MAX_PARALLEL_AGENTS: int = Field(default=5)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow extra fields from .env file
        extra = "allow"
        # Case insensitive environment variables
        case_sensitive = False


settings = Settings()
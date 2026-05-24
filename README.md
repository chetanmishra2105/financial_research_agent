# 📊 AI Financial Research Assistant

Enterprise-level multi-agent AI system for automated financial research and investment analysis.

## 🎯 Overview

This system simulates how real hedge funds and investment banks use AI for:
- Company analysis
- Market intelligence
- Earnings analysis
- Risk evaluation
- Investment memo generation

## 🏗️ Architecture

### Multi-Agent System
- **Planner Agent**: Breaks user queries into tasks
- **SEC Retrieval Agent**: Fetches and analyzes SEC filings
- **Financial Metrics Agent**: Computes KPIs and ratios
- **News Research Agent**: Searches latest market news
- **Risk Analysis Agent**: Identifies investment risks
- **Competitor Agent**: Compares companies
- **Report Writer Agent**: Generates investment memos

### MCP (Model Context Protocol)
Standardized interface for AI agents to discover and use tools:
- Stock API Tool
- Financial Calculator Tool
- PDF Parser Tool
- Web Search Tool (Tavily)
- Earnings Transcript Retriever

### Technology Stack
- **Orchestration**: LangGraph
- **Vector Store**: ChromaDB
- **API**: FastAPI
- **UI**: Streamlit
- **Cache**: Redis
- **Container**: Docker

## 🚀 Quick Start

### Prerequisites
```bash
# Clone repository
git clone <repository-url>
cd ai-financial-research-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys


### # Start API server
### python -m uvicorn src.api.routes:app --reload --port 8001

### # Start Streamlit UI (new terminal)
### streamlit run ui/streamlit_app.py

### # Start Celery worker (new terminal)
### celery -A src.tasks worker --loglevel=info
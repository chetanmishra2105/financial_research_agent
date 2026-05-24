"""
Streamlit UI for AI Financial Research Assistant
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any


# Page configuration
st.set_page_config(
    page_title="AI Financial Research Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main Streamlit application"""
    
    # Header
    st.title("📊 AI Financial Research Assistant")
    st.markdown("""
    *Powered by Multi-Agent AI System*
    
    Get comprehensive investment research, competitor analysis, and risk assessments.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("Research Configuration")
        
        research_type = st.selectbox(
            "Research Type",
            ["Investment Analysis", "Company Deep Dive", "Competitor Comparison", "Risk Assessment"]
        )
        
        include_news = st.checkbox("Include Latest News", value=True)
        include_competitors = st.checkbox("Include Competitor Analysis", value=True)
        include_financials = st.checkbox("Include Financial Metrics", value=True)
        
        st.divider()
        
        # Example queries
        st.subheader("Example Queries")
        examples = [
            "Should I invest in NVIDIA for long-term growth?",
            "Analyze Apple's financial health",
            "Compare AMD vs Intel in AI chip market",
            "What are the risks of investing in Tesla?"
        ]
        
        for example in examples:
            if st.button(example):
                st.session_state.query = example
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Query input
        query = st.text_area(
            "Enter your investment research question:",
            value=st.session_state.get("query", ""),
            height=100,
            placeholder="Example: Should I invest in NVIDIA for long-term growth?"
        )
        
        if st.button("🔍 Start Research", type="primary"):
            if query:
                with st.spinner("🤖 AI agents working on your research..."):
                    result = execute_research(query)
                    display_results(result)
            else:
                st.warning("Please enter a research question")
    
    with col2:
        # Live status updates
        st.subheader("📡 Research Progress")
        if "progress" in st.session_state:
            for step in st.session_state.progress:
                st.write(f"✅ {step}")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>AI Financial Research Assistant v1.0 | Multi-Agent System with MCP Protocol</small>
    </div>
    """, unsafe_allow_html=True)


def execute_research(query: str) -> Dict[str, Any]:
    """Execute research via API"""
    
    # Update progress
    st.session_state.progress = []
    
    try:
        # Call API
        response = requests.post(
            "http://localhost:8001/api/v1/research",
            json={"query": query, "include_news": True, "include_competitors": True}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Research failed: {response.text}")
            return {}
            
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return {}


def display_results(result: Dict[str, Any]):
    """Display research results"""
    
    if not result:
        return
    
    st.success("✅ Research Complete!")
    
    # Create tabs for different sections
    tabs = st.tabs(["📄 Executive Summary", "📊 Financial Analysis", "🏢 Competitors", "⚠️ Risks", "📰 News"])
    
    with tabs[0]:
        st.header("Executive Summary")
        report = result.get("report") or {}
        summary = report.get("executive_summary") or report.get("summary") or "Analysis in progress..."
        st.markdown(summary)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Rating", "BUY", "Strong")
        with col2:
            st.metric("Risk Level", "Moderate", "")
        with col3:
            st.metric("Growth Potential", "High", "+15%")
    
    with tabs[1]:
        st.header("Financial Analysis")
        
        # Sample metrics
        metrics = {
            "Revenue Growth": "+126%",
            "Gross Margin": "74%",
            "PE Ratio": "High",
            "EPS Growth": "Strong",
            "Cash Flow": "Positive"
        }
        
        for metric, value in metrics.items():
            st.metric(metric, value)
    
    with tabs[2]:
        st.header("Competitor Analysis")
        
        # Sample competitor data
        competitors = {
            "NVIDIA": {"strength": "AI Dominance", "weakness": "High Valuation"},
            "AMD": {"strength": "Growing AI Business", "weakness": "Lower Margins"},
            "Intel": {"strength": "Manufacturing Scale", "weakness": "AI Lagging"}
        }
        
        for company, analysis in competitors.items():
            with st.expander(f"🏢 {company}"):
                st.write(f"**Strength:** {analysis['strength']}")
                st.write(f"**Weakness:** {analysis['weakness']}")
    
    with tabs[3]:
        st.header("Risk Assessment")
        
        risks = [
            {"risk": "AI Bubble Risk", "severity": "Medium", "color": "orange"},
            {"risk": "Export Regulations", "severity": "High", "color": "red"},
            {"risk": "Competition", "severity": "Medium", "color": "orange"},
            {"risk": "Valuation Risk", "severity": "High", "color": "red"}
        ]
        
        for risk in risks:
            st.markdown(f"🔴 **{risk['risk']}** - Severity: {risk['severity']}")
    
    with tabs[4]:
        st.header("Latest News")
        
        news_items = [
            {"title": "NVIDIA Signs Major AI Cloud Deals", "sentiment": "Positive", "date": "2024-01-15"},
            {"title": "US Export Restrictions Impact Chip Makers", "sentiment": "Negative", "date": "2024-01-14"},
            {"title": "Global AI Demand Continues to Surge", "sentiment": "Positive", "date": "2024-01-13"}
        ]
        
        for news in news_items:
            sentiment_color = "green" if news["sentiment"] == "Positive" else "red"
            st.markdown(f"""
            <div style='padding: 10px; border-left: 3px solid {sentiment_color}; margin: 5px 0;'>
                <strong>{news['title']}</strong><br>
                <small>Sentiment: <span style='color:{sentiment_color}'>{news['sentiment']}</span> | {news['date']}</small>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
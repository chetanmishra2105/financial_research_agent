import os

# Base project folder
BASE_DIR = "ai-financial-research-assistant"

# Folder structure
structure = {
    "": [
        "README.md",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "docker-compose.yml",
        "Dockerfile",
    ],

    "config": [
        "__init__.py",
        "settings.py",
        "logging_config.py",
        "agent_config.py",
    ],

    "src": [
        "__init__.py",
        "main.py",
    ],

    "src/api": [
        "__init__.py",
        "routes.py",
        "schemas.py",
        "dependencies.py",
    ],

    "src/agents": [
        "__init__.py",
        "base_agent.py",
        "planner_agent.py",
        "sec_retrieval_agent.py",
        "financial_metrics_agent.py",
        "news_agent.py",
        "risk_analysis_agent.py",
        "competitor_agent.py",
        "report_writer_agent.py",
    ],

    "src/mcp": [
        "__init__.py",
        "mcp_server.py",
        "mcp_client.py",
    ],

    "src/mcp/tools": [
        "__init__.py",
        "sec_filing_tool.py",
        "financial_calculator_tool.py",
        "news_search_tool.py",
        "pdf_parser_tool.py",
        "stock_api_tool.py",
    ],

    "src/mcp/servers": [
        "__init__.py",
        "sec_server.py",
        "tavily_server.py",
        "calculator_server.py",
        "chromadb_server.py",
        "market_data_server.py",
    ],

    "src/orchestrator": [
        "__init__.py",
        "workflow.py",
        "supervisor.py",
        "state_manager.py",
    ],

    "src/memory": [
        "__init__.py",
        "vector_store.py",
        "context_manager.py",
        "embeddings.py",
    ],

    "src/data": [
        "__init__.py",
        "sec_processor.py",
        "transcript_processor.py",
        "financial_data_processor.py",
    ],

    "src/utils": [
        "__init__.py",
        "helpers.py",
        "validators.py",
        "formatters.py",
    ],

    "tests": [
        "__init__.py",
        "test_agents.py",
        "test_mcp.py",
        "test_workflow.py",
        "test_api.py",
    ],

    "ui": [
        "__init__.py",
        "streamlit_app.py",
    ],

    "ui/components": [
        "__init__.py",
        "chat_interface.py",
        "report_viewer.py",
        "data_visualizer.py",
    ],

    "scripts": [
        "setup.sh",
        "run_dev.sh",
        "seed_data.py",
    ],
}


def create_project_structure():
    for folder, files in structure.items():
        folder_path = os.path.join(BASE_DIR, folder)

        # Create directory
        os.makedirs(folder_path, exist_ok=True)

        # Create files
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)

            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    pass

    print(f"\nProject structure created successfully: {BASE_DIR}")


if __name__ == "__main__":
    create_project_structure()
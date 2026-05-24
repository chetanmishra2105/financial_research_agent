"""
Main entry point for AI Financial Research Assistant
"""
import uvicorn
import subprocess
import sys
import os
from config.settings import settings
from src.utils.logger import logger, setup_logging


def start_api():
    """Start FastAPI server"""
    logger.info(f"Starting API server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "src.api.routes:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEBUG,
        log_level="info"
    )


def start_streamlit():
    """Start Streamlit UI"""
    logger.info("Starting Streamlit UI on http://localhost:8501")
    subprocess.run([
        "streamlit", "run",
        "ui/streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])


def main():
    """Main entry point"""
    setup_logging()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "api":
            start_api()
        elif command == "ui":
            start_streamlit()
        elif command == "all":
            # Start both API and UI
            from multiprocessing import Process
            api_process = Process(target=start_api)
            ui_process = Process(target=start_streamlit)
            
            api_process.start()
            ui_process.start()
            
            api_process.join()
            ui_process.join()
        else:
            print("Usage: python -m src.main [api|ui|all]")
    else:
        print("AI Financial Research Assistant")
        print("================================")
        print("\nAvailable commands:")
        print("  api  - Start FastAPI server")
        print("  ui   - Start Streamlit UI")
        print("  all  - Start both API and UI")
        print("\nExample: python -m src.main api")


if __name__ == "__main__":
    main()
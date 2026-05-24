"""Shared logging utilities for the AI Financial Research Assistant."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger as _logger
import sys

LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} | {function} | {message}"


def setup_logging(
    log_dir: str = "logs",
    log_file_name: str = "financial_research.log",
    level: str = "INFO"
) -> None:
    """Configure the shared logger and enable file+console output."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    _logger.remove()
    _logger.add(
        sys.stderr,
        level=level,
        format=LOG_FORMAT,
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )
    _logger.add(
        str(log_path / log_file_name),
        rotation="500 MB",
        retention="10 days",
        level=level,
        format=LOG_FORMAT,
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )


def log_input(
    function_name: str,
    input_data: Any,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a function input payload."""
    _logger.info(
        f"[INPUT] {function_name} | context={context or {}} | payload={input_data}"
    )


def log_output(
    function_name: str,
    output_data: Any,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a function output payload."""
    _logger.info(
        f"[OUTPUT] {function_name} | context={context or {}} | result={output_data}"
    )


def log_agent_io(
    agent_name: str,
    stage: str,
    payload: Any,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Log structured agent input/output details."""
    _logger.info(
        f"[AGENT] {agent_name} | stage={stage} | extra={extra or {}} | payload={payload}"
    )


def log_vector_store(
    action: str,
    collection_name: str,
    details: Any,
) -> None:
    """Log vector store actions and retrieved information."""
    _logger.info(
        f"[VECTOR_STORE] action={action} | collection={collection_name} | details={details}"
    )


def log_mcp_action(
    action: str,
    server_name: str,
    tool_name: Optional[str] = None,
    arguments: Optional[Dict[str, Any]] = None,
    result: Optional[Any] = None,
) -> None:
    """Log MCP actions at the client/server boundary."""
    _logger.info(
        f"[MCP] action={action} | server={server_name} | tool={tool_name} | arguments={arguments} | result={result}"
    )


logger = _logger

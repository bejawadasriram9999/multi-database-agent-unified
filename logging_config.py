"""
Logging configuration for Multi-Database Agent
Provides structured logging with different handlers for different environments.
"""

import os
import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class DatabaseOperationFilter(logging.Filter):
    """Filter to add database operation context to logs."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add database context to log records."""
        # Add database operation context if not already present
        if not hasattr(record, 'database'):
            record.database = 'unknown'
        if not hasattr(record, 'operation'):
            record.operation = 'unknown'
        if not hasattr(record, 'query_type'):
            record.query_type = 'unknown'
        
        return True

def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    enable_console: bool = True,
    enable_file: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Setup logging configuration for the multi-database agent.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: logs/multi_db_agent.log)
        enable_console: Enable console logging
        enable_file: Enable file logging
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
    """
    
    # Create logs directory if it doesn't exist
    if enable_file and log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    elif enable_file:
        os.makedirs("logs", exist_ok=True)
        log_file = "logs/multi_db_agent.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    json_formatter = JSONFormatter()
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(DatabaseOperationFilter())
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file and log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(json_formatter)
        file_handler.addFilter(DatabaseOperationFilter())
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_logger_levels()
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized", extra={
        "log_level": log_level,
        "log_file": log_file,
        "console_enabled": enable_console,
        "file_enabled": enable_file
    })

def configure_logger_levels():
    """Configure specific logger levels for different components."""
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Set specific levels for our components
    logging.getLogger("mongodb_agent").setLevel(logging.INFO)
    logging.getLogger("mcp_servers").setLevel(logging.INFO)
    logging.getLogger("database_router").setLevel(logging.INFO)

def log_database_operation(
    operation: str,
    database: str,
    query_type: str,
    success: bool,
    execution_time: float = None,
    error: str = None,
    **kwargs
) -> None:
    """
    Log a database operation with structured information.
    
    Args:
        operation: The operation being performed
        database: Database name (MongoDB, Oracle, etc.)
        query_type: Type of query (SELECT, INSERT, etc.)
        success: Whether the operation was successful
        execution_time: Time taken to execute the operation
        error: Error message if operation failed
        **kwargs: Additional context information
    """
    
    logger = logging.getLogger("database_operations")
    
    log_data = {
        "operation": operation,
        "database": database,
        "query_type": query_type,
        "success": success,
        "execution_time": execution_time,
        "error": error,
        **kwargs
    }
    
    if success:
        logger.info(f"Database operation completed: {operation}", extra=log_data)
    else:
        logger.error(f"Database operation failed: {operation}", extra=log_data)

def log_agent_interaction(
    user_query: str,
    agent_response: str,
    database_used: str,
    confidence_score: float,
    execution_time: float = None,
    **kwargs
) -> None:
    """
    Log an agent interaction with structured information.
    
    Args:
        user_query: The user's query
        agent_response: The agent's response
        database_used: Database that was queried
        confidence_score: Confidence score for database routing
        execution_time: Time taken to process the query
        **kwargs: Additional context information
    """
    
    logger = logging.getLogger("agent_interactions")
    
    log_data = {
        "user_query": user_query,
        "agent_response": agent_response,
        "database_used": database_used,
        "confidence_score": confidence_score,
        "execution_time": execution_time,
        **kwargs
    }
    
    logger.info("Agent interaction completed", extra=log_data)

def log_security_event(
    event_type: str,
    severity: str,
    user_ip: str = None,
    user_agent: str = None,
    details: Dict[str, Any] = None
) -> None:
    """
    Log a security-related event.
    
    Args:
        event_type: Type of security event
        severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        user_ip: User's IP address
        user_agent: User's browser/agent string
        details: Additional event details
    """
    
    logger = logging.getLogger("security")
    
    log_data = {
        "event_type": event_type,
        "severity": severity,
        "user_ip": user_ip,
        "user_agent": user_agent,
        "details": details or {}
    }
    
    if severity.upper() in ["HIGH", "CRITICAL"]:
        logger.error(f"Security event: {event_type}", extra=log_data)
    else:
        logger.warning(f"Security event: {event_type}", extra=log_data)

# Initialize logging on import
if __name__ != "__main__":
    # Setup logging based on environment variables
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")
    enable_console = os.getenv("ENABLE_CONSOLE_LOGGING", "TRUE").upper() == "TRUE"
    enable_file = os.getenv("ENABLE_FILE_LOGGING", "TRUE").upper() == "TRUE"
    
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        enable_console=enable_console,
        enable_file=enable_file
    )

"""
LVL-CODES: Logging Configuration
================================================================================
This module provides a centralized logging configuration for the entire
application. It uses the loguru library for enhanced logging capabilities.

Features:
    - Structured logging with JSON support
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File rotation and retention
    - Console and file output
    - Contextual logging with metadata
    - Performance timing decorators

Usage:
    from src.utils.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Starting forecasting process", extra={"model": "SARIMA"})

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps
import time
from datetime import datetime

from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Log level from environment (default: INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Log file path
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "./logs/lvl_codes.log")

# Create logs directory if it doesn't exist
LOG_DIR = Path(LOG_FILE_PATH).parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Environment (development, staging, production)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ============================================================================
# LOG FORMAT TEMPLATES
# ============================================================================

# Detailed format for file logging
DETAILED_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level> | "
    "{extra}"
)

# Simple format for console logging
CONSOLE_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)

# JSON format for structured logging (production)
JSON_FORMAT = (
    '{{"timestamp": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
    '"level": "{level}", '
    '"module": "{name}", '
    '"function": "{function}", '
    '"line": {line}, '
    '"message": "{message}", '
    '"extra": {extra}}}'
)


# ============================================================================
# LOGGER CONFIGURATION
# ============================================================================

def configure_logger() -> None:
    """
    Configure the global logger with appropriate handlers and formats.

    This function:
        1. Removes default logger
        2. Adds console handler with colorized output
        3. Adds file handler with rotation
        4. Adds error-specific file handler
        5. Configures JSON logging for production

    Returns:
        None
    """
    # Remove default logger
    logger.remove()

    # ========================================================================
    # CONSOLE HANDLER (colorized output for development)
    # ========================================================================
    if ENVIRONMENT == "development":
        logger.add(
            sys.stderr,
            format=CONSOLE_FORMAT,
            level=LOG_LEVEL,
            colorize=True,
            backtrace=True,  # Show traceback on errors
            diagnose=True,   # Show variable values in traceback
        )
    else:
        # Production: simpler console output
        logger.add(
            sys.stderr,
            format=CONSOLE_FORMAT,
            level="INFO",  # Only INFO and above in production console
            colorize=False,
        )

    # ========================================================================
    # FILE HANDLER (main application log with rotation)
    # ========================================================================
    logger.add(
        LOG_FILE_PATH,
        format=DETAILED_FORMAT if ENVIRONMENT == "development" else JSON_FORMAT,
        level=LOG_LEVEL,
        rotation="100 MB",  # Rotate when file reaches 100MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip",    # Compress rotated logs
        backtrace=True,
        diagnose=True if ENVIRONMENT == "development" else False,
        enqueue=True,  # Thread-safe logging
    )

    # ========================================================================
    # ERROR FILE HANDLER (separate file for errors and above)
    # ========================================================================
    error_log_path = LOG_FILE_PATH.replace(".log", "_errors.log")
    logger.add(
        error_log_path,
        format=DETAILED_FORMAT if ENVIRONMENT == "development" else JSON_FORMAT,
        level="ERROR",  # Only ERROR and CRITICAL
        rotation="50 MB",
        retention="90 days",  # Keep error logs longer
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    # ========================================================================
    # PERFORMANCE LOG (for timing and performance metrics)
    # ========================================================================
    perf_log_path = LOG_FILE_PATH.replace(".log", "_performance.log")
    logger.add(
        perf_log_path,
        format=DETAILED_FORMAT,
        level="DEBUG",
        rotation="50 MB",
        retention="7 days",
        filter=lambda record: "performance" in record["extra"],
        enqueue=True,
    )

    logger.info(f"Logger configured for {ENVIRONMENT} environment at level {LOG_LEVEL}")


# Configure logger on module import
configure_logger()


# ============================================================================
# LOGGER FACTORY
# ============================================================================

def get_logger(name: str) -> logger:
    """
    Get a logger instance with the specified name.

    This is the primary way to obtain a logger in the application.
    The name typically corresponds to the module name (__name__).

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> from src.utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    return logger.bind(module=name)


# ============================================================================
# CONTEXT MANAGER FOR SCOPED LOGGING
# ============================================================================

class LogContext:
    """
    Context manager for adding contextual information to logs.

    This allows you to add metadata that will be included in all logs
    within the context block.

    Example:
        >>> with LogContext(model="SARIMA", year=2026):
        >>>     logger.info("Training model")  # Will include model and year
    """

    def __init__(self, **kwargs):
        """
        Initialize context with key-value pairs.

        Args:
            **kwargs: Key-value pairs to add to log context
        """
        self.context = kwargs
        self.token = None

    def __enter__(self):
        """Enter the context and bind the metadata."""
        self.token = logger.contextualize(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        # Context is automatically removed by loguru
        pass


# ============================================================================
# PERFORMANCE TIMING DECORATOR
# ============================================================================

def log_execution_time(func_name: Optional[str] = None):
    """
    Decorator to log function execution time.

    This decorator measures and logs the execution time of a function,
    which is useful for performance monitoring and optimization.

    Args:
        func_name: Optional custom name for the function (defaults to actual name)

    Returns:
        Decorated function

    Example:
        >>> @log_execution_time()
        >>> def train_model(data):
        >>>     # Training logic
        >>>     pass
        >>> train_model(df)
        # Logs: "Function train_model executed in 12.34 seconds"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use custom name or function name
            name = func_name or func.__name__

            # Record start time
            start_time = time.perf_counter()

            # Log function start
            logger.debug(f"Starting {name}", performance=True)

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Calculate execution time
                execution_time = time.perf_counter() - start_time

                # Log success with timing
                logger.info(
                    f"Function {name} completed successfully in {execution_time:.2f} seconds",
                    extra={"performance": True, "execution_time": execution_time}
                )

                return result

            except Exception as e:
                # Calculate execution time even on error
                execution_time = time.perf_counter() - start_time

                # Log failure with timing
                logger.error(
                    f"Function {name} failed after {execution_time:.2f} seconds: {str(e)}",
                    extra={"performance": True, "execution_time": execution_time}
                )

                # Re-raise the exception
                raise

        return wrapper
    return decorator


# ============================================================================
# STEP LOGGING DECORATOR
# ============================================================================

def log_step(step_name: str):
    """
    Decorator to log individual steps in a process.

    Useful for tracking progress through multi-step operations like
    ETL pipelines or model training workflows.

    Args:
        step_name: Name of the step being executed

    Returns:
        Decorated function

    Example:
        >>> @log_step("Data Extraction")
        >>> def extract_data():
        >>>     pass
        # Logs: "=== Starting: Data Extraction ==="
        # Logs: "=== Completed: Data Extraction ==="
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"{'='*60}")
            logger.info(f"=== Starting: {step_name} ===")
            logger.info(f"{'='*60}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"✓ Completed: {step_name}")
                return result

            except Exception as e:
                logger.error(f"✗ Failed: {step_name} - {str(e)}")
                raise

        return wrapper
    return decorator


# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

def log_exception(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    critical: bool = False
) -> None:
    """
    Log an exception with optional context.

    Args:
        exception: The exception to log
        context: Optional dictionary of contextual information
        critical: If True, log as CRITICAL instead of ERROR

    Example:
        >>> try:
        >>>     risky_operation()
        >>> except Exception as e:
        >>>     log_exception(e, context={"user_id": 123})
    """
    level = "CRITICAL" if critical else "ERROR"

    log_message = f"Exception occurred: {type(exception).__name__}: {str(exception)}"

    if context:
        logger.log(level, log_message, extra=context)
    else:
        logger.log(level, log_message)


# ============================================================================
# PROGRESS TRACKING
# ============================================================================

class ProgressLogger:
    """
    Logger for tracking progress of long-running operations.

    Example:
        >>> progress = ProgressLogger("Processing SKUs", total=1000)
        >>> for i, sku in enumerate(skus):
        >>>     process_sku(sku)
        >>>     progress.update(i + 1)
    """

    def __init__(self, task_name: str, total: int, log_every: int = 10):
        """
        Initialize progress logger.

        Args:
            task_name: Name of the task being tracked
            total: Total number of items to process
            log_every: Log progress every N percent (default: 10)
        """
        self.task_name = task_name
        self.total = total
        self.log_every = log_every
        self.start_time = time.perf_counter()
        self.last_logged_percent = 0

        logger.info(f"Starting {task_name}: 0/{total} (0%)")

    def update(self, current: int) -> None:
        """
        Update progress.

        Args:
            current: Current number of items processed
        """
        if self.total == 0:
            return

        percent = (current / self.total) * 100

        # Log if we've crossed the next logging threshold
        if percent >= self.last_logged_percent + self.log_every or current == self.total:
            elapsed = time.perf_counter() - self.start_time
            rate = current / elapsed if elapsed > 0 else 0

            logger.info(
                f"{self.task_name}: {current}/{self.total} ({percent:.1f}%) - "
                f"Rate: {rate:.1f} items/sec",
                extra={"progress": percent, "rate": rate}
            )

            self.last_logged_percent = int(percent / self.log_every) * self.log_every

    def complete(self) -> None:
        """Mark the task as complete and log final statistics."""
        elapsed = time.perf_counter() - self.start_time
        rate = self.total / elapsed if elapsed > 0 else 0

        logger.info(
            f"✓ {self.task_name} completed: {self.total} items in {elapsed:.2f}s "
            f"(avg {rate:.1f} items/sec)"
        )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "logger",
    "get_logger",
    "LogContext",
    "log_execution_time",
    "log_step",
    "log_exception",
    "ProgressLogger",
    "configure_logger",
]

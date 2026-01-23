"""
Comprehensive logging configuration for sideMCP.

Provides detailed logging to help debug issues and track performance.
"""

import logging
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Optional: Sentry and PostHog
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

try:
    from posthog import Posthog
    POSTHOG_AVAILABLE = True
except ImportError:
    POSTHOG_AVAILABLE = False


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra attributes
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
            
        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO", log_file: str | None = None) -> None:
    """
    Setup high-fidelity logging and telemetry for sideMCP.
    """
    # 1. Initialize Sentry if DSN is provided
    sentry_dsn = os.getenv("SENTRY_DSN")
    if SENTRY_AVAILABLE and sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=1.0,
            environment=os.getenv("RAILWAY_ENVIRONMENT_NAME", "development")
        )
        logging.info("Sentry initialized")

    # 2. Determine Log File
    if log_file is None:
        log_dir = Path.home() / ".side-mcp" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "sidelith.log"

    # 3. Setup Formatting
    # Use JSON for production/file, simple for development
    is_production = os.getenv("RAILWAY_ENVIRONMENT_NAME") is not None
    
    if is_production:
        formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ")
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
            datefmt="%H:%M:%S"
        )

    # 4. Handlers
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 5. Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)

    # Reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.WARNING)

    root_logger.info(f"Observability Layer Active - Env: {os.getenv('RAILWAY_ENVIRONMENT_NAME', 'local')}")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

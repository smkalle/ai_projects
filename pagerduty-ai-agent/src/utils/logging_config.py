"""
Logging configuration for PagerDuty AI Agent.
"""

import logging
import logging.config
import os
from typing import Dict, Any

def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "mode": "a",
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "mode": "a",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file", "error_file"],
                "level": log_level,
                "propagate": False,
            },
            "streamlit": {
                "handlers": ["console", "file"],
                "level": "WARNING",
                "propagate": False,
            },
            "langchain": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "openai": {
                "handlers": ["console", "file"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
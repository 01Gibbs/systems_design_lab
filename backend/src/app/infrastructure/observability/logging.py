"""Structured logging configuration - Infrastructure adapter"""

import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging(*, level: str = "INFO", json_format: bool = True) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, output JSON logs (for Loki). If False, human-readable.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if json_format:
        # JSON format for machine parsing (Loki)
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s "
            "%(request_id)s %(trace_id)s %(span_id)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )
        log_handler.setFormatter(formatter)
    else:
        # Human-readable format for local dev
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    root_logger = logging.getLogger()
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(log_handler)
    root_logger.setLevel(log_level)

    # Set uvicorn loggers to use same configuration
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.propagate = True

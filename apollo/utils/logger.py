# apollo/utils/logger.py
# ============================================================
# Centralized logging setup for Apollo.
#
# All modules should import get_logger from here instead of
# calling logging.getLogger directly. This ensures consistent
# formatting across the entire app.
#
# Usage:
#     from apollo.utils.logger import get_logger
#     logger = get_logger(__name__)
#     logger.info("Apollo started")
# ============================================================

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module name.

    Args:
        name: Typically __name__ from the calling module.
              Produces names like: apollo.core.wakeword.detector

    Log levels (low → high severity):
        DEBUG   → detailed internal state, audio frame counts, etc.
        INFO    → normal events (wake word detected, STT result, etc.)
        WARNING → recoverable issues (audio buffer overflow, retry, etc.)
        ERROR   → failures that affect functionality
        CRITICAL → app-breaking failures
    """
    logger = logging.getLogger(name)

    # Only add handler if the logger doesn't already have one
    # (prevents duplicate log lines if get_logger is called multiple times)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        ))
        logger.addHandler(handler)

    # Default level: DEBUG in development, INFO in production
    # TODO: read level from .env (LOG_LEVEL=DEBUG)
    logger.setLevel(logging.DEBUG)

    return logger

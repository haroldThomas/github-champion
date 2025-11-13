import logging
import sys

def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure and return a root logger for the application.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger("github_champion")
    logger.setLevel(numeric_level)

    # Avoid adding multiple handlers if setup_logging is called more than once
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
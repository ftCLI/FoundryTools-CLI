import sys

from loguru import logger

# Remove the default logger
logger.remove(0)

# Add a sink to the logger to print to stdout
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<level>{message}</level>",
)

__all__ = ["logger"]

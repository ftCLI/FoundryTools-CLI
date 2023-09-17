import sys

from pathlib import Path

from loguru import logger

# Remove the default logger
logger.remove(0)

# Add a sink to the logger to print to stdout
logger.add(
    sys.stdout,
    level="INFO",
    backtrace=False,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " "<level>{level: <8}</level> | " "<level>{message}</level>",
)


class Logs:
    file_saved = "File saved: {file}"
    file_not_changed = "File not changed: {file}"
    file_not_selected = "File not selected: {file}"
    file_not_exists = "File does not exist: {file}"
    no_valid_fonts = "No valid fonts found: {input_path}"
    x_height_not_defined = "sxHeight is defined only in OS/2 version 2 and up. Current OS/2 version is {version}"


__all__ = ["logger", "Logs"]

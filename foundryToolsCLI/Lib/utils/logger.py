import sys

from functools import partialmethod

from loguru import logger

# Remove the default logger
logger.remove(0)

# Add a sink to the logger to print to stdout
logger.add(
    sys.stdout,
    level="SUCCESS",
    backtrace=False,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " "<level>{level: <8}</level> | " "<level>{message}</level>",
)

# Add a custom level to the logger
logger.level("SKIP", no=27, color="<yellow>", icon="⏭️")
logger.__class__.skip = partialmethod(logger.__class__.log, "SKIP")


class Logs:
    file_saved = "File saved: {file}"
    file_not_changed = "File not changed: {file}"
    file_not_selected = "File not selected: {file}"
    file_not_exists = "File does not exist: {file}"
    no_valid_fonts = "No valid fonts found: {input_path}"
    x_height_not_defined = "sxHeight is defined only in OS/2 version 2 and up. Current OS/2 version is {version}"
    not_monospaced = "Font is not monospaced: {file}"


__all__ = ["logger", "Logs"]

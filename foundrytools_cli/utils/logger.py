import sys
from functools import partialmethod

from loguru import logger

# Remove the default logger
logger.remove()

# Add a sink to the logger to print to stdout
logger.add(
    sys.stderr,
    backtrace=False,
    colorize=True,
    format="[ <level>{level: <8}</level> ] {message}",
    level="INFO",
)

# Add a custom level to the logger
logger.level("SKIP", no=27, color="<light-black><bold>", icon="⏭️")
logger.__class__.skip = partialmethod(logger.__class__.log, "SKIP")  # type: ignore
logger.opt(colors=True)

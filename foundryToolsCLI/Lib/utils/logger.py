import sys

from functools import partialmethod

from loguru import logger

# Remove the default logger
logger.remove(0)

# Add a sink to the logger to print to stdout
logger.add(
    sys.stdout,
    level="INFO",
    backtrace=False,
    colorize=True,
    format="[ <level>{level: <8}</level> ] " "<level>{message}</level>",
)

# Add a custom level to the logger
logger.level("SKIP", no=27, color="<light-black><bold>", icon="⏭️")
logger.__class__.skip = partialmethod(logger.__class__.log, "SKIP")


class Logs:
    checking_file = "Checking file: <cyan>{file}</>"
    current_file = "Current file: <cyan>{file}</>"
    converting_file = "Converting file: <cyan>{file}</>"
    file_saved = "File saved: {file}"
    file_not_changed = "File not changed: {file}"
    file_not_selected = "File not selected: {file}"
    file_not_exists = "File does not exist: {file}"
    no_valid_fonts = "No valid fonts found: {input_path}"
    no_parameter = "Please, pass at least a valid parameter."
    x_height_not_defined = (
        "sxHeight is defined only in OS/2 version 2 and up. Current OS/2 version is {version}"
    )
    cap_height_not_defined = (
        "sCapHeight is defined only in OS/2 version 2 and up. Current version is {os_2.version}"
    )
    max_context_not_defined = (
        "usMaxContext is defined only in OS/2 version 2 and up. Current version is {os_2.version}"
    )
    bits_7_8_9_not_defined = (
        "{flag} flag can't be set. Bits 7, 8 and 9 are defined only in OS/2 version 4 and up. Current version is "
        "{version}"
    )
    not_monospaced = "Font is not monospaced: {file}"
    postscript_name_too_long = (
        "PostScript name is too long: {max} characters allowed, {current} found"
    )
    full_font_name_too_long = (
        "Full font name is too long: {max} characters allowed, {current} found"
    )
    tiny_path_removed = "Tiny path removed from glyph: {glyph_name}"


__all__ = ["logger", "Logs"]

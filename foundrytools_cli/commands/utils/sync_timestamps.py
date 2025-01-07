# pylint: disable=import-outside-toplevel
import os
import platform
from pathlib import Path

from fontTools.misc.timeTools import epoch_diff, timestampToString
from foundrytools import FontFinder
from foundrytools.constants import T_HEAD

from foundrytools_cli.utils.logger import logger

# Placeholder for `setctime`, and `import_error`
SETCTIME = None
IMPORT_ERROR = None

# Conditionally import win32_setctime if running on Windows
if platform.system() == "Windows":
    try:
        from win32_setctime import setctime

        SETCTIME = setctime
    except (ImportError, Exception) as exc:  # pylint: disable=broad-except
        SETCTIME = None
        IMPORT_ERROR = exc


__all__ = ["main"]


# Helper function for Python 3.8 compatibility
def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False


def _get_file_timestamps(input_path: Path, recursive: bool = True) -> dict[Path, tuple[int, int]]:
    finder = FontFinder(input_path)
    finder.options.recursive = recursive
    fonts = finder.find_fonts()

    font_timestamps = {
        font.file: (font.ttfont[T_HEAD].created, font.ttfont[T_HEAD].modified)
        for font in fonts
        if font.file
    }

    return font_timestamps


def _get_folder_timestamps(
    folders: set[Path],
    files_timestamps: dict[Path, tuple[int, int]],
) -> dict[Path, tuple[int, int]]:
    folder_timestamps = {
        folder: (
            min(
                files_timestamps[file][0]
                for file in files_timestamps
                if hasattr(file, "is_relative_to")
                and file.is_relative_to(folder)
                or _is_relative_to(file, folder)
            ),
            max(
                files_timestamps[file][1]
                for file in files_timestamps
                if hasattr(file, "is_relative_to")
                and file.is_relative_to(folder)
                or _is_relative_to(file, folder)
            ),
        )
        for folder in folders
    }

    return folder_timestamps


def _set_timestamps(path_timestamps: dict[Path, tuple[int, int]]) -> None:
    for path, timestamps in path_timestamps.items():
        logger.opt(colors=True).info(f"Current path: <light-cyan>{path}</>")

        # Set the file creation time on Windows. Figure out a way to do this on other platforms.
        if platform.system() == "Windows":
            _set_windows_ctime(path, timestamps[0])
        _set_mtime_and_atime(path, timestamps[1])
        print()


def _set_windows_ctime(path: Path, timestamp: int) -> None:
    if SETCTIME is None:
        raise ImportError(
            "Unable to set file creation time on Windows. Please install the "
            "win32_setctime package."
        ) from IMPORT_ERROR

    try:
        SETCTIME(path, timestamp + epoch_diff)
        logger.info(f"created timestamp  : {timestampToString(timestamp)}")
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Error setting file creation time: {e}")


def _set_mtime_and_atime(path: Path, timestamp: int) -> None:
    try:
        os.utime(path, (timestamp + epoch_diff, timestamp + epoch_diff))
        logger.info(f"modified timestamp : {timestampToString(timestamp)}")
        logger.info(f"access timestamp   : {timestampToString(timestamp)}")
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Error setting file timestamps: {e}")


def main(input_path: Path, recursive: bool = False) -> None:
    """
    Aligns files created and modified timestamps with the created and modified values stored in the
    head table.
    """

    logger.info("Collecting file and folder timestamps...")
    file_timestamps = _get_file_timestamps(input_path, recursive=recursive)
    if not file_timestamps:
        logger.error("No valid font files found.")
        return

    folders = {file.parent for file in file_timestamps}
    folder_timestamps = _get_folder_timestamps(folders, file_timestamps)

    _set_timestamps(file_timestamps)
    _set_timestamps(folder_timestamps)

from pathlib import Path

from foundrytools import Font
from foundrytools.constants import T_HEAD, T_NAME
from pathvalidate import sanitize_filename, sanitize_filepath

from foundrytools_cli.utils.logger import logger

__all__ = ["main"]


def _determine_output_directory(
    base_dir: Path,
    font: Font,
    sort_by_manufacturer: bool,
    sort_by_font_revision: bool,
    sort_by_extension: bool,
) -> Path:
    """
    Determines the output directory for the font file based on sorting options.

    Args:
        base_dir (Path): The base directory where the font file will be saved.
        font (Font): The font object containing metadata.
        sort_by_manufacturer (bool): Whether to sort by manufacturer.
        sort_by_font_revision (bool): Whether to sort by font revision.
        sort_by_extension (bool): Whether to sort by file extension.

    Returns:
        Path: The sanitized output directory path.
    """
    family_name = sanitize_filename(font.ttfont[T_NAME].getBestFamilyName())
    manufacturer_name = sanitize_filename(font.ttfont[T_NAME].getDebugName(8))
    font_revision = sanitize_filename(f"v{font.ttfont[T_HEAD].fontRevision:.3f}")
    extension = font.get_file_ext().replace(".", "")

    out_dir = base_dir

    if sort_by_manufacturer and manufacturer_name:
        out_dir = out_dir.joinpath(manufacturer_name)

    if sort_by_font_revision and font_revision:
        out_dir = out_dir.joinpath(f"{family_name} {font_revision}")
    else:
        out_dir = out_dir.joinpath(family_name)

    if sort_by_extension:
        out_dir = out_dir.joinpath(extension)

    return sanitize_filepath(out_dir, platform="auto")


def _remove_empty_directories(directory: Path) -> None:
    """
    Removes empty directories recursively.

    Args:
        directory (Path): The directory to start removing from.
    """
    while not any(directory.iterdir()):
        directory.rmdir()
        logger.opt(colors=True).success(f"{directory} <magenta>--></> <red>Deleted</>")
        directory = directory.parent


def main(
    font: Font,
    in_path: Path,
    sort_by_manufacturer: bool = False,
    sort_by_font_revision: bool = False,
    sort_by_extension: bool = False,
    delete_empty_directories: bool = False,
) -> None:
    """
    Organizes the given font files based on specified sorting options.

    Args:
        font (Font): The font object to be organized.
        in_path (Path): The input path where the font file is located.
        sort_by_manufacturer (bool, optional): Whether to sort by manufacturer. Defaults to False.
        sort_by_font_revision (bool, optional): Whether to sort by font revision. Defaults to False.
        sort_by_extension (bool, optional): Whether to sort by file extension. Defaults to False.
        delete_empty_directories (bool, optional): Whether to delete empty directories after moving
            the font file. Defaults to False.

    Raises:
        AttributeError: If the font file is None.
    """
    if font.file is None:
        raise AttributeError("Font file is None")

    with font:
        out_dir = _determine_output_directory(
            base_dir=in_path,
            font=font,
            sort_by_manufacturer=sort_by_manufacturer,
            sort_by_font_revision=sort_by_font_revision,
            sort_by_extension=sort_by_extension,
        )
        out_dir.mkdir(parents=True, exist_ok=True)

        new_file = font.get_file_path(file=out_dir.joinpath(font.file.name), overwrite=True)

        if font.file == new_file:
            logger.skip("No changes made")  # type: ignore
        elif new_file.exists():
            logger.opt(colors=True).warning(
                f"<red>{new_file.relative_to(in_path)}</> already exists"
            )
        else:
            font.file.rename(new_file)
            logger.opt(colors=True).success(
                f"{font.file.relative_to(in_path)} <magenta>--></> "
                f"<green>{new_file.relative_to(in_path)}</>"
            )

        if delete_empty_directories:
            _remove_empty_directories(font.file.parent)

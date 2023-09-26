from typing import Optional

from pathlib import Path

from fontTools.ttLib import TTLibError

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.VFont import VariableFont
from foundryToolsCLI.Lib.utils.logger import logger


def get_files_in_path(input_path: Path, recursive: bool = False) -> list[Path]:
    """
    Get a list of files from a path. If the path is a directory, the function will return a list of all files found in
    the directory. If ``recursive`` is True, the function will recursively search for files in subdirectories. If the
    path is a file, the function will return a list containing only one file.
    :param input_path: path to the input file or directory
    :param recursive: If True, the function will recursively search for files in subdirectories
    :return: A list of pathlib.Path objects representing the files found in the path
    """
    files = []
    if input_path.is_file():
        files.append(input_path.resolve())
    if input_path.is_dir():
        if recursive:
            files = [p.resolve() for p in input_path.rglob("*") if p.is_file()]
        else:
            files = [p.resolve() for p in input_path.iterdir() if p.is_file()]

    return files


def get_variable_fonts_in_path(
    input_path: Path, recursive: bool = False, recalc_timestamp: bool = False
) -> list[VariableFont]:
    """
    Get a list of VariableFont objects from a path. If the path is a directory, the function will return a list of all
    VariableFont objects found in the directory. If ``recursive`` is True, the function will recursively search for
    VariableFonts in subdirectories. If the path is a file, the function will return a list containing only one
    VariableFont.
    :param input_path: path to the input file or directory
    :param recursive: If True, the function will recursively search for VariableFonts in subdirectories
    :param recalc_timestamp: If True, the function ``modified`` timestamp in the ``head`` table will be recalculated
    on save
    :return: A list of VariableFont objects
    """
    files = get_files_in_path(input_path, recursive=recursive)

    variable_fonts = []
    for file in files:
        try:
            variable_font = VariableFont(file, recalcTimestamp=recalc_timestamp)
            variable_fonts.append(variable_font)
        except (TTLibError, Exception):
            pass

    return variable_fonts


def get_fonts_in_path(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    allow_extensions: list = None,
    allow_ttf=True,
    allow_cff=True,
    allow_static=True,
    allow_variable=True,
    allow_web_font=True,
    allow_sfnt=True,
) -> list[Font]:
    """
    Get a list of Font objects from a path, optionally filtering by extension and font type. If the path is a directory,
    the function will return a list of all Font objects found in the directory. If ``recursive`` is True, the function
    will recursively search for fonts in subdirectories. If the path is a file, the function will return a list
    containing only one Font.

    :param input_path: The path to the input file or directory
    :param recursive: If True, the function will recursively search for fonts in subdirectories
    :param recalc_timestamp: If True, the ``modified`` timestamp in the ``head`` table will be recalculated on save
    :param allow_extensions: A list of allowed extensions.
    :param allow_ttf:   If False, TrueType fonts will be excluded from the list
    :param allow_cff:  If False, CFF fonts will be excluded from the list
    :param allow_static: If False, static fonts will be excluded from the list
    :param allow_variable: If False, variable fonts will be excluded from the list
    :param allow_web_font: If False, web fonts will be excluded from the list
    :param allow_sfnt: If False, sfnt fonts will be excluded from the list
    :return: A list of Font objects
    """
    files = get_files_in_path(input_path, recursive=recursive)

    fonts = []
    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalc_timestamp)

            if allow_extensions and font.get_real_extension() not in allow_extensions:
                continue
            if not allow_ttf and font.is_ttf:
                continue
            if not allow_cff and font.is_otf:
                continue
            if not allow_static and font.is_static:
                continue
            if not allow_variable and font.is_variable:
                continue
            if not allow_sfnt and font.is_sfnt:
                continue
            if not allow_web_font and font.is_web_font:
                continue

            fonts.append(font)

        except (TTLibError, Exception):
            pass

    return fonts


def initial_check_pass(fonts: list, output_dir: Optional[Path] = None) -> bool:
    """
    Checks if the list of fonts is not empty and if the output directory is writable.

    :param fonts: a list Font objects
    :param output_dir: the output directory
    :return: False if one of the checks fails, True if both checks succeed
    """
    if not len(fonts) > 0:
        logger.error("No valid fonts found")
        return False

    if output_dir is not None:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.exception(e)
            return False

    return True


def get_project_files_path(input_path: Path) -> Path:
    """
    Get the path to the directory containing the project files (styles_mapping.json, fonts_data.csv).
    :param input_path:
    :return:
    """
    if input_path.is_file():
        project_files_path = input_path.parent.joinpath("ftCLI_files")
    else:
        project_files_path = input_path.joinpath("ftCLI_files")

    return project_files_path


def get_style_mapping_path(input_path: Path) -> Path:
    """
    Get the path to the styles_mapping.json file.
    :param input_path: Path to the input file or directory
    :return: A pathlib.Path object representing the styles_mapping.json file
    """
    project_files_dir = get_project_files_path(input_path)
    styles_mapping_file = Path.joinpath(project_files_dir, "styles_mapping.json")

    return styles_mapping_file


def get_fonts_data_path(input_path: Path) -> Path:
    """
    Get the path to the fonts_data.csv file.
    :param input_path: Path to the input file or directory
    :return: A pathlib.Path object representing the fonts_data.csv file
    """
    project_files_dir = get_project_files_path(input_path)
    fonts_data_file = Path.joinpath(project_files_dir, "fonts_data.csv")

    return fonts_data_file

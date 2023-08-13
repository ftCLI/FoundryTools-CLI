import pathlib

import click
from fontTools.ttLib import TTLibError

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.VFont import VariableFont


def get_variable_fonts_in_path(input_path: pathlib.Path, recalc_timestamp: bool = False) -> list[VariableFont]:
    files = []
    if input_path.is_file():
        files.append(input_path.resolve())
    if input_path.is_dir():
        files = [p.resolve() for p in input_path.iterdir()]

    variable_fonts = []
    for file in files:
        try:
            variable_font = VariableFont(file, recalcTimestamp=recalc_timestamp)
            variable_fonts.append(variable_font)
        except (TTLibError, Exception):
            pass

    return variable_fonts


def get_fonts_in_path(
    input_path: pathlib.Path,
    recalc_timestamp: bool = False,
    allow_extensions: list = None,
    allow_ttf=True,
    allow_cff=True,
    allow_static=True,
    allow_variable=True,
    allow_web_font=True,
    allow_sfnt=True,
) -> list[Font]:
    files = []
    if input_path.is_file():
        files.append(input_path.resolve())
    if input_path.is_dir():
        files = [p.resolve() for p in input_path.iterdir()]

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


def get_output_dir(input_path: pathlib.Path, output_dir: pathlib.Path = None) -> pathlib.Path:
    """
    If the output directory is not specified, then the output directory is the directory of the input file if the input
    is a file, or the input directory if the input is a directory

    :param input_path: The path to the input file or directory
    :type input_path: str
    :param output_dir: The output directory, if specified
    :type output_dir: str
    :return: The output directory.
    """
    if output_dir is not None:
        return output_dir.resolve()
    else:
        if input_path.is_file():
            return input_path.parent.resolve()
        else:
            return input_path.resolve()


def initial_check_pass(fonts: list, output_dir: pathlib.Path) -> bool:
    """
    Checks if the list of fonts is not empty and if the output directory is writable.

    :param fonts: a list Font objects
    :param output_dir: the output directory
    :return: False if one of the checks fails, True if both checks succeed
    """
    if not len(fonts) > 0:
        click.secho(f"[{click.style('FAIL', fg='red')}] No fonts matching the given criteria")
        return False
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        click.secho(f"[{click.style('FAIL', fg='red')}] {e}")
        return False
    return True


def get_project_files_path(input_path: pathlib.Path) -> pathlib.Path:
    if input_path.is_file():
        project_files_path = input_path.parent.joinpath("ftCLI_files")
    else:
        project_files_path = input_path.joinpath("ftCLI_files")

    return project_files_path


def get_style_mapping_path(input_path: pathlib.Path) -> pathlib.Path:
    project_files_dir = get_project_files_path(input_path)
    styles_mapping_file = pathlib.Path.joinpath(project_files_dir, "styles_mapping.json")

    return styles_mapping_file


def get_fonts_data_path(input_path: pathlib.Path) -> pathlib.Path:
    project_files_dir = get_project_files_path(input_path)
    fonts_data_file = pathlib.Path.joinpath(project_files_dir, "fonts_data.csv")

    return fonts_data_file

import pathlib
from pathlib import Path

import click


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def add_file_or_path_argument(dir_okay=True, file_okay=True):
    _file_or_path_argument = [
        click.argument(
            "input_path",
            type=click.Path(
                exists=True, resolve_path=True, path_type=pathlib.Path, dir_okay=dir_okay, file_okay=file_okay
            ),
        )
    ]
    return add_options(_file_or_path_argument)


def add_file_argument():
    return add_file_or_path_argument(dir_okay=False)


def add_path_argument():
    return add_file_or_path_argument(file_okay=False)


def add_common_options():
    _common_options = [
        click.option(
            "-out",
            "--output-dir",
            type=click.Path(path_type=pathlib.Path, file_okay=False, resolve_path=True),
            default=None,
            help="""
            Specify the directory where output files are to be saved. If the directory doesn't exist, will be created.
            If output_dir is not specified, files will be saved to the same folder.
            """,
        ),
        click.option(
            "--recalc-timestamp",
            is_flag=True,
            default=False,
            help="""
            Keep the original font 'modified' timestamp (head.modified) or set it to current time. By default,
            original timestamp is kept.
            """,
        ),
        click.option(
            "--no-overwrite",
            "overwrite",
            is_flag=True,
            default=True,
            help="""
            Overwrite existing files or save them to a new file (numbers are appended at the end of file name). By
            default, files are overwritten.
            """,
        ),
    ]
    return add_options(_common_options)


def file_overwrite_prompt(input_file: Path) -> bool:
    return click.confirm(
        f"{click.style(input_file, fg='yellow', bold=True)} already exists. " f"Do you want to overwrite it?"
    )


def file_not_selected_message(file: Path):
    click.secho(
        f"[{click.style('SKIP', fg='yellow')}] {file.name} ({click.style('file is not selected', fg='yellow')})"
    )


def no_valid_fonts_message(input_path: Path):
    if input_path.is_dir():
        message = f"No valid font files matching the given criteria found in {input_path.name}"
    else:
        message = f"{input_path.name} is not a valid font file or doesn't match the given criteria"
    click.secho(f"[{click.style('FAIL', fg='red')}] {message}")


def file_not_exists_message(file: Path):
    click.secho(
        f"[{click.style('WARN', fg='bright_yellow')}] {file} {click.style('file does not exist', fg='bright_yellow')}"
    )


def file_not_changed_message(file: Path):
    click.secho(
        f"[{click.style('SKIP', fg='bright_yellow')}] {file} ({click.style('no changes made', fg='bright_yellow')})"
    )


def file_saved_message(file: Path):
    click.secho(f"[{click.style('DONE', fg='green')}] {file} ({click.style('saved', fg='green')})")


def generic_success_message(success_message):
    click.secho(f"[{click.style('PASS', fg='green')}] {success_message}")


def generic_info_message(info_message, nl=True):
    click.secho(f"[{click.style('INFO', fg='cyan')}] {info_message}", nl=nl)


def generic_error_message(error_message):
    click.secho(f"[{click.style('FAIL', fg='red')}] {error_message}")


def generic_warning_message(warning_message):
    click.secho(f"[{click.style('WARN', fg='bright_yellow')}] {warning_message}")


def select_instance_coordinates(axes: list) -> dict:
    click.secho("\nSelect coordinates:")
    selected_coordinates = {}
    for a in axes:
        axis_tag = a.axisTag
        min_value = a.minValue
        max_value = a.maxValue
        coordinates = click.prompt(
            f"{axis_tag} ({min_value} - {max_value})",
            type=click.FloatRange(min_value, max_value),
        )
        selected_coordinates[axis_tag] = coordinates

    return selected_coordinates


# Allows to pass no value in prompts.
# Usage: click.prompt()
# See: https://stackoverflow.com/questions/68529664/prompt-for-an-optional-intrange-with-click-prompt
class OptionalParamType(click.ParamType):
    def __init__(self, param_type: click.ParamType):
        self.param_type = param_type

    def convert(self, value, param, ctx):
        if not value:
            return
        return self.param_type.convert(value, param, ctx)

from copy import copy

import click
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import check_output_dir, check_input_path
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    file_saved_message,
    file_not_changed_message,
    generic_error_message,
)


@click.command()
@add_file_or_path_argument()
@click.option(
    "--rise",
    type=int,
    help="""
              Sets the `caretSlopeRise` value.
              """,
)
@click.option(
    "--run",
    type=int,
    help="""
              Sets the `caretSlopeRun` value.
              """,
)
@click.option(
    "--offset",
    type=int,
    help="""
              Sets the `caretOffset` value.
              """,
)
@click.option(
    "--ascent",
    type=int,
    help="""
              Sets the `ascent` value.
              """,
)
@click.option(
    "--descent",
    type=int,
    help="""
              Sets the `descent` value.
              """,
)
@click.option(
    "--linegap",
    type=int,
    help="""
              Sets the `lineGap` value.
              """,
)
@add_common_options()
def cli(input_path, recalcTimestamp, outputDir, overWrite, **kwargs):
    """Command line hhea table editor."""

    params = {k: v for k, v in kwargs.items() if v is not None}

    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
            hhea_table_copy = copy(font.hhea_table)

            if "rise" in params.keys():
                font.hhea_table.set_caret_slope_rise(params.get("rise"))

            if "run" in params.keys():
                font.hhea_table.set_caret_slope_run(params.get("run"))

            if "offset" in params.keys():
                font.hhea_table.set_caret_offset(params.get("offset"))

            if "ascent" in params.keys():
                font.hhea_table.set_ascent(params.get("ascent"))

            if "descent" in params.keys():
                font.hhea_table.set_descent(params.get("descent"))

            if "linegap" in params.keys():
                font.hhea_table.set_linegap(params.get("linegap"))

            if font.hhea_table != hhea_table_copy:
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)

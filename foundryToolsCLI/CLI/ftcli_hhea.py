import os
from copy import copy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.tables.hhea import TableHhea
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_recursive_option,
    add_common_options,
)
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.timer import Timer


@click.command()
@add_file_or_path_argument()
@click.option("--rise", type=int, help="""Sets the ``caretSlopeRise`` value.""")
@click.option("--run", type=int, help="""Sets the ``caretSlopeRun`` value.""")
@click.option("--offset", type=int, help="""Sets the ``caretOffset`` value.""")
@click.option("--ascent", type=int, help="""Sets the ``ascent`` value.""")
@click.option("--descent", type=int, help="""Sets the ``descent`` value.""")
@click.option("--linegap", type=int, help="""Sets the ``lineGap`` value.""")
@click.option("--recalc-offset", is_flag=True, default=None, help="""Recalculate the ``caretOffset`` value.""")
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def cli(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = True,
    output_dir: Path = None,
    overwrite: bool = True,
    **kwargs
):
    """A command line tool to manipulate the ``hhea`` table."""

    params = {k: v for k, v in kwargs.items() if v is not None}

    if len(params) == 0:
        logger.error(Logs.no_parameter)
        return

    fonts = get_fonts_in_path(input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            hhea_table: TableHhea = font["hhea"]
            hhea_table_copy = copy(hhea_table)

            if "rise" in params.keys():
                hhea_table.set_caret_slope_rise(params.get("rise"))

            if "run" in params.keys():
                hhea_table.set_caret_slope_run(params.get("run"))

            if "offset" in params.keys():
                hhea_table.set_caret_offset(params.get("offset"))

            if "ascent" in params.keys():
                hhea_table.set_ascent(params.get("ascent"))

            if "descent" in params.keys():
                hhea_table.set_descent(params.get("descent"))

            if "linegap" in params.keys():
                hhea_table.set_linegap(params.get("linegap"))

            if params.get("recalc_offset") is True:
                temp_otf_fd, temp_otf_file = font.make_temp_otf()
                temp_font = Font(temp_otf_file)
                calculated_offset = temp_font["hhea"].caretOffset
                hhea_table.set_caret_offset(calculated_offset)
                temp_font.close()
                os.close(temp_otf_fd)
                os.remove(temp_otf_file)

            if hhea_table_copy.compile(font) != hhea_table.compile(font):
                font.save(output_file)
                logger.info(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=output_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()

from copy import copy
from pathlib import Path
from typing import Optional

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.tables.post import TablePost
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
@click.option(
    "--italic-angle",
    type=click.FloatRange(-90.0, 90.0),
    help="""Sets the `italicAngle` value.""",
)
@click.option(
    "--ul-position",
    type=int,
    help="""Sets the `underlinePosition` value.""",
)
@click.option(
    "--ul-thickness",
    type=int,
    help="""Sets the `underlineThickness` value.""",
)
@click.option(
    "--fixed-pitch/--no-fixed-pitch",
    is_flag=True,
    default=None,
    help="""Sets or clears the `isFixedPitch` value.""",
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def cli(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = False,
    italic_angle: Optional[float] = None,
    ul_position: Optional[int] = None,
    ul_thickness: Optional[int] = None,
    fixed_pitch: Optional[bool] = None,
):
    """A command line tool to manipulate the 'post' table."""

    if not any([italic_angle, ul_position, ul_thickness, fixed_pitch]) is not None:
        logger.error(Logs.no_parameter)
        return

    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            post_table: TablePost = font["post"]
            post_table_copy = copy(post_table)
            if font.is_otf:
                cff_table = font["CFF "]
                cff_table_copy = copy(cff_table)
            else:
                cff_table = cff_table_copy = None

            # Process the arguments
            if italic_angle:
                post_table.set_italic_angle(italic_angle)
                if font.is_otf:
                    font["CFF "].cff.topDictIndex[0].ItalicAngle = round(italic_angle)

            if ul_position:
                post_table.set_underline_position(ul_position)

            if ul_thickness:
                post_table.set_underline_thickness(ul_thickness)

            if fixed_pitch is not None:
                post_table.set_fixed_pitch(fixed_pitch)

            # Check if tables have changed before saving the font. No need to compile here.
            if post_table_copy.compile(font) != post_table.compile(font):
                post_table_modified = True
            else:
                post_table_modified = False

            if font.is_otf and (cff_table_copy.compile(font) != cff_table.compile(font)):
                cff_table_modified = True
            else:
                cff_table_modified = False

            if post_table_modified or cff_table_modified:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()

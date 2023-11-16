from copy import copy
from pathlib import Path
from typing import Optional

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import add_common_options, add_file_or_path_argument
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.timer import Timer

vertical_metrics_tools = click.Group("subcommands")


@vertical_metrics_tools.command()
@add_file_or_path_argument()
@click.option(
    "-p",
    "--percent",
    type=click.IntRange(0, 100),
    required=True,
    help="Adjust font line spacing to % of UPM value.",
)
@add_common_options()
@Timer(logger=logger.info)
def set_linegap(
    input_path: Path,
    percent: int,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Modifies the line spacing metrics in one or more fonts.

    This is a fork of font-line by Source Foundry: https://github.com/source-foundry/font-line
    """

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            hhea_table = font["hhea"]
            os2_table = font["OS/2"]
            hhea_table_copy = copy(font["hhea"])
            os2_table_copy = copy(font["OS/2"])

            font.modify_linegap_percent(percent=percent)

            hhea_modified = hhea_table_copy != hhea_table
            os2_modified = os2_table_copy != os2_table

            if hhea_modified or os2_modified:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@vertical_metrics_tools.command()
@add_file_or_path_argument()
@click.option(
    "--with-linegap",
    is_flag=True,
    help="""
            By default, SIL method (https://silnrsi.github.io/FDBP/en-US/Line_Metrics.html) is used. This means that,
            in OS/2 table, sTypoAscender and sTypoDescender values are set, respectively, equal to maximum real ascender
            and minimum real descender, and the sTypoLineGap is set to zero. Use '--with-linegap' to set sTypoAscender
            value to the maximum ideal ascender (calculated from letters b, f, f, h, k, l and t) and the sTypoDescender
            value to the minimum ideal descender (calculated from letters g, j, p, q and y). The sTypoLineGap will be
            calculated as follows: (real ascender + abs(real descender)) - (ideal ascender + abs(ideal descender)).
    """,
)
@add_common_options()
@Timer(logger=logger.info)
def align(
    input_path: Path,
    with_linegap: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Aligns all fonts stored in INPUT_PATH folder to the same baseline.

    To achieve this, the script finds the maximum ascender and the minimum descender values of the fonts stored in the
    INPUT_PATH folder and applies those values to all fonts.

    This can produce undesired effects (an exaggerated line height) when one or more fonts contain swashes, for example.
    In such cases, it's better to copy the vertical metrics from a template font to one or more destination fonts using
    the 'ftcli metrics copy-metrics' command.

    See https://kltf.de/download/FontMetrics-kltf.pdf for more information.
    """

    import math

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    ideal_ascenders = []
    ideal_descenders = []
    real_ascenders = []
    real_descenders = []

    for font in fonts:
        try:
            font_y_min, font_y_max = font.get_bounding_box()
            real_ascenders.append(math.ceil(font_y_max))
            real_descenders.append(math.floor(font_y_min))

            if with_linegap:
                for glyph_name in ["b", "d", "f", "h", "k", "l", "t"]:
                    ideal_ascenders.append(math.ceil(font.get_glyph_bounds(glyph_name)["yMax"]))

                for glyph_name in ["g", "j", "p", "q", "y"]:
                    ideal_descenders.append(math.floor(font.get_glyph_bounds(glyph_name)["yMin"]))
            else:
                ideal_ascenders = real_ascenders
                ideal_ascenders = real_descenders

        except Exception as e:
            logger.exception(e)

    max_real_ascender = max(real_ascenders)
    min_real_descender = min(real_descenders)
    max_ideal_ascender = max(ideal_ascenders) if ideal_descenders != [] else max_real_ascender
    min_ideal_descender = min(ideal_descenders) if ideal_descenders != [] else min_real_descender
    typo_line_gap = (max_real_ascender + abs(min_real_descender)) - (
        max_ideal_ascender + abs(min_ideal_descender)
    )

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            hhea_table = font["hhea"]
            os2_table = font["OS/2"]
            hhea_table_copy = copy(hhea_table)
            os2_table_copy = copy(os2_table)

            hhea_table.ascender = max_real_ascender
            hhea_table.descender = min_real_descender
            hhea_table.lineGap = 0

            os2_table.usWinAscent = max_real_ascender
            os2_table.usWinDescent = abs(min_real_descender)
            os2_table.sTypoAscender = max_real_ascender
            os2_table.sTypoDescender = min_real_descender
            os2_table.sTypoLineGap = 0

            if with_linegap:
                os2_table.sTypoAscender = max_ideal_ascender
                os2_table.sTypoDescender = min_ideal_descender
                os2_table.sTypoLineGap = typo_line_gap

            hhea_modified = hhea_table_copy != hhea_table
            os2_modified = os2_table_copy != os2_table

            if hhea_modified or os2_modified:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@vertical_metrics_tools.command()
@click.option(
    "-s",
    "--source-file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    required=True,
    help="Source file. Vertical metrics from this font will be applied to all destination fonts.",
)
@click.option(
    "-d",
    "--destination",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    required=True,
    help="Destination file or directory.",
)
@add_common_options()
@Timer(logger=logger.info)
def copy_metrics(
    source_file: Path,
    destination: Path,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Copies vertical metrics from a source font to one or more destination fonts.
    """
    fonts = get_fonts_in_path(input_path=destination, recalc_timestamp=recalc_timestamp)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    try:
        source_font = Font(source_file)

        hhea_source = source_font["hhea"]
        os2_source = source_font["OS/2"]

        ascender = hhea_source.ascender
        descender = hhea_source.descender
        lineGap = hhea_source.lineGap

        usWinAscent = os2_source.usWinAscent
        usWinDescent = os2_source.usWinDescent
        sTypoAscender = os2_source.sTypoAscender
        sTypoDescender = os2_source.sTypoDescender
        sTypoLineGap = os2_source.sTypoLineGap

    except Exception as e:
        logger.exception(e)
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            hhea_table = font["hhea"]
            os2_table = font["OS/2"]

            hhea_table_copy = copy(hhea_table)
            os2_table_copy = copy(os2_table)

            hhea_table.ascender = ascender
            hhea_table.descender = descender
            hhea_table.lineGap = lineGap

            os2_table.usWinAscent = usWinAscent
            os2_table.usWinDescent = usWinDescent
            os2_table.sTypoAscender = sTypoAscender
            os2_table.sTypoDescender = sTypoDescender
            os2_table.sTypoLineGap = sTypoLineGap

            hhea_modified = hhea_table_copy != hhea_table
            os2_modified = os2_table_copy != os2_table

            if hhea_modified or os2_modified:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[vertical_metrics_tools],
    help="""
Vertical metrics tools.
""",
)

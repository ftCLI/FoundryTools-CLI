import sys
from copy import copy

import click
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import check_output_dir, check_input_path
from ftCLI.Lib.utils.click_tools import (
    add_common_options,
    file_saved_message,
    generic_error_message,
    add_file_or_path_argument,
    file_not_changed_message,
)


@click.group()
def set_linegap_percent():
    pass


@set_linegap_percent.command()
@add_file_or_path_argument()
@click.option(
    "-p",
    "--percent",
    type=click.IntRange(0, 100),
    required=True,
    help="Adjust font line spacing to % of UPM value.",
)
@add_common_options()
def set_linegap(input_path, percent, outputDir=None, recalcTimestamp=False, overWrite=True):
    """Modifies the line spacing metrics in one or more fonts.

    This is a fork of font-line by Source Foundry: https://github.com/source-foundry/font-line
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            hhea_table_copy = copy(font.hhea_table)
            os2_table_copy = copy(font.os_2_table)

            font.modify_linegap_percent(percent=percent)

            hhea_modified = hhea_table_copy != font.hhea_table
            os2_modified = os2_table_copy != font.os_2_table

            if hhea_modified or os2_modified:
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def align_vertical_metrics():
    pass


@align_vertical_metrics.command()
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
def align(input_path, with_linegap=False, outputDir=None, recalcTimestamp=False, overWrite=True):
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
    from ftCLI.Lib.utils.glyphs import get_glyph_bounds

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    fonts = []
    ideal_ascenders = []
    ideal_descenders = []
    real_ascenders = []
    real_descenders = []

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            fonts.append(font)

            font_y_min, font_y_max = font.get_bounding_box()
            real_ascenders.append(math.ceil(font_y_max))
            real_descenders.append(math.floor(font_y_min))

            if with_linegap:
                glyph_set = font.getGlyphSet()

                for glyph_name in ["b", "d", "f", "h", "k", "l", "t"]:
                    ideal_ascenders.append(math.ceil(get_glyph_bounds(glyph_set, glyph_name)["yMax"]))

                for glyph_name in ["g", "j", "p", "q", "y"]:
                    ideal_descenders.append(math.floor(get_glyph_bounds(glyph_set, glyph_name)["yMin"]))
            else:
                ideal_ascenders = real_ascenders
                ideal_ascenders = real_descenders

        except Exception as e:
            generic_error_message(e)

    max_real_ascender = max(real_ascenders)
    min_real_descender = min(real_descenders)
    max_ideal_ascender = max(ideal_ascenders) if ideal_descenders != [] else max_real_ascender
    min_ideal_descender = min(ideal_descenders) if ideal_descenders != [] else min_real_descender
    typo_line_gap = (max_real_ascender + abs(min_real_descender)) - (max_ideal_ascender + abs(min_ideal_descender))

    for font in fonts:
        hhea_table_copy = copy(font.hhea_table)
        os2_table_copy = copy(font.os_2_table)

        try:
            font.hhea_table.ascender = max_real_ascender
            font.hhea_table.descender = min_real_descender
            font.hhea_table.lineGap = 0

            font.os_2_table.usWinAscent = max_real_ascender
            font.os_2_table.usWinDescent = abs(min_real_descender)
            font.os_2_table.sTypoAscender = max_real_ascender
            font.os_2_table.sTypoDescender = min_real_descender
            font.os_2_table.sTypoLineGap = 0

            if with_linegap:
                font.os_2_table.sTypoAscender = max_ideal_ascender
                font.os_2_table.sTypoDescender = min_ideal_descender
                font.os_2_table.sTypoLineGap = typo_line_gap

            hhea_modified = hhea_table_copy != font.hhea_table
            os2_modified = os2_table_copy != font.os_2_table

            if hhea_modified or os2_modified:
                output_file = makeOutputFileName(font.file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(font.file)

            else:
                file_not_changed_message(font.file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def copy_vertical_metrics():
    pass


@copy_vertical_metrics.command()
@click.option(
    "-s",
    "--source-file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True,
    help="Source file. Vertical metrics from this font will be applied to all destination fonts.",
)
@click.option(
    "-d",
    "--destination",
    type=click.Path(exists=True, resolve_path=True),
    required=True,
    help="Destination file or directory.",
)
@click.option(
    "-o",
    "--output-dir",
    "outputDir",
    type=click.Path(file_okay=False, resolve_path=True),
    help="""
The output directory where the output files are to be created. If it doesn't exist, will be created. If not specified,
files are saved to the same folder.""",
)
@click.option(
    "--recalc-timestamp",
    "recalcTimestamp",
    is_flag=True,
    default=False,
    help="""
By default, original head.modified value is kept when a font is saved. Use this switch to set head.modified timestamp
to current time.
""",
)
@click.option(
    "--no-overwrite",
    "overWrite",
    is_flag=True,
    default=True,
    help="""
By default, modified files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name).
""",
)
def copy_metrics(source_file, destination, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Copies vertical metrics from a source font to one or more destination fonts.
    """

    files = check_input_path(destination)
    output_dir = check_output_dir(input_path=destination, output_path=outputDir)

    try:
        source_font = Font(source_file)

        ascender = source_font.hhea_table.ascender
        descender = source_font.hhea_table.descender
        lineGap = source_font.hhea_table.lineGap

        usWinAscent = source_font.os_2_table.usWinAscent
        usWinDescent = source_font.os_2_table.usWinDescent
        sTypoAscender = source_font.os_2_table.sTypoAscender
        sTypoDescender = source_font.os_2_table.sTypoDescender
        sTypoLineGap = source_font.os_2_table.sTypoLineGap

    except Exception as e:
        click.secho("ERROR: {}".format(e), fg="red")
        sys.exit()

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            hhea_table_copy = copy(font.hhea_table)
            os2_table_copy = copy(font.os_2_table)

            font.hhea_table.ascender = ascender
            font.hhea_table.descender = descender
            font.hhea_table.lineGap = lineGap

            font.os_2_table.usWinAscent = usWinAscent
            font.os_2_table.usWinDescent = usWinDescent
            font.os_2_table.sTypoAscender = sTypoAscender
            font.os_2_table.sTypoDescender = sTypoDescender
            font.os_2_table.sTypoLineGap = sTypoLineGap

            hhea_modified = hhea_table_copy != font.hhea_table
            os2_modified = os2_table_copy != font.os_2_table

            if hhea_modified or os2_modified:
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


cli = click.CommandCollection(
    sources=[align_vertical_metrics, set_linegap_percent, copy_vertical_metrics],
    help="""
Vertical metrics tools.
""",
)

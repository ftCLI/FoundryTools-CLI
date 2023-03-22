import os
import sys

import click
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import get_fonts_list, get_output_dir, check_output_dir
from ftCLI.Lib.utils.click_tools import (
    add_common_options,
    file_saved_message,
    generic_error_message,
    add_file_or_path_argument,
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
def set_linegap(
    input_path, percent, outputDir=None, recalcTimestamp=False, overWrite=True
):
    """Modifies the line spacing metrics in one or more fonts.

    This is a fork of font-line by Source Foundry: https://github.com/source-foundry/font-line
    """

    files = get_fonts_list(input_path)
    if len(files) == 0:
        generic_error_message(f"No valid font files found in {input_path}")
        return

    output_dir = get_output_dir(fallback_path=input_path, path=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            font.modify_linegap_percent(percent=percent)
            output_file = makeOutputFileName(
                file, outputDir=output_dir, overWrite=overWrite
            )
            font.save(output_file)
            file_saved_message(file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def align_vertical_metrics():
    pass


@align_vertical_metrics.command()
@add_file_or_path_argument()
@click.option(
    "-sil",
    "--sil-method",
    is_flag=True,
    help="Use SIL method: https://silnrsi.github.io/FDBP/en-US/Line_Metrics.html",
)
@add_common_options()
def align(
    input_path, sil_method=False, outputDir=None, recalcTimestamp=False, overWrite=True
):
    """
    Aligns all fonts stored in INPUT_PATH folder to the same baseline.

    To achieve this, the script finds the maximum ascender and the minimum descender values of the fonts stored in the
    INPUT_PATH folder and applies those values to all fonts.

    This can produce undesired effects (an exaggerated line height) when one or more fonts contain swashes, for example.
    In such cases, it's better to copy the vertical metrics from a template font to one or more destination fonts using
    the 'ftcli metrics copy' command.

    See https://kltf.de/download/FontMetrics-kltf.pdf for more information.
    """

    files = get_fonts_list(input_path)
    if len(files) == 0:
        generic_error_message(f"No valid font files found in {input_path}")
        return

    output_dir = get_output_dir(fallback_path=input_path, path=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    ideal_ascenders = []
    ideal_descenders = []
    real_ascenders = []
    real_descenders = []

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            y_max = font["head"].yMax
            y_min = font["head"].yMin

            ascender = font["hhea"].ascender
            descender = font["hhea"].descender

            typo_ascender = font["OS/2"].sTypoAscender
            typo_descender = font["OS/2"].sTypoDescender
            win_ascent = font["OS/2"].usWinAscent
            win_descent = font["OS/2"].usWinDescent

            ideal_ascenders.extend([typo_ascender])
            ideal_descenders.extend([abs(typo_descender)])

            real_ascenders.extend([y_max])
            real_descenders.extend([abs(y_min)])

        except Exception as e:
            generic_error_message(e)
            files.remove(file)

    max_real_ascender = max(real_ascenders)
    max_real_descender = max(real_descenders)
    max_ideal_ascender = max(ideal_ascenders)
    max_ideal_descender = max(ideal_descenders)
    typo_line_gap = (max_real_ascender + max_real_descender) - (
        max_ideal_ascender + max_ideal_descender
    )

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            font.hhea_table.ascender = max_real_ascender
            font.hhea_table.descender = -max_real_descender
            font.hhea_table.lineGap = 0

            font.os_2_table.usWinAscent = max_real_ascender
            font.os_2_table.usWinDescent = max_real_descender
            font.os_2_table.sTypoAscender = max_ideal_ascender
            font.os_2_table.sTypoDescender = -max_ideal_descender
            font.os_2_table.sTypoLineGap = typo_line_gap

            if sil_method:
                font.os_2_table.sTypoAscender = max_real_ascender
                font.os_2_table.sTypoDescender = -max_real_descender
                font.os_2_table.sTypoLineGap = 0

            output_file = makeOutputFileName(
                file, outputDir=outputDir, overWrite=overWrite
            )
            font.save(output_file)
            file_saved_message(file)
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
def copy(source_file, destination, outputDir, recalcTimestamp, overWrite):
    """
    Copies vertical metrics from a source font to one or more destination fonts.
    """

    try:
        source_font = Font(source_file)

        ascender = source_font["hhea"].ascender
        descender = source_font["hhea"].descender
        lineGap = source_font["hhea"].lineGap

        usWinAscent = source_font["OS/2"].usWinAscent
        usWinDescent = source_font["OS/2"].usWinDescent
        sTypoAscender = source_font["OS/2"].sTypoAscender
        sTypoDescender = source_font["OS/2"].sTypoDescender
        sTypoLineGap = source_font["OS/2"].sTypoLineGap

    except Exception as e:
        click.secho("ERROR: {}".format(e), fg="red")
        sys.exit()

    files = get_fonts_list(destination)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)

            font["hhea"].ascender = ascender
            font["hhea"].descender = descender
            font["hhea"].lineGap = lineGap

            font["OS/2"].usWinAscent = usWinAscent
            font["OS/2"].usWinDescent = usWinDescent
            font["OS/2"].sTypoAscender = sTypoAscender
            font["OS/2"].sTypoDescender = sTypoDescender
            font["OS/2"].sTypoLineGap = sTypoLineGap

            output_file = makeOutputFileName(
                f, outputDir=outputDir, overWrite=overWrite
            )
            font.save(output_file)
            click.secho(f"{os.path.basename(output_file)} --> saved", fg="green")
        except Exception as e:
            click.secho(f"ERROR: {e}", fg="red")


cli = click.CommandCollection(
    sources=[align_vertical_metrics, set_linegap_percent, copy_vertical_metrics],
    help="""
Vertical metrics tools.
""",
)

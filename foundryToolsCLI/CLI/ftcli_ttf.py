from io import BytesIO
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.utils.cli_tools import (
    get_fonts_in_path,
    get_output_dir,
    initial_check_pass,
)
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    file_not_changed_message,
    file_saved_message,
    generic_error_message,
    generic_info_message,
)

ttf_tools = click.Group("subcommands")


@ttf_tools.command()
@add_file_or_path_argument()
@add_common_options()
def autohint(
    input_path: Path,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Autohint TrueType fonts using ttfautohint-py.
    """

    from ttfautohint import ttfautohint

    fonts = get_fonts_in_path(
        input_path,
        recalc_timestamp=recalc_timestamp,
        allow_cff=False,
        allow_variable=False,
    )
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            buf = BytesIO()
            font.save(buf)
            data = ttfautohint(in_buffer=buf.getvalue(), no_info=True)
            hinted_font = Font(BytesIO(data))
            file = Path(font.reader.file.name)
            if not recalc_timestamp:
                hinted_font.set_modified_timestamp(font.modified_timestamp)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            hinted_font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@ttf_tools.command()
@add_file_or_path_argument()
@add_common_options()
def decompose(
    input_path: Path,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Decompose composite glyphs of a TrueType font.
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp, allow_cff=False)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            font.ttf_decomponentize()
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@ttf_tools.command()
@add_file_or_path_argument()
@add_common_options()
def dehint(
    input_path: Path,
    recalc_timestamp: bool = False,
    output_dir: Path = None,
    overwrite: bool = True,
):
    """
    Drops hinting from TrueType fonts.

    This is a CLI for dehinter by Source Foundry: https://github.com/source-foundry/dehinter
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp, allow_cff=False)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            font.ttf_dehint()
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@ttf_tools.command()
@add_file_or_path_argument()
@click.option(
    "--min-area",
    type=int,
    default=25,
    help="""
        Minimum area for a tiny outline.

        Default is 25 square units. Subpaths with a bounding box less than this will be reported and deleted.
    """,
)
@click.option(
    "--keep-hinting",
    "remove_hinting",
    is_flag=True,
    default=True,
    help="""Do not remove hinting.""",
)
@click.option("--silent", "verbose", is_flag=True, default=True, help="Run in silent mode")
@add_common_options()
def fix_contours(
    input_path: Path,
    min_area: int = 25,
    remove_hinting: bool = True,
    verbose: bool = True,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Fix winding and remove overlaps and tiny paths from contours.
    """
    fonts = get_fonts_in_path(
        input_path=input_path,
        allow_variable=False,
        allow_cff=False,
        recalc_timestamp=recalc_timestamp,
    )
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        print()
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            generic_info_message(f"Checking file {file.name}")
            font.ttf_fix_contours(min_area=min_area, remove_hinting=remove_hinting, verbose=verbose)
            font.save(output_file)
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@ttf_tools.command()
@add_file_or_path_argument()
@click.option(
    "--keep-hinting",
    "remove_hinting",
    is_flag=True,
    default=True,
    help="""Keep hinting for unmodified glyphs""",
)
@click.option(
    "--ignore-errors",
    is_flag=True,
    help="""Ignore errors while removing overlaps.""",
)
@add_common_options()
def remove_overlaps(
    input_path: Path,
    remove_hinting: bool = True,
    ignore_errors: bool = False,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Simplify glyphs in TrueType fonts by merging overlapping contours.
    """

    fonts = get_fonts_in_path(
        input_path,
        recalc_timestamp=recalc_timestamp,
        allow_cff=False,
        allow_variable=False,
    )
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.ttf_remove_overlaps(remove_hinting=remove_hinting, ignore_errors=ignore_errors)
            font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@ttf_tools.command()
@add_file_or_path_argument()
@click.option(
    "-upm",
    type=int,
    required=True,
    help="""
    New UPM value
    """,
)
@add_common_options()
def scale_upm(
    input_path: Path,
    upm: int,
    recalc_timestamp: bool = False,
    output_dir: Path = None,
    overwrite: bool = True,
):
    """
    Change the units-per-EM of TrueType fonts.

    Hinting is removed from scaled TrueType fonts to avoid bad results. You may consider to use 'ftcli utils
    ttf-autohint' to hint the scaled fonts.
    """

    fonts = get_fonts_in_path(input_path, allow_cff=False, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)

            if font["head"].unitsPerEm == upm:
                file_not_changed_message(file.relative_to(input_path))
                continue

            font.ttf_scale_upem(units_per_em=upm)

            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@ttf_tools.command()
@add_file_or_path_argument()
@click.option(
    "-old",
    "old_glyph_name",
    required=True,
    help="Old glyph name",
)
@click.option(
    "-new",
    "new_glyph_name",
    required=True,
    help="New glyph name",
)
@add_common_options()
def rename_glyph(
    input_path: Path,
    old_glyph_name: str,
    new_glyph_name: str,
    recalc_timestamp: bool = False,
    output_dir: Path = None,
    overwrite: bool = True,
):
    """
    Renames a glyph.
    """
    fonts = get_fonts_in_path(input_path=input_path, allow_cff=False, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            glyph_names = font.getGlyphOrder()
            modified = False
            for i in range(len(glyph_names)):
                if glyph_names[i] == old_glyph_name:
                    glyph_names[i] = new_glyph_name
                    generic_info_message(f"{old_glyph_name} renamed to {new_glyph_name}")
                    modified = True
            if modified:
                font.setGlyphOrder(glyph_names)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)
        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[ttf_tools],
    help="""
    A set of tools to manipulate fonts with TrueType outlines.
    """,
)

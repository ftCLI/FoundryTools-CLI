import time
from copy import deepcopy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, get_output_dir, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    file_saved_message,
    generic_error_message,
    generic_info_message,
    file_not_changed_message,
)

otf_tools = click.Group("subcommands")


@otf_tools.command()
@add_file_or_path_argument()
@click.option(
    "--optimize/--no-optimize",
    default=True,
    help="""
    Optimize the hinted font by specializing the charstrings and applying subroutines.
    """,
)
@click.option(
    "-r",
    "--reference-font",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="""
    Reference font.

    Font to be used as reference, when hinting multiple fonts compatibility.
    """,
)
@click.option(
    "-c",
    "--allow-changes",
    is_flag=True,
    help="""
    Allow changes to the glyph outlines.

    Paths are reordered to reduce hint substitution, and nearly straight curves
    are flattened.
    """,
)
@click.option(
    "-d",
    "--decimal",
    is_flag=True,
    help="""
    Use decimal coordinates.
    """,
)
@click.option(
    "-nf",
    "--no-flex",
    is_flag=True,
    help="""
    Suppress generation of flex commands.
    """,
)
@click.option(
    "-ns",
    "--no-hint-sub",
    is_flag=True,
    help="""
    Suppress hint substitution.
    """,
)
@click.option(
    "-nz",
    "--no-zones-stems",
    is_flag=True,
    help="""
    Allow the font to have no alignment zones nor stem widths.
    """,
)
@add_common_options()
def autohint(
    input_path: Path,
    reference_font: Path = None,
    allow_changes: bool = False,
    decimal: bool = False,
    no_flex: bool = False,
    no_hint_sub: bool = False,
    no_zones_stems: bool = False,
    optimize: bool = True,
    output_dir: bool = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Auto-hint OTF and PostScript flavored WOFF/WOFF2 fonts.
    """
    from fontTools.cffLib.specializer import specializeProgram
    from psautohint.autohint import ACOptions, hintFiles

    fonts = get_fonts_in_path(
        input_path=input_path, recalc_timestamp=recalc_timestamp, allow_ttf=False, allow_variable=False
    )
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for count, font in enumerate(fonts, start=1):
        t = time.time()
        print()
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            temp_otf_file = Path(makeOutputFileName(output_file, extension=".otf", suffix="_tmp", overWrite=True))

            generic_info_message(f"Auto-hinting file {count} of {len(fonts)}: {file.name} ")
            original_timestamp = font.modified_timestamp

            flavor = font.flavor
            if flavor:
                font.flavor = None
                font.save(temp_otf_file)
                input_file = temp_otf_file
            else:
                input_file = file

            font.close()

            options = ACOptions()
            options.inputPaths = [input_file]
            options.outputPaths = [output_file]
            options.reference_font = reference_font
            options.allowChanges = allow_changes
            options.round_coords = decimal
            options.noFlex = no_flex
            options.noHintSub = no_hint_sub
            options.allow_no_blues = no_zones_stems

            try:
                hintFiles(options=options)
            except Exception as e:
                generic_error_message(e)
                continue

            hinted_font = Font(output_file, recalcTimestamp=recalc_timestamp)

            if not recalc_timestamp:
                hinted_font.set_modified_timestamp(original_timestamp)

            if optimize:
                generic_info_message("Performing charstrings optimization")
                top_dict = hinted_font["CFF "].cff.topDictIndex[0]
                charstrings = top_dict.CharStrings
                for charstring in charstrings.values():
                    charstring.decompile()
                    charstring.program = specializeProgram(charstring.program)

                generic_info_message("Applying subroutines")
                hinted_font.otf_subroutinize()

            hinted_font.flavor = flavor

            hinted_font.save(output_file)
            hinted_font.close()
            temp_otf_file.unlink(missing_ok=True)
            generic_info_message(f"Done in {round(time.time() - t, 3)} seconds")
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)


@otf_tools.command()
@add_file_or_path_argument()
@click.option(
    "--no-subr",
    "subroutinize",
    is_flag=True,
    default=True,
    help="""
    Do not subroutinize dehinted fonts.
    """,
)
@click.option(
    "-d",
    "--dehinter",
    type=click.Choice(choices=("tx", "fonttools")),
    default="tx",
    show_default=True,
    help="""
    Use tx (default) or fontTools to remove hints.

    tx creates a temporary .cff file (tx -cff) removing hints (-n), preserving the glyph order (+d) and applying
    subroutines (+S). Then the .cff file is merged to the destination file using sfntedit, as explained here:
    https://github.com/adobe-type-tools/afdko/wiki/How-To#how-to-remove-hints-from-a-cff-based-otf. Finally, the
    temporary .cff file is deleted.

    fontTools uses the subset.cff.remove_hints() method to remove hints, and the font is subroutinized with cffsubr
    (subroutinization can be deactivated passing the --no-subr parameter).

    fontTools drops font-wide hinting values from the Private dict, while tx preserves them.
    """,
)
@add_common_options()
def dehint(
    input_path: Path,
    dehinter: str = "tx",
    subroutinize: bool = True,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Remove hints from CFF flavored (OTF, WOFF, WOFF2) fonts.
    """
    from afdko.fdkutils import run_shell_command

    fonts = get_fonts_in_path(input_path=input_path, allow_ttf=False, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        # Using fontTools.subset.cff.remove_hints()
        if dehinter == "fonttools":
            try:
                font.otf_dehint()
                if subroutinize:
                    font.otf_subroutinize()

                file = Path(font.reader.file.name)
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file)
            except Exception as e:
                generic_error_message(e)
            font.close()
            continue

        # Using tx -cff -n +b +/-S and then sfntedit -a to merge the CFF table to the destination file
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            temp_cff_file = Path(makeOutputFileName(output_file, extension=".cff", overWrite=True))
            temp_otf_file = Path(makeOutputFileName(output_file, extension=".otf", suffix="_tmp", overWrite=True))

            # If the font is WOFF or WOFF2, we need to convert to a temporary OTF font
            flavor = font.flavor
            if flavor:
                font.flavor = None
                font.save(temp_otf_file, reorderTables=False)
                font.close()
                input_file = temp_otf_file
            else:
                input_file = file

            tx_command = ["tx", "-cff", "-n", "+b"]
            if subroutinize:
                tx_command.append("+S")
            else:
                tx_command.append("-S")
            tx_command.extend([input_file, temp_cff_file])
            run_shell_command(tx_command, suppress_output=True)

            sfntedit_command = ["sfntedit", "-a", f"CFF={temp_cff_file}", input_file]
            if output_file != input_file:
                sfntedit_command.append(output_file)
            run_shell_command(sfntedit_command, suppress_output=True)

            # Convert the font back to WOFF/WOFF2
            if flavor:
                font = Font(output_file, recalcTimestamp=recalc_timestamp)
                font.flavor = flavor
                font.save(output_file)
                font.close()

            file_saved_message(output_file)
            temp_cff_file.unlink()
            temp_otf_file.unlink(missing_ok=True)

        except Exception as e:
            generic_error_message(e)


@otf_tools.command()
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
@click.option("--no-subr", "subroutinize", is_flag=True, default=True, help="""Do not subroutinize fixed fonts.""")
@click.option("--silent", "verbose", is_flag=True, default=True, help="Run in silent mode")
@add_common_options()
def fix_contours(
    input_path: Path,
    min_area: int = 25,
    subroutinize: bool = True,
    verbose: bool = True,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Fix contours by correcting contours direction, removing overlaps and tiny paths.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, allow_variable=False, allow_ttf=False, recalc_timestamp=recalc_timestamp
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
            font.otf_fix_contours(min_area=min_area, verbose=verbose)
            if subroutinize:
                font.otf_subroutinize()
            font.save(output_file)
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@otf_tools.command()
@add_file_or_path_argument()
@add_common_options()
def fix_version(input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overwrite: bool = True):
    """
    Aligns CFF topDict version string to the head.fontRevision value.

    For example, if head.fontRevision value is 2.001, CFF topDict version value will be 2.1.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recalc_timestamp=recalc_timestamp, allow_ttf=False, allow_variable=False
    )
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            cff_table = font["CFF "]
            cff_table_copy = deepcopy(cff_table)

            font.fix_cff_top_dict_version()

            if cff_table_copy.compile(font) != cff_table.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)
        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@otf_tools.command()
@add_file_or_path_argument()
@add_common_options()
def subr(input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True):
    """
    Subroutinize OpenType-PS fonts.
    """
    fonts = get_fonts_in_path(input_path=input_path, allow_ttf=False, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            font.otf_subroutinize()
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@otf_tools.command()
@add_file_or_path_argument()
@add_common_options()
def desubr(input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True):
    """
    Desubroutinize OpenType-PS fonts.
    """
    fonts = get_fonts_in_path(input_path=input_path, allow_ttf=False, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            font.otf_desubroutinize()
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@otf_tools.command()
@add_file_or_path_argument()
@click.option("-q", "--quiet-mode", is_flag=True, help="Run in quiet mode.")
@add_common_options()
def check_outlines(
    input_path: Path,
    quiet_mode: bool = False,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Performs outline quality checks and overlaps removal with checkoutlinesufo.
    """

    from afdko import checkoutlinesufo

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp, allow_ttf=False)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        print()
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            generic_info_message(f"Checking file {file.name}")

            flavor = font.flavor
            if flavor:
                font.flavor = None
                font.save(output_file)

            if not file == output_file:
                font.save(output_file)

            font.close()

            args = [output_file.as_posix(), "--error-correction-mode"]
            if quiet_mode:
                args.append("--quiet-mode")
            checkoutlinesufo.run(args=args)

            if flavor:
                font = Font(output_file, recalcTimestamp=recalc_timestamp)
                font.flavor = flavor
                font.save(output_file)

            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[otf_tools],
    help="""
    A set of tools to manipulate fonts with PostScript outlines.
    """,
)

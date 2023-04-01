import os
import time
from io import BytesIO

import cffsubr
import click
from afdko import checkoutlinesufo
from afdko.fdkutils import run_shell_command
from dehinter.font import dehint
from fontTools.cffLib.specializer import specializeProgram
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.subset import Subsetter
from fontTools.ttLib.removeOverlaps import removeOverlaps
from pathvalidate import sanitize_filepath, sanitize_filename

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import get_fonts_list, check_output_dir, get_output_dir
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    generic_error_message,
    file_saved_message,
    file_not_changed_message,
    generic_info_message, no_valid_fonts_message,
)


@click.group()
def add_dummy_dsig():
    pass


@add_dummy_dsig.command()
@add_file_or_path_argument()
@add_common_options()
def add_dsig(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Adds a dummy DSIG table to fonts, unless the table is already present. WOFF2 flavored fonts are ignored, since
    encoders must remove the DSIG table from woff2 font data.
    """
    files = get_fonts_list(input_path, allow_extensions=[".otf", ".ttf", ".woff"])

    if len(files) == 0:
        no_valid_fonts_message(input_path)
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            if "DSIG" not in font.keys():
                font.add_dummy_dsig()
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(f"DSIG table is already present in {os.path.basename(file)}")
        except Exception as e:
            generic_error_message(e)


@click.group()
def organizer():
    pass


@organizer.command()
@add_file_or_path_argument()
@click.option(
    "--rename-source",
    type=click.Choice(choices=["1", "2", "3", "4", "5"]),
    default=None,
    help="""
    Renames the font files according to the provided source string(s). See ftcli utils font-renamer.
    """,
)
@click.option(
    "-ext",
    "--extension",
    "sort_by_extension",
    is_flag=True,
    help="Sorts fonts by extension.",
)
@click.option("-ver", "--version", "sort_by_version", is_flag=True, help="Sorts fonts by version.")
def font_organizer(input_path, rename_source=None, sort_by_extension=False, sort_by_version=False):
    """
    Organizes fonts by moving them into a subdirectory named after the font's family name, and eventually a subdirectory
    named after the font's extension and version.
    """

    files = get_fonts_list(input_path)
    if len(files) == 0:
        no_valid_fonts_message(input_path)
        return

    for file in files:
        try:
            font = Font(file)
            family_name = font.guess_family_name()
            extension = font.get_real_extension()
            file_name = os.path.basename(file)
            if rename_source:
                file_name = f"{font.get_file_name(source=int(rename_source))}{extension}"

            version_string = font.name_table.getDebugName(5).replace("Version ", "v").split(";")[0]

            output_dir = os.path.join(os.path.dirname(file), family_name)
            if sort_by_version:
                output_dir = f"{output_dir} {version_string}"

            if sort_by_extension:
                output_dir = os.path.join(output_dir, f"{extension}"[1:].lower())

            output_file = makeOutputFileName(file_name, outputDir=output_dir, overWrite=False)
            output_file = sanitize_filepath(output_file, platform="auto")
            os.renames(file, output_file)
            generic_info_message(f"{os.path.basename(file)} moved")

        except Exception as e:
            generic_error_message(e)


@click.group()
def renamer():
    pass


@renamer.command()
@add_file_or_path_argument()
@click.option(
    "-s",
    "--source",
    type=click.Choice(choices=["1", "2", "3", "4", "5"]),
    default="1",
    help="""
              The source string(s) from which to extract the new file name. Default is 1 (FamilyName-StyleName), used
              also as fallback name when 4 or 5 are passed but the font is TrueType
              
              \b
              1: FamilyName-StyleName
              2: PostScript Name
              3: Full Font Name
              4: CFF TopDict fontNames (CFF fonts only)
              5: CFF TopDict FullName (CFF fonts only)
              """,
)
def font_renamer(input_path, source):
    """
    Takes a path to a single font file or directory of font files, extracts each font's metadata according to the
    `--source` parameter passed by the user, and renames the font file to match the metadata, adding the correct
    extension.
    """

    files = get_fonts_list(input_path=input_path)

    # Conversion to integer is needed because click.Choice() only accepts strings
    source = int(source)

    for file in files:
        try:
            font = Font(file)

            # Read the PostScript Name if the user passed 4 or 5 but the font isn't CFF
            if font.is_true_type:
                if source in (4, 5):
                    source = 1

            old_file_name, old_extension = os.path.splitext(os.path.basename(font.file))

            new_file_name = sanitize_filename(font.get_file_name(source=source), platform="auto")
            new_extension = font.get_real_extension()

            output_file = os.path.join(os.path.dirname(file), f"{new_file_name}{new_extension}")

            if f"{new_file_name}{new_extension}" != f"{old_file_name}{old_extension}":
                try:
                    output_file = makeOutputFileName(output_file, outputDir=os.path.dirname(file), overWrite=True)
                    os.renames(file, output_file)
                except FileExistsError:
                    output_file = makeOutputFileName(output_file, outputDir=os.path.dirname(file), overWrite=False)
                    os.renames(file, output_file)
                file_saved_message(f"{os.path.basename(file)} --> {os.path.basename(output_file)}")
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def ttf_autohinter():
    pass


@ttf_autohinter.command()
@add_file_or_path_argument()
@add_common_options()
def ttf_autohint(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Autohints TrueType fonts using ttfautohint-py.
    """

    from ttfautohint import ttfautohint

    files = get_fonts_list(input_path, allow_cff=False, allow_variable=False)
    if len(files) == 0:
        generic_error_message(f"No valid TrueType font files found in {input_path}.")
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            buf = BytesIO()
            font.save(buf)
            data = ttfautohint(in_buffer=buf.getvalue(), no_info=True)
            hinted_font = Font(BytesIO(data))
            if recalcTimestamp is False:
                hinted_font.head_table.modified = font.head_table.modified
            output_file = makeOutputFileName(font.file, outputDir=output_dir, overWrite=overWrite)
            hinted_font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def ttf_dehinter():
    pass


@ttf_dehinter.command()
@add_file_or_path_argument()
@click.option("--keep-cvar", is_flag=True, default=False, help="keep cvar table")
@click.option("--keep-cvt", is_flag=True, default=False, help="keep cvt table")
@click.option("--keep-fpgm", is_flag=True, default=False, help="keep fpgm table")
@click.option("--keep-hdmx", is_flag=True, default=False, help="keep hdmx table")
@click.option("--keep-ltsh", is_flag=True, default=False, help="keep LTSH table")
@click.option("--keep-prep", is_flag=True, default=False, help="keep prep table")
@click.option("--keep-ttfa", is_flag=True, default=False, help="keep ttfa table")
@click.option("--keep-vdmx", is_flag=True, default=False, help="keep vdmx table")
@click.option("--keep-glyf", is_flag=True, default=False, help="do not modify glyf table")
@click.option("--keep-gasp", is_flag=True, default=False, help="do not modify gasp table")
@click.option("--keep-maxp", is_flag=True, default=False, help="do not modify maxp table")
@click.option("--keep-head", is_flag=True, default=False, help="do not modify head table")
@click.option("--verbose", is_flag=True, default=False, help="display standard output")
@add_common_options()
def ttf_dehint(
    input_path,
    keep_cvar: bool,
    keep_cvt: bool,
    keep_fpgm: bool,
    keep_hdmx: bool,
    keep_ltsh: bool,
    keep_prep: bool,
    keep_ttfa: bool,
    keep_vdmx: bool,
    keep_glyf: bool,
    keep_gasp: bool,
    keep_maxp: bool,
    keep_head: bool,
    verbose: bool,
    outputDir=None,
    recalcTimestamp=False,
    overWrite=True,
):
    """Drops hinting from TrueType fonts.

    This is a CLI for dehinter by Source Foundry: https://github.com/source-foundry/dehinter
    """

    files = get_fonts_list(input_path, allow_cff=False)

    if len(files) == 0:
        generic_error_message(f"No valid TrueType font files found in {input_path}.")
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            dehint(
                font,
                keep_cvar=keep_cvar,
                keep_cvt=keep_cvt,
                keep_fpgm=keep_fpgm,
                keep_gasp=keep_gasp,
                keep_glyf=keep_glyf,
                keep_head=keep_head,
                keep_hdmx=keep_hdmx,
                keep_ltsh=keep_ltsh,
                keep_maxp=keep_maxp,
                keep_prep=keep_prep,
                keep_ttfa=keep_ttfa,
                keep_vdmx=keep_vdmx,
                verbose=verbose,
            )
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
            font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def ttf_overlaps_remover():
    pass


@ttf_overlaps_remover.command()
@add_file_or_path_argument()
@click.option(
    "--ignore-errors",
    is_flag=True,
    help="""
              Ignore errors while removing overlaps.
              """,
)
@add_common_options()
def ttf_remove_overlaps(input_path, ignore_errors, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Simplify glyphs in TrueType fonts by merging overlapping contours.
    """

    files = get_fonts_list(input_path, allow_cff=False, allow_variable=False)
    if len(files) == 0:
        generic_error_message(f"No valid TrueType font files found in {input_path}.")
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(font.file, outputDir=output_dir, overWrite=overWrite)
            removeOverlaps(font, removeHinting=True, ignoreErrors=ignore_errors)
            font.save(output_file)
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def cff_check_outlines_ufo():
    pass


@cff_check_outlines_ufo.command()
@add_file_or_path_argument()
@add_common_options()
def cff_check_outlines(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Performs afdko.checkoutlinesufo outline quality checks and overlaps removal. Supports CFF fonts only.
    """

    files = get_fonts_list(input_path, allow_ttf=False, allow_variable=False)
    if len(files) == 0:
        generic_error_message(f"No valid CFF font files found in {input_path}.")
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        print()
        generic_info_message(f"Checking file {os.path.basename(file)}")
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(font.file, outputDir=output_dir, overWrite=overWrite)
            font.save(output_file)
            checkoutlinesufo.run(args=[output_file, "--error-correction-mode", "--quiet-mode"])
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def cff_autohinter():
    pass


@cff_autohinter.command()
@add_file_or_path_argument()
@click.option(
    "--optimize/--no-optimize",
    default=True,
    help="""
              Optimize the hinted font by specializing the charstrings and applying subroutines.
              """,
)
@add_common_options()
def cff_autohint(input_path, optimize=True, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Autohints CFF fonts with psautohint.
    """

    files = get_fonts_list(input_path, allow_extensions=[".otf"])
    if len(files) == 0:
        generic_error_message(f"No valid CFF font files found in {input_path}.")
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    start_time = time.time()
    counter = 0
    for file in files:
        t = time.time()
        counter += 1
        try:
            print()
            generic_info_message(f"Autohinting file {os.path.basename(file)}: {counter} of {len(files)}")
            font = Font(file, recalcTimestamp=recalcTimestamp)
            original_timestamp = font.head_table.modified
            output_file = makeOutputFileName(font.file, outputDir=output_dir, overWrite=overWrite)
            font.save(output_file)
            font.close()
            run_shell_command(["psautohint", output_file, "--no-zones-stems"], suppress_output=False)

            if not recalcTimestamp:
                tmp_font = Font(output_file, recalcTimestamp=False)
                tmp_font.head_table.modified = original_timestamp
                tmp_font.save(output_file)

            if optimize:
                generic_info_message("Performing charstrings optimization")
                otf = Font(output_file, recalcTimestamp=recalcTimestamp)
                top_dict = otf["CFF "].cff.topDictIndex[0]
                charstrings = top_dict.CharStrings
                for charstring in charstrings.values():
                    charstring.decompile()
                    charstring.program = specializeProgram(charstring.program)
                cffsubr.subroutinize(otf, keep_glyph_names=False)
                otf.save(output_file)

            generic_info_message(f"Done in {round(time.time() - t, 3)}")
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)

    print()
    generic_info_message(f"Total files  : {len(files)}")
    generic_info_message(f"Elapsed time : {round(time.time() - start_time, 3)} seconds")


@click.group()
def cff_dehinter():
    pass


@cff_dehinter.command()
@add_file_or_path_argument()
@add_common_options()
def cff_dehint(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Drops hinting from CFF fonts.
    """
    files = get_fonts_list(input_path, allow_ttf=False, allow_variable=False)
    if len(files) == 0:
        generic_error_message(f"No valid CFF font files found in {input_path}.")
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            subsetter = Subsetter()
            subsetter.options.drop_tables = []
            subsetter.options.passthrough_tables = True
            subsetter.options.name_IDs = "*"
            subsetter.options.name_legacy = True
            subsetter.options.name_languages = "*"
            subsetter.options.layout_features = "*"
            subsetter.options.hinting = False
            subsetter.glyph_ids_requested = [i for i in font.getReverseGlyphMap().values()]
            Subsetter.subset(subsetter, font)

            output_file = makeOutputFileName(font.file, outputDir=output_dir, overWrite=overWrite)
            font.save(output_file)
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def cff_subroutinize():
    pass


@cff_subroutinize.command()
@add_file_or_path_argument()
@add_common_options()
def cff_subr(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Subroutinize CFF fonts.
    """

    files = get_fonts_list(input_path, allow_extensions=[".otf"])
    if len(files) == 0:
        no_valid_fonts_message(input_path)
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            cffsubr.subroutinize(otf=font, keep_glyph_names=False)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
            font.save(output_file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def cff_desubroutinize():
    pass


@cff_desubroutinize.command()
@add_file_or_path_argument()
@add_common_options()
def cff_desubr(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Desoubroutinize CFF fonts.
    """
    files = get_fonts_list(input_path, allow_extensions=[".otf"])
    if len(files) == 0:
        no_valid_fonts_message(input_path)
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            cffsubr.desubroutinize(otf=font)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
            font.save(output_file)
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)


cli = click.CommandCollection(
    sources=[
        add_dummy_dsig,
        organizer,
        renamer,
        ttf_overlaps_remover,
        ttf_dehinter,
        ttf_autohinter,
        cff_check_outlines_ufo,
        cff_autohinter,
        cff_dehinter,
        cff_subroutinize,
        cff_desubroutinize,
    ],
    help="""Miscellaneous utilities.""",
)

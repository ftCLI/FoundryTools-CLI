import os
import time

import click
import fontTools.ttLib
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import check_output_dir, check_input_path
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    generic_error_message,
    generic_info_message,
    file_saved_message,
    select_instance_coordinates,
)


@click.group()
def ttf_to_otf():
    pass


@ttf_to_otf.command()
@add_file_or_path_argument()
@click.option(
    "-t",
    "--tolerance",
    type=click.FloatRange(0, 2.5),
    default=1,
    help="""
              Conversion tolerance (0-2.5, default 1). Low tolerance adds more points but keeps shapes. High tolerance
              adds few points but may change shape.
              """,
)
@click.option(
    "--safe",
    "safe_mode",
    is_flag=True,
    help="""
              Sometimes Qu2CuPen may fail or produce distorted outlines. Most of times, use of '--safe' will prevent
              errors by converting the source TTF font to a temporary OTF built using T2CharstringsPen, and then
              reconverting it to a temporary TTF font. This last one will be used for TTF to OTF conversion instead of
              the source TTF file. This is slower, but safest.
    """,
)
@click.option(
    "--scale-upm",
    is_flag=True,
    help="""
              Scale units-per-em to 1000
    """
)
@click.option(
    "--keep-glyphs",
    "purge_glyphs",
    is_flag=True,
    default=True,
    help="""
              Keeps NULL and CR glyphs from the output font
              """,
)
@click.option(
    "--no-subr",
    "subroutinize",
    is_flag=True,
    default=True,
    help="""
              Do not subroutinize converted fonts
              """,
)
@click.option(
    "--check-outlines",
    is_flag=True,
    help="""
              Performs optional outline quality checks and removes overlaps with afdko.checkoutlinesufo
              """,
)
@add_common_options()
def ttf2otf(
    input_path,
    tolerance=1,
    safe_mode=False,
    scale_upm=False,
    purge_glyphs=False,
    subroutinize=True,
    check_outlines=False,
    outputDir=None,
    recalcTimestamp=False,
    overWrite=True,
):
    """
    Converts TTF fonts (or TrueType flavored woff/woff2 web fonts) to OTF fonts (or CFF flavored woff/woff2 web fonts).
    """

    from ftCLI.Lib.converters.ttf_to_otf import TrueTypeToCFF

    files = check_input_path(input_path, allow_variable=False, allow_cff=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    from ftCLI.Lib.converters.ttf_to_otf import JobRunner_ttf2otf
    converter = JobRunner_ttf2otf(files=files)
    converter.options.tolerance = tolerance
    converter.options.output_dir = output_dir
    converter.options.overwrite = overWrite
    converter.options.subroutinize = subroutinize
    converter.options.check_outlines = check_outlines
    converter.options.safe_mode = safe_mode
    converter.options.remove_glyphs = purge_glyphs
    converter.options.scale_upm = scale_upm
    converter.options.recalc_timestamp = recalcTimestamp
    converter.run()


@click.group()
def otf_2_ttf():
    pass


@otf_2_ttf.command()
@add_file_or_path_argument()
@click.option(
    "--max-err", type=click.FloatRange(0.1, 3.0), default=1.0, help="""Approximation error, measured in UPEM"""
)
@add_common_options()
def otf2ttf(input_path, max_err, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Converts fonts from OTF to TTF format.
    """
    from ftCLI.Lib.converters.otf_to_ttf import CFFToTrueType

    files = check_input_path(input_path, allow_variable=False, allow_ttf=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    start_time = time.time()
    counter = 0
    converted_files = 0

    for file in files:
        t = time.time()
        counter += 1
        generic_info_message(f"Converting file {counter} of {len(files)}")
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            converter = CFFToTrueType(font=font)
            converter.options.max_err = max_err
            ttf_font = converter.run()

            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite, extension=".ttf")
            ttf_font.save(output_file)
            converted_files += 1

            generic_info_message(f"Done in {round(time.time() - t, 3)}")
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)

    print()
    generic_info_message(f"Total files       : {len(files)}")
    generic_info_message(f"Converted files   : {converted_files}")
    generic_info_message(f"Elapsed time      : {round(time.time() - start_time, 3)} seconds")


@click.group()
def web_to_sfnt():
    pass


@web_to_sfnt.command()
@add_file_or_path_argument()
@click.option(
    "-f",
    "--flavor",
    type=click.Choice(choices=["woff", "woff2"]),
    help="""
              By default, the script converts both woff and woff2 flavored web fonts to SFNT fonts (TrueType or
              OpenType). Use this option to convert only woff or woff2 flavored web fonts.
              """,
)
@click.option(
    "-d",
    "--delete-source-file",
    is_flag=True,
    help="""
              Deletes the source files after conversion.
              """,
)
@add_common_options()
def wf2ft(
    input_path,
    flavor=None,
    delete_source_file=False,
    outputDir=None,
    recalcTimestamp=False,
    overWrite=True,
):
    """
    Converts web fonts (WOFF and WOFF2) to SFNT fonts (TTF or OTF)
    """
    from ftCLI.Lib.converters.web_to_sfnt import WebToSFNT

    if not flavor:
        allowed_extensions = [".woff", ".woff2"]
    else:
        allowed_extensions = [f".{flavor}"]

    files = check_input_path(input_path, allow_extensions=allowed_extensions)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            web_font = Font(file, recalcTimestamp=recalcTimestamp)

            converter = WebToSFNT(font=web_font)
            desktop_font = converter.run()

            new_extension = desktop_font.get_real_extension()
            output_file = makeOutputFileName(
                file, extension=new_extension, outputDir=output_dir, overWrite=overWrite
            )
            desktop_font.save(output_file, reorderTables=False)
            if delete_source_file:
                os.remove(file)
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def sfnt_to_web():
    pass


@web_to_sfnt.command()
@add_file_or_path_argument()
@click.option(
    "-f",
    "--flavor",
    type=click.Choice(choices=["woff", "woff2"]),
    help="""
              By default, the script converts SFNT fonts (TrueType or OpenType) both to woff and woff2 flavored web
              fonts. Use this option to create only woff (--flavor woff) or woff2 (--flavor woff2) files.
              """,
)
@add_common_options()
def ft2wf(input_path, flavor=None, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Converts SFNT fonts (TTF or OTF) to web fonts (WOFF and/or WOFF2)
    """
    from ftCLI.Lib.converters.sfnt_to_web import SFNTToWeb

    files = check_input_path(input_path, allow_extensions=[".otf", ".ttf"])
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    output_flavors = ["woff", "woff2"]
    if flavor is not None:
        output_flavors = [flavor]

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            if font.flavor is not None:
                continue
            for flavor in output_flavors:
                font.flavor = flavor
                converter = SFNTToWeb(font=font, flavor=flavor)
                web_font = converter.run()
                extension = web_font.get_real_extension()
                output_file = makeOutputFileName(file, extension=extension, outputDir=output_dir, overWrite=overWrite)
                web_font.save(output_file, reorderTables=False)
                file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def ttc_to_sfnt():
    pass


@ttc_to_sfnt.command()
@add_file_or_path_argument()
@add_common_options()
def ttc2sfnt(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Extracts each font from a TTC file, and saves it as a TTF or OTF file.
    """
    from fontTools.ttLib import TTCollection

    if os.path.isfile(input_path):
        files = [input_path]
    elif os.path.isdir(input_path):
        files = [os.path.join(input_path, file) for file in os.listdir(input_path)]
    else:
        generic_error_message(f"Invalid path: {input_path}")
        return

    ttc_files = []
    for file in files:
        try:
            ttc_font = TTCollection(file)
            ttc_files.append(file)
            ttc_font.close()
        except fontTools.ttLib.TTLibError:
            pass

    if len(ttc_files) == 0:
        generic_error_message(f"No valid .ttc font files found in {input_path}.")
        return

    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for ttc_file in ttc_files:
        try:
            ttc_font = TTCollection(ttc_file)
            for font in ttc_font.fonts:
                font.recalcTimestamp = recalcTimestamp
                file_name = font["name"].getDebugName(6)
                extension = ".otf" if font.sfntVersion == "OTTO" else ".ttf"
                output_file = makeOutputFileName(
                    file_name,
                    extension=extension,
                    outputDir=output_dir,
                    overWrite=overWrite,
                )
                font.save(output_file)
                file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def variable_to_static():
    pass


@variable_to_static.command()
@add_file_or_path_argument()
@click.option(
    "-s",
    "--select-instance",
    is_flag=True,
    default=False,
    help="""
              By default, the script exports all named instances. Use this option to select custom axis values
              for a single instance.
              """,
)
@click.option(
    "--no-cleanup",
    "cleanup",
    is_flag=True,
    default=True,
    help="""
              By default, STAT table is dropped and axis nameIDs are deleted from name table. Use --no-cleanup to keep
              STAT table and prevent axis nameIDs to be deleted from name table.""",
)
@click.option(
    "--update-name-table",
    is_flag=True,
    default=True,
    help="""
              Update the instantiated font's `name` table. Input font must have a STAT table with Axis Value Tables
              """,
)
@add_common_options()
def var2static(
    input_path,
    select_instance=False,
    cleanup=True,
    update_name_table=False,
    outputDir=None,
    recalcTimestamp=False,
    overWrite=True,
):
    """
    Exports static instances from variable fonts.
    """

    from ftCLI.Lib.VFont import VariableFont
    from ftCLI.Lib.converters.variable_to_static import VariableToStatic
    from fontTools.ttLib.tables._f_v_a_r import NamedInstance

    files = check_input_path(input_path, allow_static=False, allow_cff=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    start_time = time.time()
    for file in files:
        print()
        generic_info_message(f"Converting file {os.path.basename(file)}")
        try:
            variable_font = VariableFont(file, recalcTimestamp=recalcTimestamp)

            converter = VariableToStatic()
            converter.options.cleanup = cleanup
            converter.options.update_name_table = update_name_table
            converter.options.output_dir = output_dir
            converter.options.overwrite = overWrite

            instances = variable_font.get_instances()
            if select_instance:
                axes = variable_font.get_axes()
                selected_coordinates = select_instance_coordinates(axes)
                is_named_instance = selected_coordinates in [i.coordinates for i in instances]
                if not is_named_instance:
                    # Set update_name_table value to False because we won't find this Axis Value in the STAT table.
                    converter.options.update_name_table = False
                    selected_instance = NamedInstance()
                    selected_instance.coordinates = selected_coordinates
                else:
                    # In case there are several instances with the same coordinates, return only the first one.
                    #
                    # From https://learn.microsoft.com/en-us/typography/opentype/spec/fvar#instancerecord:
                    #
                    # All the instance records in a font should have distinct coordinates and distinct
                    # subfamilyNameID and postScriptName ID values. If two or more records share the same coordinates,
                    # the same nameID values or the same postScriptNameID values, then all but the first can be ignored.
                    selected_instance = [i for i in instances if i.coordinates == selected_coordinates][0]

                instances = [selected_instance]

            converter.run(variable_font=variable_font, instances=instances)

        except Exception as e:
            generic_error_message(e)

        generic_info_message(f"Total files     : {len(files)}")
        generic_info_message(f"Elapsed time    : {round(time.time() - start_time)} seconds")


cli = click.CommandCollection(
    sources=[
        otf_2_ttf,
        ttf_to_otf,
        web_to_sfnt,
        sfnt_to_web,
        variable_to_static,
        ttc_to_sfnt,
    ],
    help="""
Font converter.
""",
)

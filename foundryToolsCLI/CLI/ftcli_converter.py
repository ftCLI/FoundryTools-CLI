import typing as t

from pathlib import Path

import click

from foundryToolsCLI.Lib.utils.cli_tools import (
    get_fonts_in_path,
    initial_check_pass,
    get_variable_fonts_in_path,
)
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    add_recursive_option,
    select_instance_coordinates,
)
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.timer import Timer

font_converter = click.Group("subcommands")


@font_converter.command()
@add_file_or_path_argument()
@click.option(
    "-t",
    "--tolerance",
    type=click.FloatRange(0.0, 3.0),
    default=1.0,
    help="""
    Conversion tolerance (0.0-3.0, default 1.0). Low tolerance adds more points but keeps shapes.
    High tolerance adds  few points but may change shape.
    """,
)
@click.option(
    "--scale-upm",
    type=click.IntRange(16, 16384, max_open=True),
    help="Scale the units-per-em of converted fonts.",
)
@click.option(
    "--no-subr",
    "subroutinize",
    is_flag=True,
    default=True,
    help="Do not subroutinize converted fonts.",
)
@click.option("--silent", "verbose", is_flag=True, default=True, help="Run in silent mode")
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def ttf2otf(
    input_path: Path,
    tolerance: float = 1.0,
    scale_upm: t.Optional[int] = None,
    subroutinize: bool = True,
    recalc_timestamp: bool = False,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
    verbose: bool = True,
):
    """
    Converts TTF fonts to OTF (or TrueType flavored woff/woff2 web fonts to PostScript flavored
    woff/woff2 web fonts).
    """
    fonts = get_fonts_in_path(
        input_path=input_path,
        recursive=recursive,
        allow_cff=False,
        allow_variable=False,
        recalc_timestamp=recalc_timestamp,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    from foundryToolsCLI.Lib.converters.ttf_to_otf import TTF2OTFRunner

    runner = TTF2OTFRunner()
    runner.options.tolerance = tolerance
    runner.options.scale_upm = scale_upm
    runner.options.subroutinize = subroutinize
    runner.options.recalc_timestamp = recalc_timestamp
    runner.options.output_dir = output_dir
    runner.options.overwrite = overwrite
    runner.options.verbose = verbose
    runner.run(source_fonts=fonts)


@font_converter.command()
@add_file_or_path_argument()
@click.option(
    "--max-err",
    type=click.FloatRange(0.1, 3.0),
    default=1.0,
    help="Approximation error, measured in UPEM",
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def otf2ttf(
    input_path: Path,
    max_err: float = 1.0,
    recalc_timestamp: bool = False,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Converts OTF fonts to TTF (or PostScripts flavored woff/woff2 web fonts to TrueType flavored
    woff/woff2 web fonts).
    """
    fonts = get_fonts_in_path(
        input_path=input_path,
        recursive=recursive,
        allow_ttf=False,
        allow_variable=False,
        recalc_timestamp=recalc_timestamp,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    from foundryToolsCLI.Lib.converters.otf_to_ttf import OTF2TTFRunner

    runner = OTF2TTFRunner()
    runner.options.max_err = max_err
    runner.options.output_dir = output_dir
    runner.options.overwrite = overwrite
    runner.run(source_fonts=fonts)


@font_converter.command()
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
    By default, STAT table is dropped and axis nameIDs are deleted from name table. Use --no-cleanup
    to keep STAT table and prevent axis nameIDs to be deleted from name table.
    """,
)
@click.option(
    "--no-update-name-table",
    "update_name_table",
    is_flag=True,
    default=True,
    help="""
    Prevent updating instantiated fonts `name` table. Input fonts must have a STAT table with Axis
    Value Tables.
    """,
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def vf2i(
    input_path: Path,
    select_instance: bool = False,
    cleanup: bool = True,
    update_name_table: bool = True,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Exports static instances from variable fonts.
    """
    variable_fonts = get_variable_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=variable_fonts, output_dir=output_dir):
        return

    from foundryToolsCLI.Lib.converters.variable_to_static import VariableToStatic
    from fontTools.ttLib.tables._f_v_a_r import NamedInstance

    for variable_font in variable_fonts:
        file = Path(variable_font.reader.file.name)
        logger.opt(colors=True).info(Logs.converting_file, file=file.name)

        try:
            converter = VariableToStatic()
            converter.options.cleanup = cleanup
            converter.options.update_name_table = update_name_table
            converter.options.output_dir = output_dir
            converter.options.overwrite = overwrite

            instances = variable_font.get_instances()
            if select_instance:
                axes = variable_font.get_axes()
                selected_coordinates = select_instance_coordinates(axes)
                is_named_instance = selected_coordinates in [i.coordinates for i in instances]
                if not is_named_instance:
                    # Set update_name_table value to False because we won't find this Axis Value in
                    # the STAT table.
                    converter.options.update_name_table = False
                    selected_instance = NamedInstance()
                    selected_instance.coordinates = selected_coordinates
                else:
                    # In case there are several instances with the same coordinates, return only the
                    # first one.
                    #
                    # https://learn.microsoft.com/en-us/typography/opentype/spec/fvar#instancerecord
                    #
                    # All the instance records in a font should have distinct coordinates and
                    # distinct subfamilyNameID and postScriptName ID values. If two or more records
                    # share the same coordinates, the same nameID values or the same
                    # postScriptNameID values, then all but the first can be ignored.
                    selected_instance = [
                        i for i in instances if i.coordinates == selected_coordinates
                    ][0]

                instances = [selected_instance]

            converter.run(variable_font=variable_font, instances=instances)

        except Exception as e:
            logger.exception(e)


@font_converter.command()
@add_file_or_path_argument()
@click.option(
    "-f",
    "--flavor",
    type=click.Choice(choices=["woff", "woff2"]),
    help="""
    By default, the script converts both woff and woff2 flavored web fonts to SFNT fonts (TrueType
    or OpenType). Use this option to convert only woff or woff2 flavored web fonts.
    """,
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def wf2ft(
    input_path: Path,
    flavor: t.Optional[str] = None,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Converts web fonts (WOFF and WOFF2) to SFNT fonts (TTF or OTF)
    """

    if not flavor:
        allowed_extensions = [".woff", ".woff2"]
    else:
        allowed_extensions = [f".{flavor}"]

    fonts = get_fonts_in_path(
        input_path=input_path,
        recursive=recursive,
        allow_extensions=allowed_extensions,
        recalc_timestamp=recalc_timestamp,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    from foundryToolsCLI.Lib.converters.web_to_sfnt import WF2FTRunner

    converter = WF2FTRunner()

    input_flavors = ["woff", "woff2"]
    if flavor is not None:
        input_flavors = [flavor]

    converter.options.woff = True if "woff" in input_flavors else False
    converter.options.woff2 = True if "woff2" in input_flavors else False
    converter.options.recalc_timestamp = recalc_timestamp
    converter.options.output_dir = output_dir
    converter.options.overwrite = overwrite
    converter.run(fonts=fonts)


@font_converter.command()
@add_file_or_path_argument()
@click.option(
    "-f",
    "--flavor",
    type=click.Choice(choices=["woff", "woff2"]),
    help="""
    By default, the script converts SFNT fonts (TrueType or OpenType) both to woff and woff2
    flavored web fonts. Use this option to create only woff (--flavor woff) or woff2
    (--flavor woff2) files.
    """,
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def ft2wf(
    input_path: Path,
    flavor: t.Optional[str] = None,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp=False,
    overwrite=True,
):
    """
    Converts SFNT fonts (TTF or OTF) to web fonts (WOFF and/or WOFF2)
    """

    fonts = get_fonts_in_path(
        input_path=input_path,
        allow_extensions=[".otf", ".ttf"],
        recalc_timestamp=recalc_timestamp,
        recursive=recursive,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    from foundryToolsCLI.Lib.converters.sfnt_to_web import FT2WFRunner

    converter = FT2WFRunner()

    output_flavors = ["woff", "woff2"]
    if flavor is not None:
        output_flavors = [flavor]

    converter.options.woff = True if "woff" in output_flavors else False
    converter.options.woff2 = True if "woff2" in output_flavors else False
    converter.options.recalc_timestamp = recalc_timestamp
    converter.options.output_dir = output_dir
    converter.options.overwrite = overwrite
    converter.run(fonts=fonts)


@font_converter.command()
@add_file_or_path_argument()
@add_common_options()
@Timer(logger=logger.info)
def ttc2sfnt(
    input_path: Path,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Extracts each font from a TTC file, and saves it as a TTF or OTF file.
    """
    from fontTools.ttLib import TTCollection, TTLibError

    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        files = [p.resolve() for p in input_path.iterdir() if p.is_file()]
    else:
        logger.error(f"Invalid path: {input_path}")
        return

    tt_collections: list[TTCollection] = []
    for file in files:
        try:
            ttc_font = TTCollection(file)
            tt_collections.append(ttc_font)
        except (TTLibError, Exception):
            pass

    if not initial_check_pass(fonts=tt_collections, output_dir=output_dir):
        return

    from foundryToolsCLI.Lib.converters.ttc_to_sfnt import TTC2SFNTRunner

    converter = TTC2SFNTRunner()
    converter.options.recalc_timestamp = recalc_timestamp
    converter.options.output_dir = output_dir
    converter.options.overwrite = overwrite
    converter.run(tt_collections=tt_collections)


cli = click.CommandCollection(
    sources=[font_converter],
    help="""
    Font converter.
    """,
)

from pathlib import Path
from typing import Any, Literal, Optional

import click
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib.tables._f_v_a_r import Axis, NamedInstance
from foundrytools import Font, FontFinder
from foundrytools.app.var2static import (
    BadInstanceError,
    UpdateNameTableError,
    Var2StaticError,
    check_update_name_table,
)
from foundrytools.app.var2static import run as var2static
from foundrytools.constants import WOFF2_FLAVOR, WOFF_FLAVOR
from pathvalidate import sanitize_filename

from foundrytools_cli.commands.converter.ttf_to_otf import ttf2otf, ttf2otf_with_tx
from foundrytools_cli.utils import BaseCommand, choice_to_int_callback
from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.task_runner import TaskRunner
from foundrytools_cli.utils.timer import Timer


def _select_instance_coordinates(axes: list[Axis]) -> NamedInstance:
    click.secho("\nSelect coordinates:")
    selected_coordinates = {}
    selected_instance = NamedInstance()
    for a in axes:
        axis_tag = a.axisTag
        min_value = a.minValue
        max_value = a.maxValue
        coordinates = click.prompt(
            f"{axis_tag} ({min_value} - {max_value})",
            type=click.FloatRange(min_value, max_value),
        )
        selected_coordinates[axis_tag] = coordinates

    selected_instance.coordinates = selected_coordinates

    return selected_instance


cli = click.Group("converter", help="Font conversion utilities.")


@cli.command("otf2ttf", cls=BaseCommand)
@click.option(
    "-t",
    "--tolerance",
    type=click.FloatRange(min=0.0, max=3.0),
    default=1.0,
    help="""
    Conversion tolerance (0.0-3.0, default 1.0). Low tolerance adds more points but keeps shapes.
    High tolerance adds few points but may change shape.
    """,
)
@click.option(
    "-upm",
    "--target-upm",
    type=click.IntRange(min=16, max=16384),
    help="""
    Set the target UPM value for the converted font.

    Scaling is applied to the font after conversion to TrueType, to avoid scaling a PostScript font
    (which in some cases can lead to corrupted outlines).
    """,
)
def otf_to_ttf(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """

    def task(
        font: Font,
        tolerance: float = 1.0,
        target_upm: Optional[int] = None,
        output_dir: Optional[Path] = None,
        overwrite: bool = True,
    ) -> None:
        flavor = font.ttfont.flavor
        suffix = ".ttf" if flavor is not None else ""
        extension = font.get_file_ext() if flavor is not None else ".ttf"
        out_file = font.get_file_path(
            output_dir=output_dir, overwrite=overwrite, extension=extension, suffix=suffix
        )

        tolerance = tolerance / 1000 * font.t_head.units_per_em

        logger.info("Converting to TTF...")
        font.to_ttf(max_err=tolerance, reverse_direction=True)

        if target_upm:
            logger.info(f"Scaling UPM to {target_upm}...")
            font.scale_upm(target_upm=target_upm)

        font.save(out_file)
        logger.success(f"File saved to {out_file}")

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("ttf2otf", cls=BaseCommand)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["qu2cu", "tx"]),
    default="qu2cu",
    show_default=True,
    help="""
    Conversion mode. By default, the script uses the ``qu2cu`` mode. Quadratic curves are
    converted to cubic curves using the Qu2CuPen. Use the ``tx`` mode to use the tx tool
    from AFDKO to generate the CFF table instead of the Qu2CuPen.
    """,
)
@click.option(
    "-t",
    "--tolerance",
    type=click.FloatRange(min=0.0, max=3.0),
    default=1.0,
    help="""
    Conversion tolerance (0.0-3.0, default 1.0). Low tolerance adds more points but keeps shapes.
    High tolerance adds few points but may change shape.

    This option is only used in the ``qu2cu`` mode.
    """,
)
@click.option(
    "-upm",
    "--target-upm",
    type=click.IntRange(min=16, max=16384),
    default=None,
    help="""
    Set the target UPM value for the converted font.

    Scaling is applied to the TrueType font before conversion, to avoid scaling a PostScript font
    (which in some cases can lead to corrupted outlines).
    """,
)
@click.option(
    "-cc/--no-cc",
    "--correct-contours/--no-correct-contours",
    is_flag=True,
    default=True,
    show_default=True,
    help="""
    Correct contours with pathops during conversion (removes overlaps and tiny contours, corrects
    direction).
    """,
)
@click.option(
    "-co/--no-co",
    "--check-outlines/--no-check-outlines",
    is_flag=True,
    default=False,
    show_default=True,
    help="Perform a further check with ``afdko.checkoutlinesufo`` after conversion.",
)
@click.option(
    "-s/--no-s",
    "--subroutinize/--no-subroutinize",
    is_flag=True,
    default=True,
    show_default=True,
    help="Subroutinize the font with ``cffsubr`` after conversion.",
)
def ttf_to_otf(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Convert TrueType flavored fonts to PostScript flavored fonts.
    """

    if options["mode"] == "tx":
        options.pop("tolerance")
        task = ttf2otf_with_tx
    else:
        task = ttf2otf  # type: ignore

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.filter.filter_out_ps = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("wf2ft", cls=BaseCommand)
@click.option(
    "-f",
    "--format",
    "in_format",
    type=click.Choice(["woff", "woff2"]),
    default=None,
    help="""
    By default, the script converts both woff and woff2 flavored web fonts to SFNT fonts
    (TrueType or OpenType). Use this option to convert only woff or woff2 flavored web
    fonts.
    """,
)
def web_to_sfnt(
    input_path: Path,
    in_format: Optional[Literal["woff", "woff2"]],
    **options: dict[str, Any],
) -> None:
    """
    Convert WOFF and WOFF2 fonts to SFNT fonts.
    """
    runner = TaskRunner(input_path=input_path, task=Font.to_sfnt, **options)
    runner.filter.filter_out_sfnt = True
    runner.force_modified = True
    if in_format == "woff":
        runner.filter.filter_out_woff2 = True
    elif in_format == "woff2":
        runner.filter.filter_out_woff = True
    runner.run()


@cli.command("ft2wf", cls=BaseCommand)
@click.option(
    "-f",
    "--format",
    "out_format",
    type=click.Choice(["woff", "woff2"]),
    default=None,
    help="""
    By default, the script converts SFNT fonts to both woff and woff2 flavored web fonts.
    Use this option to convert only to woff or woff2 flavored web fonts.
    """,
)
def sfnt_to_web(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Convert SFNT fonts to WOFF and/or WOFF2 fonts.
    """

    def task(
        font: Font,
        output_dir: Optional[Path] = None,
        out_format: Optional[Literal["woff", "woff2"]] = None,
        overwrite: bool = True,
        reorder_tables: bool = False,
    ) -> None:
        suffix = font.get_file_ext()

        out_formats = [WOFF_FLAVOR, WOFF2_FLAVOR] if out_format is None else [out_format]

        if WOFF_FLAVOR in out_formats:
            logger.info("Converting to WOFF")
            font.to_woff()
            out_file = font.get_file_path(output_dir=output_dir, overwrite=overwrite, suffix=suffix)
            font.save(out_file, reorder_tables=reorder_tables)
            logger.success(f"File saved to {out_file}")

        if WOFF2_FLAVOR in out_formats:
            logger.info("Converting to WOFF2")
            font.to_woff2()
            out_file = font.get_file_path(output_dir=output_dir, overwrite=overwrite, suffix=suffix)
            font.save(out_file, reorder_tables=reorder_tables)
            logger.success(f"File saved to {out_file}")

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_woff = True
    runner.filter.filter_out_woff2 = True
    runner.save_if_modified = False
    runner.run()


@cli.command("var2static", cls=BaseCommand)
@click.option(
    "-ol",
    "--overlap-mode",
    "overlap",
    type=click.Choice(["0", "1", "2", "3"]),
    default="1",
    show_default=True,
    callback=choice_to_int_callback,
    help="""
    The overlap mode to use when converting variable fonts to static fonts.

    See https://fonttools.readthedocs.io/en/latest/varLib/instancer.html#fontTools.varLib.instancer.instantiateVariableFont

    \b
    0: KEEP_AND_DONT_SET_FLAGS
    1: KEEP_AND_SET_FLAGS
    2: REMOVE
    3: REMOVE_AND_IGNORE_ERRORS
    """,
)
@click.option(
    "-s",
    "--select-instance",
    is_flag=True,
    help="Select a single instance with custom axis values.",
)
def variable_to_static(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Convert variable fonts to static fonts.
    """

    def task(
        var_font: Font,
        select_instance: bool = False,
        overlap: int = 1,
        output_dir: Optional[Path] = None,
        overwrite: bool = True,
    ) -> None:
        if select_instance:
            axes = var_font.t_fvar.table.axes
            selected_instance = _select_instance_coordinates(axes)
            requested_instances = [selected_instance]
        else:
            requested_instances = var_font.t_fvar.table.instances

        if not requested_instances:
            raise ValueError("No instances found in the variable font.")

        if output_dir is None:
            if var_font.file is None:
                raise ValueError("Cannot determine the output directory.")
            output_dir = var_font.file.parent

        try:
            check_update_name_table(var_font)
            update_font_names = True
        except UpdateNameTableError as e:
            logger.warning(f"The name table cannot be updated: {e}")
            update_font_names = False

        for i, instance in enumerate(requested_instances, start=1):
            logger.info(f"Exporting instance {i} of {len(requested_instances)}")
            try:
                static_font, file_name = var2static(var_font, instance, update_font_names, overlap)
            except (BadInstanceError, Var2StaticError) as e:
                logger.opt(colors=True).error(f"<lr>{e.__module__}.{type(e).__name__}</lr>: {e}")
                continue

            out_file = makeOutputFileName(
                sanitize_filename(file_name), output_dir, overWrite=overwrite
            )
            static_font.save(out_file)
            static_font.close()
            logger.success(f"Static instance saved to {out_file}\n")

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_static = True
    runner.filter.filter_out_ps = True
    runner.save_if_modified = False
    runner.run()


@cli.command("ttc2sfnt", cls=BaseCommand)
def ttc_to_sfnt(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Extract fonts from a TTCollection file.
    """

    recursive = bool(options.get("recursive", False))
    overwrite = bool(options.get("overwrite", True))
    recalc_bboxes = bool(options.get("recalc_bboxes", True))
    reorder_tables = bool(options.get("reorder_tables", False))

    finder = FontFinder(input_path)
    finder.options.recursive = recursive

    tt_collections = finder.generate_collections()

    timer_1 = Timer(
        logger=logger.opt(colors=True).info, text="Elapsed time <cyan>{:0.4f} seconds</>"
    )
    timer_2 = Timer(
        logger=logger.opt(colors=True).info,
        text="Processing time: <cyan>{:0.4f} seconds</>",
    )

    timer_1.start()
    for collection in tt_collections:
        timer_2.start()
        num_fonts = len(collection.fonts)
        collection_file = Path(collection.fonts[0].reader.file.name)
        output_dir = options.get("output_dir", collection_file.parent)

        logger.info(f"Converting {collection_file} ({num_fonts} fonts in collection)")

        for font in collection.fonts:
            font_wrapper = Font(font)
            font_wrapper.ttfont.recalcBBoxes = recalc_bboxes
            file_stem = font_wrapper.t_name.get_debug_name(6)
            file_ext = font_wrapper.get_file_ext()

            out_file = makeOutputFileName(
                sanitize_filename(file_stem),
                outputDir=output_dir,
                overWrite=overwrite,
                extension=file_ext,
            )
            font_wrapper.save(out_file, reorder_tables=reorder_tables)

            logger.success(f"File saved to {out_file}")

        timer_2.stop()
        print()

    timer_1.stop()

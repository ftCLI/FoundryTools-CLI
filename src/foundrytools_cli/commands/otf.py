from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import click
from foundrytools import Font
from foundrytools.app.otf_autohint import OTFAutohintError
from foundrytools.app.otf_autohint import run as otf_autohint
from foundrytools.app.otf_check_outlines import run as otf_check_outlines
from foundrytools.app.otf_dehint import run as otf_dehint
from foundrytools.app.otf_recalc_stems import run as get_stems
from foundrytools.app.otf_recalc_zones import run as get_zones
from foundrytools.utils.path_tools import get_temp_file_path

from foundrytools_cli.utils import BaseCommand, make_options
from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing OpenType-PS fonts.")


def subroutinize_flag() -> Callable:
    """
    Add the ``subroutinize`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``subroutinize`` option to a click command
    """
    _subroutinize_flag = [
        click.option(
            "-subr/-no-subr",
            "subroutinize",
            default=True,
            help="Subroutinize the font after processing",
        )
    ]
    return make_options(_subroutinize_flag)


@cli.command("autohint", cls=BaseCommand)
@click.option(
    "-ac",
    "--allow-changes",
    "allowChanges",
    is_flag=True,
    default=False,
    help="""
    Allow changes to the glyphs outlines.
    """,
)
@click.option(
    "-nzs",
    "--no-zones-stems",
    "allowNoBlues",
    is_flag=True,
    default=False,
    help="""
    Allow the font to have no alignment zones nor stem widths.
    """,
)
@click.option(
    "-d/-no-d",
    "--decimal/--no-decimal",
    "roundCoords",
    is_flag=True,
    default=True,
    help="""
    Use decimal coordinates.
    """,
)
@click.option(
    "-nf",
    "--no-flex",
    "noFlex",
    is_flag=True,
    default=False,
    help="""
    Suppress generation of flex commands.
    """,
)
@click.option(
    "-nh",
    "--no-hint-sub",
    "noHintSub",
    is_flag=True,
    default=False,
    help="""
    Suppress hint substitution.
    """,
)
@subroutinize_flag()
def autohint(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Autohint OpenType-PS fonts with ``afdko.otfautohint``.
    """

    def task(font: Font, subroutinize: bool = True, **kwargs: dict[str, Any]) -> bool:
        logger.info("Autohinting...")

        try:
            otf_autohint(font, **kwargs)
        except OTFAutohintError as e:
            logger.error(f"Autohinting failed: {e}")
            return False

        if subroutinize:
            font.reload()  # DO NOT REMOVE
            logger.info("Subroutinizing...")
            font.subroutinize()

        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("dehint", cls=BaseCommand)
@click.option(
    "-dh",
    "--drop-hinting-data",
    is_flag=True,
    help="""
    Drop BlueValues, OtherBlues, FamilyBlues, FamilyOtherBlues, StdHW, StdVW, StemSnapH, and
    StemSnapV from the CFF Private dictionary.
    """,
)
@subroutinize_flag()
def dehint(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Dehint OpenType-PS fonts.
    """

    def task(font: Font, drop_hinting_data: bool = False, subroutinize: bool = True) -> bool:
        logger.info("Dehinting font...")
        otf_dehint(font, drop_hinting_data=drop_hinting_data)
        if subroutinize:
            logger.info("Subroutinizing...")
            font.subroutinize()

        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("subr", cls=BaseCommand)
def subr(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
    """

    def task(font: Font) -> bool:
        logger.info("Subroutinizing...")
        return font.subroutinize()

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("desubr", cls=BaseCommand)
def desubr(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
    """

    def task(font: Font) -> bool:
        logger.info("Desubroutinizing...")
        return font.desubroutinize()

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("check-outlines", cls=BaseCommand)
@subroutinize_flag()
def check_outlines(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Check the outlines of OpenType-PS fonts with ``afdko.checkoutlinesufo``.
    """

    def task(font: Font, subroutinize: bool = True) -> bool:
        logger.info("Checking outlines")
        otf_check_outlines(font)
        if subroutinize:
            logger.info("Subroutinizing")
            font.subroutinize()

        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("round-coordinates", cls=BaseCommand)
@subroutinize_flag()
def round_coordinates(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Round the coordinates of OpenType-PS fonts.
    """

    def task(font: Font, subroutinize: bool = True, drop_hinting_data: bool = False) -> bool:
        logger.info("Rounding coordinates")
        result = font.t_cff_.round_coordinates(drop_hinting_data=drop_hinting_data)
        if not result:
            return False

        logger.info(f"{len(result)} glyphs were modified")

        if subroutinize:
            logger.info("Subroutinizing")
            font.subroutinize()

        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("recalc-stems", cls=BaseCommand)
@click.option(
    "-all",
    "--report-all-stems",
    is_flag=True,
    help="""
    Include stems formed by curved line segments; by default, includes only stems formed by straight
    line segments.
    """,
)
@click.option(
    "--max-distance",
    type=click.IntRange(min=0),
    default=1,
    help="""
    The maximum distance between widths to consider as part of the same group.
    """,
)
@click.option(
    "--max-h-stems",
    type=click.IntRange(min=1, max=12),
    default=2,
    help="""
    The number of horizontal stem values to extract.
    """,
)
@click.option(
    "--max-v-stems",
    type=click.IntRange(min=1, max=12),
    default=2,
    help="""
    The number of vertical stem values to extract.
    """,
)
@click.option(
    "--use-samples/--all-glyphs",
    default=True,
    show_default=True,
    help="Calculate each value from its default or custom glyph sample, or from the whole font.",
)
@click.option(
    "--std-h-sample",
    multiple=True,
    help="Characters to sample for StdHW; may be repeated. Defaults to the built-in sample.",
)
@click.option(
    "--std-v-sample",
    multiple=True,
    help="Characters to sample for StdVW; may be repeated. Defaults to the built-in sample.",
)
@click.option(
    "--snap-h-sample",
    multiple=True,
    help="Characters to sample for StemSnapH; may be repeated. Defaults to the built-in sample.",
)
@click.option(
    "--snap-v-sample",
    multiple=True,
    help="Characters to sample for StemSnapV; may be repeated. Defaults to the built-in sample.",
)
def recalc_stems(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Recalculate the hinting stems of OpenType-PS fonts.
    """

    sample_options = ("std_h_sample", "std_v_sample", "snap_h_sample", "snap_v_sample")
    if not options["use_samples"] and any(options[name] for name in sample_options):
        raise click.UsageError("Custom glyph samples cannot be used with --all-glyphs.")

    def task(
        font: Font,
        report_all_stems: bool = False,
        max_distance: int = 1,
        max_h_stems: int = 2,
        max_v_stems: int = 2,
        use_samples: bool = True,
        std_h_sample: tuple[str, ...] = (),
        std_v_sample: tuple[str, ...] = (),
        snap_h_sample: tuple[str, ...] = (),
        snap_v_sample: tuple[str, ...] = (),
    ) -> bool:
        if not font.is_ps:
            logger.error("Font is not a PostScript font")
            return False

        if font.file is None:
            logger.error("Font has no file path")
            return False

        flavor = font.ttfont.flavor
        temp_file: Path | None = None
        if flavor is not None:
            font.ttfont.flavor = None
            temp_file = get_temp_file_path()
            try:
                font.save(temp_file)
            except Exception:
                temp_file.unlink(missing_ok=True)
                raise
            finally:
                font.ttfont.flavor = flavor
            input_file = temp_file
        else:
            input_file = font.file

        logger.info("Getting stems...")

        current_std_h_w = font.t_cff_.get_hinting_data().get("StdHW", None)
        current_std_v_w = font.t_cff_.get_hinting_data().get("StdVW", None)
        current_stem_snap_h = font.t_cff_.get_hinting_data().get("StemSnapH", None)
        current_stem_snap_v = font.t_cff_.get_hinting_data().get("StemSnapV", None)

        def to_codepoints(sample: tuple[str, ...]) -> set[int] | None:
            codepoints = {ord(char) for text in sample for char in text}
            return codepoints or None

        try:
            std_h_w, std_v_w, stem_snap_h, stem_snap_v = get_stems(
                input_file,
                report_all_stems=report_all_stems,
                max_distance=max_distance,
                max_h_stems=max_h_stems,
                max_v_stems=max_v_stems,
                use_samples=use_samples,
                std_h_codepoints=to_codepoints(std_h_sample),
                std_v_codepoints=to_codepoints(std_v_sample),
                snap_h_codepoints=to_codepoints(snap_h_sample),
                snap_v_codepoints=to_codepoints(snap_v_sample),
            )
        finally:
            if temp_file is not None:
                temp_file.unlink(missing_ok=True)

        logger.info(f"StdHW: {current_std_h_w} -> {std_h_w}")
        logger.info(f"StdVW: {current_std_v_w} -> {std_v_w}")
        logger.info(f"StemSnapH: {current_stem_snap_h} -> {stem_snap_h}")
        logger.info(f"StemSnapV: {current_stem_snap_v} -> {stem_snap_v}")

        if (current_std_h_w, current_std_v_w, current_stem_snap_h, current_stem_snap_v) == (
            std_h_w,
            std_v_w,
            stem_snap_h,
            stem_snap_v,
        ):
            return False

        hinting_data: dict[str, Any] = {
            "StdHW": std_h_w,
            "StdVW": std_v_w,
            "StemSnapH": stem_snap_h,
            "StemSnapV": stem_snap_v,
        }
        font.t_cff_.set_hinting_data(**hinting_data)
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("recalc-zones", cls=BaseCommand)
def recalc_zones(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Recalculate the hinting zones of OpenType-PS fonts.
    """

    def task(font: Font) -> bool:
        if not font.is_ps:
            logger.error("Font is not a PostScript font")
            return False
        current_other_blues, current_blues = (
            font.t_cff_.get_hinting_data().get("OtherBlues", None),
            font.t_cff_.get_hinting_data().get("BlueValues", None),
        )
        other_blues, blue_values = get_zones(font)
        logger.info(f"BlueValues: {current_blues} -> {blue_values}")
        logger.info(f"OtherBlues: {current_other_blues} -> {other_blues}")
        if (current_other_blues, current_blues) == (other_blues, blue_values):
            return False

        font.t_cff_.set_hinting_data(
            **cast(dict[str, Any], {"BlueValues": blue_values, "OtherBlues": other_blues})
        )
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()

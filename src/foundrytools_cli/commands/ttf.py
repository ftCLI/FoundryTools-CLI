from pathlib import Path
from typing import Any

import click
from foundrytools import Font
from foundrytools.app.ttf_autohint import run as ttf_autohint
from foundrytools.app.ttf_dehint import run as ttf_dehint

from foundrytools_cli.utils import BaseCommand
from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing OpenType-TT fonts.")


@cli.command("autohint", cls=BaseCommand)
def autohint(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Auto-hints the given TrueType fonts using ttfautohint-py.
    """

    runner = TaskRunner(input_path=input_path, task=ttf_autohint, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("dehint", cls=BaseCommand)
def dehint(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Removes hinting from the given TrueType fonts.
    """

    runner = TaskRunner(input_path=input_path, task=ttf_dehint, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("decompose", cls=BaseCommand)
def decompose(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Decomposes the composite glyphs of the given TrueType fonts.
    """

    def task(font: Font) -> bool:
        result = font.t_glyf.decompose_all()
        if result:
            logger.opt(colors=True).info(f"Decomposed glyphs: <lc>{', '.join(list(result))}</lc>")
            return True
        return False

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("scale-upm", cls=BaseCommand)
@click.option(
    "-upm",
    "--target-upm",
    type=click.IntRange(min=16, max=16384),
    required=True,
    help="The target UPM value to scale the fonts to.",
)
def scale_upm(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Scales the given TrueType fonts to the specified UPM.
    """

    runner = TaskRunner(input_path=input_path, task=Font.scale_upm, **options)
    runner.filter.filter_out_ps = True
    runner.force_modified = True
    runner.run()

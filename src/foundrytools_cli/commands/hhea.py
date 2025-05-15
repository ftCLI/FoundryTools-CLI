from pathlib import Path
from typing import Any

import click
from afdko.fdkutils import run_shell_command
from foundrytools import Font
from foundrytools.utils.path_tools import get_temp_file_path

from foundrytools_cli.utils import BaseCommand, ensure_at_least_one_param
from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing the ``hhea`` table.")


@cli.command("set-attrs", cls=BaseCommand)
@click.option("--ascent", "ascent", type=int, help="""Sets the ``ascent`` value.""")
@click.option("--descent", "descent", type=int, help="""Sets the ``descent`` value.""")
@click.option("--line-gap", "line_gap", type=int, help="""Sets the ``lineGap`` value.""")
@click.option("--rise", "caret_slope_rise", type=int, help="""Sets the ``caretSlopeRise`` value.""")
@click.option("--run", "caret_slope_run", type=int, help="""Sets the ``caretSlopeRun`` value.""")
@click.option("--offset", "caret_offset", type=int, help="""Sets the ``caretOffset`` value.""")
def set_attrs(input_path: Path, **options: dict[str, Any]) -> None:
    """Sets miscellaneous attributes of the 'hhea' table."""
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: dict[str, int]) -> bool:
        for attr, value in kwargs.items():
            if value is not None:
                try:
                    setattr(font.t_hhea, attr, value)
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error setting {attr} to {value}: {e}")
        return font.t_hhea.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-caret-offset", cls=BaseCommand)
def recalc_caret_offset(input_path: Path, **options: dict[str, Any]) -> None:
    """Recalculates the ``caretOffset`` field of the ``hhea`` table."""

    def task(font: Font) -> bool:
        current_offset = font.t_hhea.caret_offset
        temp_t1_file = get_temp_file_path()
        temp_otf_file = get_temp_file_path()

        if font.ttfont.flavor is None:
            source_file = font.file
        else:
            font.ttfont.flavor = None
            source_file = font.temp_file
            font.save(source_file)

        command_1 = ["tx", "-t1", source_file, temp_t1_file]
        command_2 = ["makeotf", "-f", temp_t1_file, "-o", temp_otf_file]

        run_shell_command(command_1, suppress_output=True)
        run_shell_command(command_2, suppress_output=True)

        with Font(temp_otf_file) as temp_font:
            calculated_offset = temp_font.t_hhea.caret_offset
            font.t_hhea.caret_offset = calculated_offset

        temp_t1_file.unlink(missing_ok=True)
        temp_otf_file.unlink(missing_ok=True)

        if current_offset != calculated_offset:
            logger.info(f"Recalculated caret offset from {current_offset} to {calculated_offset}.")

        return font.t_hhea.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()

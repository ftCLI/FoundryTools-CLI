from pathlib import Path
from typing import Any, Optional

import click
from foundrytools import Font

from foundrytools_cli.utils import BaseCommand, ensure_at_least_one_param
from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.task_runner import TaskRunner


@click.command(cls=BaseCommand)
@click.option(
    "--italic-angle",
    "italic_angle",
    type=float,
    help="""Sets the `italicAngle` value.""",
)
@click.option(
    "--ul-position",
    "underline_position",
    type=int,
    help="""Sets the `underlinePosition` value.""",
)
@click.option(
    "--ul-thickness",
    "underline_thickness",
    type=click.IntRange(min=0),
    help="""Sets the `underlineThickness` value.""",
)
@click.option(
    "--fixed-pitch/--no-fixed-pitch",
    "fixed_pitch",
    is_flag=True,
    default=None,
    help="""Sets or clears the `isFixedPitch` value.""",
)
def cli(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Utilities for editing the ``post`` table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(
        font: Font,
        italic_angle: Optional[float] = None,
        underline_position: Optional[int] = None,
        underline_thickness: Optional[int] = None,
        fixed_pitch: Optional[bool] = None,
    ) -> bool:
        attrs = {
            "italic_angle": italic_angle,
            "underline_position": underline_position,
            "underline_thickness": underline_thickness,
            "fixed_pitch": fixed_pitch,
        }

        if all(value is None for value in attrs.values()):
            logger.error("No parameter provided")
            return False

        for attr, value in attrs.items():
            if value is not None:
                old_value = getattr(font.t_post, attr)
                logger.info(f"{attr}: {old_value} -> {value}")
                setattr(font.t_post, attr, value)

        return font.t_post.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()

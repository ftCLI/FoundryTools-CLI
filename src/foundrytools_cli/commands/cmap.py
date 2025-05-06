from pathlib import Path
from typing import Any

import click
from foundrytools import Font

from foundrytools_cli.utils import BaseCommand
from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing the ``cmap`` table.")


@cli.command("rebuild", cls=BaseCommand)
@click.option(
    "--remap-all",
    is_flag=True,
    help="Remap all glyphs, including the ones already in the cmap table.",
)
def rebuild_cmap(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Rebuild the cmap table of a font. Optionally remap all characters, including those already in
    the cmap table.
    """

    def task(font: Font, remap_all: bool = False) -> bool:
        remapped_glyphs, _ = font.t_cmap.rebuild_character_map(remap_all=remap_all)
        if remapped_glyphs:
            logger.info("Remapped glyphs:")
            for r in remapped_glyphs:
                logger.opt(colors=True).info(
                    f" {r[1]} -> <lc>{hex(r[0])[:2]}{hex(r[0])[2:].upper().zfill(6)}</lc>"
                )
            return True

        return False

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()

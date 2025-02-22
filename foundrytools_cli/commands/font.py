from pathlib import Path
from typing import Any, Literal, Optional

import click
from foundrytools.core.font import Font

from foundrytools_cli.utils import BaseCommand, tuple_to_set_callback
from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.task_runner import TaskRunner

cli = click.Group(help="Font level utilities.")


@cli.command("correct-contours", cls=BaseCommand)
@click.option(
    "-ma",
    "--min-area",
    type=click.IntRange(min=0),
    default=25,
    help="""
        All subpaths with a bounding box less than this value will be removed. Default is 25
        square units (same as afdko.checkoutlinesufo). Set to 0 to disable this feature.
        """,
)
@click.option(
    "--keep-hinting",
    "remove_hinting",
    is_flag=True,
    default=True,
    help="Keep hinting for unmodified glyphs, default is to drop hinting",
)
@click.option(
    "--ignore-errors",
    is_flag=True,
    help="""
        Ignore errors while correcting contours, thus keeping the tricky glyphs unchanged.
        """,
)
@click.option(
    "--keep-unused-subroutines",
    "remove_unused_subroutines",
    is_flag=True,
    default=True,
    help="""
        Keep unused subroutines in CFF table after removing overlaps, default is to remove them
        if any glyphs are modified.
        """,
)
def correct_contours(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Correct contours of the given fonts by removing overlaps, correcting the direction of the
    contours, and removing tiny paths.

    Fixing procedure:

    * Remove overlaps in the contours of the glyphs.
    * Correct the direction of the contours.
    * Remove tiny paths.
    """

    def task(
        font: Font,
        min_area: int = 25,
        remove_hinting: bool = True,
        ignore_errors: bool = False,
        remove_unused_subroutines: bool = True,
    ) -> bool:
        logger.info("Correcting contours...")
        modified_glyphs = font.correct_contours(
            min_area=min_area,
            remove_hinting=remove_hinting,
            ignore_errors=ignore_errors,
            remove_unused_subroutines=remove_unused_subroutines,
        )

        if not modified_glyphs:
            logger.info("No glyphs were modified")
            return False

        logger.opt(colors=True).info(
            f"{len(modified_glyphs)} glyphs were modified: <lc>{', '.join(modified_glyphs)}</lc>"
        )
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("del-table", cls=BaseCommand)
@click.option(
    "-t",
    "--table-tag",
    required=True,
    help="The table tag to delete.",
)
def del_table(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Delete a table from the font file.
    """

    def task(font: Font, table_tag: str) -> bool:
        if table_tag not in font.ttfont:
            logger.warning(f"Table '{table_tag}' not found in the font.")
            return False
        return font.del_table(table_tag=table_tag)

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("rebuild", cls=BaseCommand)
def rebuild(input_path: Path, **options: dict[str, Any]) -> None:
    """Rebuild the font by saving it as XML to a temporary stream and then loading it back."""

    def task(font: Font) -> bool:
        logger.info("Rebuilding font...")
        font.rebuild()
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("remove-glyphs", cls=BaseCommand)
@click.option(
    "-gn",
    "--glyph-name",
    "glyph_names_to_remove",
    type=str,
    multiple=True,
    help="The names of the glyphs to remove.",
    callback=tuple_to_set_callback,
)
@click.option(
    "-gid",
    "--glyph-id",
    "glyph_ids_to_remove",
    type=int,
    multiple=True,
    help="The glyph IDs to remove.",
    callback=tuple_to_set_callback,
)
def remove_glyphs(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Remove glyphs from a font file.
    """
    if not options.get("glyph_names_to_remove") and not options.get("glyph_ids_to_remove"):
        raise click.UsageError("You must provide at least one glyph name or ID to remove.")

    def task(
        font: Font,
        glyph_names_to_remove: Optional[set[str]],
        glyph_ids_to_remove: Optional[set[int]],
    ) -> bool:
        removed_glyphs = font.remove_glyphs(
            glyph_names_to_remove=glyph_names_to_remove,
            glyph_ids_to_remove=glyph_ids_to_remove,
        )
        if removed_glyphs:
            logger.opt(colors=True).info(
                f"Removed glyphs: <lc>{', '.join(list(removed_glyphs))}</lc>"
            )
            return True

        return False

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("rename-glyph", cls=BaseCommand)
@click.option("-old", "--old-name", required=True, help="The old name of the glyph.")
@click.option("-new", "--new-name", required=True, help="The new name of the glyph.")
def rename_glyph(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Rename a glyph in a font file.
    """

    def task(font: Font, old_name: str, new_name: str) -> bool:
        result = font.rename_glyph(old_name=old_name, new_name=new_name)
        if result:
            logger.opt(colors=True).info(
                f"Renamed glyph: <lc>{old_name}</lc> to <lc>{new_name}</lc>"
            )
            return True

        return False

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.force_modified = True
    runner.run()


@cli.command("rename-glyphs", cls=BaseCommand)
@click.option(
    "-s",
    "--source-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="The source font file to get the glyph order from.",
)
def rename_glyphs(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Rename glyphs in a font file based on the glyph order of another font file.
    """

    def task(font: Font, source_file: Path) -> bool:
        old_glyph_order = font.ttfont.getGlyphOrder()

        try:
            source_font = Font(source_file)
            new_glyph_order = source_font.ttfont.getGlyphOrder()
        except Exception as e:
            raise RuntimeError from e

        if old_glyph_order == new_glyph_order:
            logger.warning("The glyph order of the source font is the same as the current font.")
            return False

        return font.rename_glyphs(new_glyph_order=new_glyph_order)

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-production-names", cls=BaseCommand)
def set_production_names(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Set the production names of glyphs in a font file.
    """

    def task(font: Font) -> bool:
        renamed_glyphs = font.set_production_names()

        if renamed_glyphs:
            logger.info("Renamed glyphs:")
            for old_name, new_name in renamed_glyphs:
                logger.opt(colors=True).info(f"  {old_name} -> <lc>{new_name}</lc>")
            return True

        return False

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("sort-glyphs", cls=BaseCommand)
@click.option(
    "-by",
    "--sort-by",
    type=click.Choice(["unicode", "alphabetical", "cannedDesign"]),
    default="unicode",
    show_default=True,
    help="""
    The method to sort the glyphs.

    \b
    * unicode: Sort the glyphs based on their Unicode values.
    * alphabetical: Sort the glyphs alphabetically.
    * cannedDesign: Sort glyphs into a design process friendly order.
    """,
)
def sort_glyphs(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Sort the glyphs in a font file.
    """

    def task(
        font: Font,
        sort_by: Literal["unicode", "alphabetical", "cannedDesign"] = "unicode",
    ) -> bool:
        return font.sort_glyphs(sort_by=sort_by)

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()

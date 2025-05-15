# pylint: disable=import-outside-toplevel
from pathlib import Path
from typing import Any, Callable, cast

import click

from foundrytools_cli.utils import choice_to_int_callback, make_options
from foundrytools_cli.utils.task_runner import TaskRunner


def recursive_flag() -> Callable:
    """
    Add the ``recursive`` option to a click command.

    :return: A decorator that adds the ``recursive`` option to a click command
    :rtype: Callable
    """
    _recursive_flag = [
        click.option(
            "-r",
            "--recursive",
            is_flag=True,
            default=False,
            help="""
            If ``input_path`` is a directory, the font finder will search for fonts recursively in
            subdirectories.
            """,
        )
    ]
    return make_options(_recursive_flag)


cli = click.Group(help="Miscellaneous utilities.")


@cli.command("font-renamer", no_args_is_help=True)
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@click.option(
    "-s",
    "--source",
    type=click.Choice(choices=["1", "2", "3", "4", "5"]),
    default="1",
    callback=choice_to_int_callback,
    help="""
        The source string(s) from which to extract the new file name. Default is 1
        (FamilyName-StyleName), used also as fallback name when 4 or 5 are passed but the font
        is TrueType

        \b
        1: FamilyName-StyleName
        2: PostScript Name
        3: Full Font Name
        4: CFF fontNames (CFF fonts only)
        5: CFF TopDict FullName (CFF fonts only)
        """,
)
@recursive_flag()
def font_renamer(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Renames the given font files.
    """
    from foundrytools_cli.commands.utils.font_renamer import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()


@cli.command("font-organizer", no_args_is_help=True)
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@click.option(
    "-m",
    "--sort-by-manufacturer",
    is_flag=True,
    help="Sort the font files by manufacturer.",
)
@click.option(
    "-v",
    "--sort-by-font-revision",
    is_flag=True,
    help="Sort the font files by font revision.",
)
@click.option(
    "-e",
    "--sort-by-extension",
    is_flag=True,
    help="Sort the font files by extension.",
)
@click.option(
    "-d",
    "--delete-empty-directories",
    is_flag=True,
    help="Delete empty directories after moving the font files.",
)
@recursive_flag()
def font_organizer(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Organizes the given font files based on specified sorting options.
    """
    # This is a workaround to make the task work with the current TaskRunner
    options["in_path"] = cast(Any, input_path)

    from foundrytools_cli.commands.utils.font_organizer import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()


@cli.command("sync-timestamps", no_args_is_help=True)
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@recursive_flag()
def align_timestamps(input_path: Path, recursive: bool = False) -> None:
    """
    Syncs the modified and created timestamps of the font files in the given path with the
    created and modified timestamps stored in their head table.
    """

    from foundrytools_cli.commands.utils.sync_timestamps import main as task

    task(input_path, recursive=recursive)

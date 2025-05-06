from pathlib import Path
from typing import Any, Optional

import click
from foundrytools import Font

from foundrytools_cli.utils import BaseCommand, choice_to_int_callback
from foundrytools_cli.utils.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing the ``name`` table.")


@cli.command("del-names", cls=BaseCommand)
@click.option(
    "-n",
    "--name-ids",
    "name_ids_to_process",
    type=click.IntRange(min=0, max=None),
    required=True,
    multiple=True,
    default=None,
    help="""
    Specify the name IDs to be delete.

    Example: ``-n 1 -n 2`` will delete name IDs 1 and 2.
    """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.IntRange(min=0, max=4),
    default=None,
    help="""
    Specify the platform ID of the NameRecords to delete.

    Example: ``-p 1`` will modify only NameRecords with platform ID 1.
    """,
)
@click.option(
    "-l",
    "--language-string",
    type=str,
    default="en",
    help="""
    Specify the language of the NameRecords to be modified.

    Example: ``-l en`` will modify only NameRecords with language code "en".
    """,
)
def del_names(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Delete the specified NameRecords from the ``name`` table.
    """

    def task(
        font: Font,
        name_ids_to_process: tuple[int],
        platform_id: Optional[int] = None,
        language_string: Optional[str] = None,
    ) -> bool:
        font.t_name.remove_names(
            name_ids=name_ids_to_process, platform_id=platform_id, language_string=language_string
        )
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-empty-names", cls=BaseCommand)
def del_empty_names(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Deletes empty NameRecords from the ``name`` table.
    """

    def task(font: Font) -> bool:
        font.t_name.remove_empty_names()
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-mac-names", cls=BaseCommand)
def del_mac_names(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Delete Macintosh-specific NameRecords from the ``name`` table, excluding those with nameID 1, 2,
    4, 5 and 6. If the ``--del-all`` flag is set, all Macintosh-specific NameRecords are deleted.
    """

    def task(font: Font) -> bool:
        font.t_name.remove_mac_names()
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-unused-names", cls=BaseCommand)
def del_unused_names(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Delete unused NameRecords from the ``name`` table.
    """

    def task(font: Font) -> bool:
        font.t_name.table.removeUnusedNames(font.ttfont)
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("find-replace", cls=BaseCommand)
@click.option(
    "-os",
    "--old-string",
    required=True,
    help="The string to be replaced in the NameRecords.",
)
@click.option(
    "-ns",
    "--new-string",
    required=True,
    help="The string to replace the old string with in the NameRecords.",
)
@click.option(
    "-n",
    "--name-ids",
    "name_ids_to_process",
    type=click.IntRange(min=0, max=None),
    required=False,
    multiple=True,
    default=None,
    help="""
    Specify the name IDs to be modified.

    Example: ``-n 1 -n 2`` will modify name IDs 1 and 2.
    """,
)
@click.option(
    "-s",
    "--skip-name-ids",
    "name_ids_to_skip",
    type=click.IntRange(min=0, max=None),
    required=False,
    multiple=True,
    default=None,
    help="""
    Specify the name IDs to skip.

    Example: ``-s 1 -s 2`` will skip name IDs 1 and 2.
    """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.IntRange(min=0, max=4),
    default=None,
    help="""
    Specify the platform ID of the NameRecords to modify.

    Example: ``-p 1`` will modify only NameRecords with platform ID 1.
    """,
)
def find_replace(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Find and replace text in the specified NameRecords.
    """

    def task(
        font: Font,
        old_string: str,
        new_string: str,
        name_ids_to_process: Optional[tuple[int]] = None,
        name_ids_to_skip: Optional[tuple[int]] = None,
    ) -> bool:
        font.t_name.find_replace(
            old_string=old_string,
            new_string=new_string,
            name_ids_to_process=name_ids_to_process,
            name_ids_to_skip=name_ids_to_skip,
        )
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-name", cls=BaseCommand)
@click.option(
    "-s",
    "--string",
    "name_string",
    type=str,
    required=True,
    help="The string to set in the NameRecord",
)
@click.option(
    "-n",
    "--name-id",
    type=click.IntRange(min=0, max=None),
    required=True,
    help="The name ID of the NameRecord to set",
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    callback=choice_to_int_callback,
    default=None,
    help="""
    Specify the platform ID of the NameRecords to add.

    \b
    1: Macintosh
    3: Windows

    Example: ``-p 1`` will only add NameRecords with platform ID 1.
    """,
)
def set_name(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Set the string of the specified NameRecord in the ``name`` table.
    """

    def task(
        font: Font,
        name_id: int,
        name_string: str,
        platform_id: Optional[int] = None,
        language_string: str = "en",
    ) -> bool:
        font.t_name.set_name(
            name_id=name_id,
            name_string=name_string,
            platform_id=platform_id,
            language_string=language_string,
        )
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("strip-names", cls=BaseCommand)
def strip_names(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Remove leading and trailing whitespace from the NameRecords.
    """

    def task(font: Font) -> bool:
        font.t_name.strip_names()
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-unique-id", cls=BaseCommand)
@click.option(
    "-alt",
    "--alternate",
    is_flag=True,
    default=False,
    help="""
    Build the unique ID using the font's family name and subfamily name.
    """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    callback=choice_to_int_callback,
    default=None,
    help="""
    Specify the platform ID to build the unique ID for.
    """,
)
def build_unique_id(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Builds the NameID 3 (Unique ID).

    If the ``--alternate`` flag is set, the unique ID is built using the following fields:

    ``Manufacturer Name: Family Name - Subfamily Name: Creation Year``

    Otherwise, the unique ID is built using the following fields (Default):

    ``Font Revision;Vendor ID;PostScript Name``
    """

    def task(font: Font, platform_id: Optional[int] = None, alternate: bool = False) -> bool:
        font.t_name.build_unique_identifier(platform_id=platform_id, alternate=alternate)
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-full-name", cls=BaseCommand)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    callback=choice_to_int_callback,
    default=None,
    help="""
    Specify the platform ID to build the Full Name for.
    """,
)
def build_full_name(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Builds the NameID 4 (Full Font Name).
    """

    def task(font: Font, platform_id: Optional[int] = None) -> bool:
        font.t_name.build_full_font_name(platform_id=platform_id)
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-version-string", cls=BaseCommand)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    callback=choice_to_int_callback,
    default=None,
    help="""
    Specify the platform ID to build the Version String for.
    """,
)
def build_version_string(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Builds the NameID 5 (Version String).
    """

    def task(font: Font, platform_id: Optional[int] = None) -> bool:
        font.t_name.build_version_string(platform_id=platform_id)
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-postscript-name", cls=BaseCommand)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    callback=choice_to_int_callback,
    default=None,
    help="""
    Specify the platform ID to build the PostScript Name for.
    """,
)
def build_postscript_name(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Builds the NameID 6 (PostScript Name).
    """

    def task(font: Font, platform_id: Optional[int] = None) -> bool:
        font.t_name.build_postscript_name(platform_id=platform_id)
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-mac-names", cls=BaseCommand)
def build_mac_names(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Builds the Macintosh-specific names.

    The following names are built: 1 (Font Family Name), 2 (Font Subfamily Name), 4
    (Full Font Name), 5 (Version String), 6 (PostScript Name).
    """

    def task(font: Font) -> bool:
        font.t_name.build_mac_names()
        return font.t_name.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()

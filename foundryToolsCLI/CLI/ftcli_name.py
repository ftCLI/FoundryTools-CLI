from copy import deepcopy
from pathlib import Path
from typing import Optional

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.constants import LANGUAGES_EPILOG
from foundryToolsCLI.Lib.tables.name import TableName
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_recursive_option,
    add_common_options,
)
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.timer import Timer

tbl_name = click.Group("subcommands")


@tbl_name.command(epilog=LANGUAGES_EPILOG)
@add_file_or_path_argument()
@click.option(
    "-n",
    "--name-id",
    type=click.IntRange(0, 32767),
    required=True,
    help="nameID of the NameRecord to add.",
)
@click.option("-s", "--string", required=True, help="The string to write in the NameRecord.")
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    help="""
    platformID of the NameRecord to add (1: Macintosh, 3: Windows).
    
    If platformID is not specified, both a platformID=1 and a platformID=3 NameRecords will be added.
    """,
)
@click.option(
    "-l",
    "--language-string",
    default="en",
    show_default=True,
    help="""
    Write the NameRecord in a language different than English (e.g.: 'it', 'nl', 'de').

    See epilog for a list of valid language strings.
    """,
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def set_name(
    input_path: Path,
    name_id: int,
    platform_id: int,
    string: str,
    language_string: str,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
) -> None:
    """
    Adds a NameRecord to the name table. If a NameRecord with the same nameID, platformID and languageID already exists,
    it will be overwritten.
    """

    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    if platform_id:
        platform_id = int(platform_id)

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)
            name_table.add_name(
                font,
                name_id=name_id,
                string=string,
                platform_id=platform_id,
                language_string=language_string,
            )
            if name_table_copy.compile(font) != name_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)
        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_name.command(epilog=LANGUAGES_EPILOG)
@add_file_or_path_argument()
@click.option(
    "-n",
    "--name-id",
    "name_ids",
    type=click.IntRange(0, 32767, max_open=True),
    required=True,
    multiple=True,
    help="""
    nameID of the NameRecord to delete.

    This option can be repeated to delete multiple NameRecords at once (e.g.: -x 3 -x 5 -x 6).
    """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["0", "1", "3"]),
    help="""
    If platformID is specified, only NameRecords with matching platformID will be deleted.

    Valid platformID values are: 0 (Unicode), 1 (Macintosh), 3 (Windows).
    """,
)
@click.option(
    "-l",
    "--language-string",
    default=None,
    show_default=True,
    help="""
    Filter the NameRecords to delete by language string (for example: 'it', 'de', 'nl').

    See epilog for a list of valid language strings.
    """,
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def del_names(
    input_path: Path,
    name_ids: tuple[int],
    platform_id: int,
    language_string: str,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Deletes the specified NameRecords from the name table. If no platformID is specified, all NameRecords with the
    specified nameID will be deleted. If no language string is specified, all NameRecords with the specified nameID and
    platformID will be deleted.
    """

    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    if platform_id:
        platform_id = int(platform_id)

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)
            name_table.del_names(
                name_ids=name_ids,
                platform_id=platform_id,
                language_string=language_string,
            )

            if name_table_copy.compile(font) != name_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_name.command()
@add_file_or_path_argument()
@click.option("-os", "--old-string", required=True, help="The string to be replaced")
@click.option(
    "-ns", "--new-string", required=True, help="The string to replace the old string with"
)
@click.option(
    "-n",
    "--name-id",
    "name_ids",
    type=click.IntRange(0, 32767, max_open=True),
    multiple=True,
    help="""
    nameID of the NameRecords where to search and replace the string.

    If nameID is not specified, the string will be replaced in all NameRecords.

    This option can be repeated (e.g.: -x 3 -x 5 -x 6).
    """,
)
@click.option(
    "-x",
    "--exclude-name-id",
    "excluded_name_ids",
    type=click.IntRange(0, 32767, max_open=True),
    multiple=True,
    help="""
    nameID of the NameRecords to skip.

    This option can be repeated (e.g.: -x 3 -x 5 -x 6).
    """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["0", "1", "3"]),
    help="""
    platformID of the NameRecords where to perform find and replace (0: Unicode, 1: Macintosh, 3: Windows).
    """,
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def find_replace(
    input_path: Path,
    old_string: str,
    new_string: str,
    name_ids: tuple[int],
    excluded_name_ids: tuple[int],
    platform_id: int,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Finds and replaces a string in the specified NameRecords. If no nameID is specified, the string will be replaced in
    all NameRecords.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    if platform_id:
        platform_id = int(platform_id)

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)
            name_table.find_replace(
                old_string=old_string,
                new_string=new_string,
                name_ids_to_include=name_ids,
                name_ids_to_skip=excluded_name_ids,
                platform_id=platform_id,
            )

            if name_table_copy.compile(font) != name_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_name.command()
@add_file_or_path_argument()
@click.option("--del-all", is_flag=True, help="Deletes also nameIDs 1, 2, 4, 5 and 6.")
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def del_mac_names(
    input_path: Path,
    del_all: bool = False,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Deletes all the Macintosh NameRecords (platformID=1) from the name table, except the ones with nameID 1, 2, 4, 5,
    and 6.

    According to Apple (https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html), "names with
    platformID 1 were required by earlier versions of macOS. Its use on modern platforms is discouraged. Use names with
    platformID 3 instead for maximum compatibility. Some legacy software, however, may still require names with
    platformID 1, platformSpecificID 0".
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)
            name_ids = set(name.nameID for name in name_table.names if name.platformID == 1)
            if not del_all:
                for n in (1, 2, 4, 5, 6):
                    try:
                        name_ids.remove(n)
                    except KeyError:
                        pass

            name_table.del_names(name_ids=name_ids, platform_id=1)

            if name_table_copy.compile(font) != name_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_name.command(epilog=LANGUAGES_EPILOG)
@add_file_or_path_argument()
@click.option(
    "-n",
    "--name-id",
    "name_ids",
    required=True,
    multiple=True,
    type=int,
    help="""
    nameID of the NameRecords where to append the prefix/suffix.

    This option can be repeated to prepend/append the string to multiple NameRecords (e.g.: -x 3 -x 5 -x 6).
    """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["0", "1", "3"]),
    help="""
    Use this option to add the prefix/suffix only to the NameRecords matching the provided platformID (0: Unicode, 1:
    Macintosh, 3: Windows).
    """,
)
@click.option(
    "-l",
    "--language-string",
    help="""
    Use this option to append the prefix/suffix only to the NameRecords matching the provided language string.
    
    See epilog for a list of valid language strings.
    """,
)
@click.option("--prefix", type=str, help="The string to be prepended to the NameRecords")
@click.option("--suffix", type=str, help="The suffix to append to the NameRecords")
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def append(
    input_path: Path,
    name_ids: tuple[int],
    platform_id: int,
    language_string: str,
    prefix: str,
    suffix: str,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Appends a prefix and/or a suffix to the specified NameRecords. If no platformID is specified, the prefix/suffix will
    be added to all NameRecords with the specified nameID. If no language string is specified, the prefix/suffix will be
    added to all NameRecords with the specified nameID and platformID.
    """

    if prefix is None and suffix is None:
        logger.error("Please, insert at least a prefix or a suffix to append")
        return

    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    if platform_id:
        platform_id = int(platform_id)

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)
            name_table.append_string(
                name_ids=name_ids,
                platform_id=platform_id,
                language_string=language_string,
                prefix=prefix,
                suffix=suffix,
            )
            if name_table.compile(font) != name_table_copy.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)
        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[tbl_name],
    help="""
    A set of tools to write, delete and modify NameRecords in the ``name`` table.
    """,
)

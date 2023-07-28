import os
from copy import deepcopy, copy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.constants import LANGUAGES_EPILOG
from foundryToolsCLI.Lib.tables.CFF_ import TableCFF
from foundryToolsCLI.Lib.tables.OS_2 import TableOS2
from foundryToolsCLI.Lib.tables.hhea import TableHhea
from foundryToolsCLI.Lib.tables.name import TableName
from foundryToolsCLI.Lib.tables.post import TablePost
from foundryToolsCLI.Lib.utils.bits_tools import unset_nth_bit
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, get_output_dir, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    generic_error_message,
    file_saved_message,
    file_not_changed_message,
    generic_warning_message,
)

CWD = Path.cwd()
tables = click.Group("Tables")


@tables.group("cff")
def tbl_cff():
    """
    A set of command line tools to manipulate the 'CFF' table.
    """
    pass


@tbl_cff.command()
@add_file_or_path_argument()
@click.option("--full-name", "FullName", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] FullName")
@click.option("--family-name", "FamilyName", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] FamilyName")
@click.option("--weight", "Weight", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Weight")
@click.option("--version", "version", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] version")
@click.option("--copyright", "Copyright", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Copyright")
@click.option("--notice", "Notice", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Copyright")
@add_common_options()
def del_names(
    input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overwrite: bool = True, **kwargs
):
    """
    Deletes CFF names from topDict.
    """
    params = {k: v for k, v in kwargs.items() if v}
    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    fonts = get_fonts_in_path(
        input_path=input_path, recalc_timestamp=recalc_timestamp, allow_ttf=False, allow_variable=False
    )
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            cff_table: TableCFF = font["CFF "]
            cff_table_copy = deepcopy(cff_table)

            cff_table.del_top_dict_names(list(params.keys()))

            if cff_table.compile(font) != cff_table_copy.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_cff.command()
@add_file_or_path_argument()
@click.option("--font-names", "fontNames", type=str, help="Sets CFF.cff.fontNames value")
@click.option(
    "--full-name",
    "FullName",
    type=str,
    help="Sets CFF.cff.topDictIndex[0] FullName value",
)
@click.option(
    "--family-name",
    "FamilyName",
    type=str,
    help="Sets CFF.cff.topDictIndex[0] FamilyName value",
)
@click.option("--weight", "Weight", type=str, help="Sets CFF.cff.topDictIndex[0] Weight value")
@click.option("--version", "version", type=str, help="Sets CFF.cff.topDictIndex[0] version value")
@add_common_options()
def set_names(
    input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overWrite: bool = True, **kwargs
):
    """
    Sets CFF names in topDict.
    """

    params = {k: v for k, v in kwargs.items() if v is not None}
    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    fonts = get_fonts_in_path(
        input_path=input_path, recalc_timestamp=recalc_timestamp, allow_ttf=False, allow_variable=False
    )
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            cff_table: TableCFF = font["CFF "]
            cff_table_copy = deepcopy(cff_table)

            cff_table.set_top_dict_names(params)

            if cff_table.compile(font) != cff_table_copy.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite))
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_cff.command()
@add_file_or_path_argument()
@click.option("-os", "--old-string", required=True, help="The string to be replaced")
@click.option(
    "-ns",
    "--new-string",
    required=True,
    help="The string to replace the old string with",
    show_default=True,
)
@add_common_options()
def find_replace(
    input_path: Path,
    old_string: str,
    new_string: str,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overWrite: bool = True,
):
    """
    Finds a string in the following items of CFF table topDict and replaces it with a new string: `version`, `FullName`,
    `FamilyName`, `Weight`, `Copyright`, `Notice`.
    """

    fonts = get_fonts_in_path(
        input_path=input_path, recalc_timestamp=recalc_timestamp, allow_ttf=False, allow_variable=False
    )
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            cff_table: TableCFF = font["CFF "]
            cff_table_copy = deepcopy(cff_table)

            cff_table.top_dict_find_replace(old_string=old_string, new_string=new_string)

            if cff_table.compile(font) != cff_table_copy.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite))
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tables.command()
@add_file_or_path_argument()
@click.option(
    "--rise",
    type=int,
    help="""Sets the `caretSlopeRise` value.""",
)
@click.option(
    "--run",
    type=int,
    help="""Sets the `caretSlopeRun` value.""",
)
@click.option(
    "--offset",
    type=int,
    help="""Sets the `caretOffset` value.""",
)
@click.option(
    "--ascent",
    type=int,
    help="""Sets the `ascent` value.""",
)
@click.option(
    "--descent",
    type=int,
    help="""Sets the `descent` value.""",
)
@click.option(
    "--linegap",
    type=int,
    help="""Sets the `lineGap` value.""",
)
def hhea(input_path: Path, recalc_timestamp: bool = True, output_dir: Path = None, overwrite: bool = True, **kwargs):
    """
    A command line tool to manipulate the 'hhea' table.
    """

    params = {k: v for k, v in kwargs.items() if v is not None}

    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            hhea_table: TableHhea = font["hhea"]

            hhea_table_copy = copy(hhea_table)

            if "rise" in params.keys():
                hhea_table.set_caret_slope_rise(params.get("rise"))

            if "run" in params.keys():
                hhea_table.set_caret_slope_run(params.get("run"))

            if "offset" in params.keys():
                hhea_table.set_caret_offset(params.get("offset"))

            if "ascent" in params.keys():
                hhea_table.set_ascent(params.get("ascent"))

            if "descent" in params.keys():
                hhea_table.set_descent(params.get("descent"))

            if "linegap" in params.keys():
                hhea_table.set_linegap(params.get("linegap"))

            if hhea_table != hhea_table_copy:
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tables.group("name")
def tbl_name():
    """
    A set of command line tools to manipulate the 'name' table.
    """
    pass


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
@add_common_options()
def set_name(
    input_path: Path,
    name_id: int,
    platform_id: int,
    string: str,
    language_string: str,
    recalc_timestamp: bool,
    output_dir: Path,
    overwrite: bool,
) -> None:
    """
    Writes a NameRecord in the 'name' table.
    """

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    if platform_id:
        platform_id = int(platform_id)

    for font in fonts:
        try:
            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)

            name_table.add_name(
                font,
                name_id=name_id,
                string=string,
                platform_id=platform_id,
                language_string=language_string,
            )

            file = Path(font.reader.file.name)
            if name_table_copy.compile(font) != name_table.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
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
@add_common_options()
def del_names(
    input_path: Path,
    name_ids: tuple[int],
    platform_id: int,
    language_string: str,
    recalc_timestamp: bool = False,
    output_dir: Path = None,
    overwrite: bool = True,
):
    """
    Deletes one or more NameRecords.
    """

    fonts = get_fonts_in_path(input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    if platform_id:
        platform_id = int(platform_id)

    for font in fonts:
        try:
            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)

            name_table.del_names(
                name_ids=name_ids,
                platform_id=platform_id,
                language_string=language_string,
            )

            file = Path(font.reader.file.name)
            if name_table_copy.compile(font) != name_table.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_name.command()
@add_file_or_path_argument()
@click.option("-os", "--old-string", required=True, help="The string to be replaced")
@click.option("-ns", "--new-string", required=True, help="The string to replace the old string with")
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
@add_common_options()
def find_replace(
    input_path: Path,
    old_string: str,
    new_string: str,
    name_ids: tuple[int],
    excluded_name_ids: tuple[int],
    platform_id: int,
    recalc_timestamp: bool = False,
    output_dir: Path = None,
    overwrite: bool = True,
):
    """
    Finds a string in the specified NameRecords and replaces it with a new string
    """

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    if platform_id:
        platform_id = int(platform_id)

    for font in fonts:
        try:
            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)

            name_table.find_replace(
                old_string=old_string,
                new_string=new_string,
                name_ids_to_include=name_ids,
                name_ids_to_skip=excluded_name_ids,
                platform_id=platform_id,
            )

            file = Path(font.reader.file.name)
            if name_table_copy.compile(font) != name_table.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_name.command()
@add_file_or_path_argument()
@click.option("--del-all", is_flag=True, help="Deletes also nameIDs 1, 2, 4, 5 and 6.")
@add_common_options()
def del_mac_names(
    input_path: Path,
    del_all: bool = False,
    recalc_timestamp: bool = False,
    output_dir: bool = None,
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

    fonts = get_fonts_in_path(input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
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

            file = Path(font.reader.file.name)
            if name_table_copy.compile(font) != name_table.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
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
@add_common_options()
def append(
    input_path: Path,
    name_ids: tuple[int],
    platform_id: int,
    language_string: str,
    prefix: str,
    suffix: str,
    recalc_timestamp: bool = False,
    output_dir: Path = None,
    overwrite: bool = True,
):
    """
    Appends a prefix and/or a suffix to the specified NameRecords.
    """

    if prefix is None and suffix is None:
        generic_error_message("Please, insert at least a prefix or a suffix to append")
        return

    fonts = get_fonts_in_path(input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    if platform_id:
        platform_id = int(platform_id)

    for font in fonts:
        try:
            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)

            name_table.append_string(
                name_ids=name_ids,
                platform_id=platform_id,
                language_string=language_string,
                prefix=prefix,
                suffix=suffix,
            )
            file = Path(font.reader.file.name)
            if name_table.compile(font) != name_table_copy.compile(font):
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tables.group("os2")
def tbl_os2():
    """
    A set of command line tools to manipulate the 'OS/2' table.
    """
    pass


@tbl_os2.command()
@add_file_or_path_argument()
@add_common_options()
def recalc_x_height(input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overwrite: bool = True):
    """
    Recalculates sxHeight value.
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            os_2: TableOS2 = font["OS/2"]
            if os_2.version < 25:
                generic_warning_message(
                    f"{file.name}: sxHeight is defined only in OS/2 version 2 and up. Current version is {os_2.version}"
                )
                continue

            current = os_2.sxHeight
            x_height = font.recalc_x_height()
            if current == x_height:
                file_not_changed_message(file.relative_to(CWD))
                continue

            os_2.set_x_height(x_height)
            output_file = Path(makeOutputFileName(input=file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@add_common_options()
def recalc_cap_height(
    input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overwrite: bool = True
):
    """
    Recalculates sCapHeight value.
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            os_2: TableOS2 = font["OS/2"]
            if os_2.version < 2:
                generic_warning_message(
                    f"{file.name}: "
                    f"sCapHeight is defined only in OS/2 version 2 and up. Current version is {os_2.version}"
                )
                continue

            current = os_2.sCapHeight
            cap_height = font.recalc_cap_height()
            if current == cap_height:
                file_not_changed_message(file.relative_to(CWD))
                continue

            os_2.set_cap_height(cap_height)
            output_file = Path(makeOutputFileName(input=file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@add_common_options()
def recalc_max_context(
    input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overwrite: bool = True
):
    """
    Recalculates usMaxContext value.
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            os_2: TableOS2 = font["OS/2"]

            if os_2.version < 2:
                generic_warning_message(
                    f"{file.name}: "
                    f"usMaxContext is defined only in OS/2 version 2 and up. Current version is {os_2.version}"
                )
                continue

            current = os_2.usMaxContex
            max_context = font.recalc_max_context()
            if current == max_context:
                file_not_changed_message(file.relative_to(CWD))
                continue

            os_2.usMaxContext = max_context
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@add_common_options()
def recalc_ranges(input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True):
    """
    Generates a temporary Type 1 from the font file using tx, converts that to an OpenType font using makeotf, reads the
    Unicode ranges and codepage ranges from the temporary OpenType font file, and then writes those ranges to the
    original font's OS/2 table.
    """

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            temp_otf_fd, temp_otf_file = font.make_temp_otf()
            temp_font = Font(temp_otf_file)

            os_2: TableOS2 = font["OS/2"]
            os_2_temp: TableOS2 = temp_font["OS/2"]
            current_unicode_ranges = os_2.getUnicodeRanges()
            current_codepage_ranges = os_2.get_codepage_ranges()
            new_unicode_ranges = os_2_temp.getUnicodeRanges()
            new_codepage_ranges = os_2_temp.get_codepage_ranges()

            if current_unicode_ranges != new_unicode_ranges or current_codepage_ranges != new_codepage_ranges:
                os_2.setUnicodeRanges(bits=new_unicode_ranges)
                os_2.set_codepage_ranges(codepage_ranges=new_codepage_ranges)
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

            temp_font.close()
            os.close(temp_otf_fd)
            os.remove(temp_otf_file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@click.option(
    "-it/-no-it",
    "--italic/--no-italic",
    "italic",
    default=None,
    help="Sets or clears the ITALIC bits (`fsSelection` bit 0 and `head` table `macStyle` bit 1).",
)
@click.option(
    "-us/-no-us",
    "--underscore/--no-underscore",
    "underscore",
    default=None,
    help="""
Sets or clears `fsType` bit 1 (UNDERSCORE).
""",
)
@click.option(
    "-ng/-no-ng",
    "--negative/--no-negative",
    "negative",
    default=None,
    help="""
Sets or clears `fsType` bit 2 (NEGATIVE).
""",
)
@click.option(
    "-ol/-no-ol",
    "--outlined/--no-outlined",
    "outlined",
    default=None,
    help="""
Sets or clears `fsType` bit 3 (OUTLINED).
""",
)
@click.option(
    "-st/-no-st",
    "--strikeout/--no-strikeout",
    "strikeout",
    default=None,
    help="""
Sets or clears `fsType` bit 4 (STRIKEOUT).
""",
)
@click.option(
    "-bd/-no-bd",
    "--bold/--no-bold",
    "bold",
    default=None,
    help="Sets or clears the BOLD bits (`OS/2.fsSelection` bit 5 and `head.macStyle` bit 0).",
)
@click.option(
    "-rg",
    "--regular",
    "regular",
    is_flag=True,
    default=None,
    help="""
Sets REGULAR (`fsSelection` bit 6) and clears BOLD (`fsSelection` bit 5, `head.macStyle` bit 0) and ITALIC
(`fsSelection` bit 0, `head.macStyle` bit 1) bits. This is equivalent to `--no-bold --no-italic`.
""",
)
@click.option(
    "-utm/-no-utm",
    "--use-typo-metrics/--no-use-typo-metrics",
    "use_typo_metrics",
    default=None,
    help="""
Sets or clears the USE_TYPO_METRICS bit (`fsSelection` bit 7).

If set, it is strongly recommended that applications use `OS/2.sTypoAscender` - `OS/2.sTypoDescender` + 
`OS/2.sTypoLineGap` as the default line spacing for the font.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection
""",
)
@click.option(
    "-wws/-no-wws",
    "--wws-consistent/--no-wws-consistent",
    "wws_consistent",
    default=None,
    help="""
Sets or clears the WWS bit (`fsSelection` bit 8).

If the `OS/2.fsSelection` bit is set, the font has `name` table strings consistent with a weight/width/slope family
without requiring use of name IDs 21 and 22.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection

Also: https://typedrawers.com/discussion/3857/fontlab-7-windows-reads-exported-font-name-differently
""",
)
@click.option(
    "-obl/-no-obl",
    "--oblique/--no-oblique",
    "oblique",
    default=None,
    help="Sets or clears the OBLIQUE bit (`fsSelection` bit 9).",
)
@click.option(
    "-el",
    "--embed-level",
    "embed_level",
    type=click.Choice(["0", "2", "4", "8"]),
    default=None,
    help="""
Sets/clears `fsType` bits 0-3 (EMBEDDING_LEVEL).

Valid fonts must set at most one of bits 1, 2 or 3; bit 0 is permanently reserved and must be zero. Valid values for
this sub-field are 0, 2, 4 or 8. The meaning of these values is as follows:

\b
0: Installable embedding
2: Restricted License embedding
4: Preview & Print embedding
8: Editable embedding

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
""",
)
@click.option(
    "-ns/-as",
    "--no-subsetting/--allow-subsetting",
    default=None,
    help="""
Sets or clears `fsType` bit 8 (NO_SUBSETTING).

When this bit is set, the font may not be subsetted prior to embedding. Other embedding restrictions specified in bits
0-3 and 9 also apply.
""",
)
@click.option(
    "-beo/-no-beo",
    "--bitmap-embedding-only/--no-bitmap-embedding-only",
    default=None,
    help="""
Sets or clears `fsType` bit 9 (BITMAP_EMBEDDING_ONLY).

When this bit is set, only bitmaps contained in the font may be embedded. No outline data may be embedded. If there are
no bitmaps available in the font, then the font is considered unembeddable and the embedding services will fail. Other
embedding restrictions specified in bits 0-3 and 8 also apply.
""",
)
@add_common_options()
def set_flags(
    input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overwrite: bool = True, **kwargs
):
    """
    Sets/clears the following flags in OS/2.fsSelection and OS/2.fsType fields:

    fsSelection:

    \b
    Bit 0: ITALIC
    Bit 1: UNDERSCORE
    Bit 2: NEGATIVE
    Bit 3: OUTLINED
    Bit 4: STRIKEOUT
    Bit 5: BOLD
    Bit 6: REGULAR
    Bit 7: USE_TYPO_METRICS
    Bit 8: WWS
    Bit 9: OBLIQUE

    fsType:

    \b
    Bits 0-3: Usage permissions
    Bit 8: No subsetting
    Bit 9: Bitmap embedding only
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    options = {k: v for k, v in kwargs.items() if v is not None}
    if len(options) == 0:
        generic_error_message("Please, pass at least one valid parameter.")
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            head = font["head"]
            head_copy = deepcopy(head)
            os2 = font["OS/2"]
            os2_copy = deepcopy(os2)

            for flag, value in options.items():
                if flag in ("use_typo_metrics", "wws_consistent", "oblique") and os2.version < 4:
                    generic_warning_message(
                        f"{flag.upper()} flag can't be set. Bits 7, 8 and 9 are only defined in OS/2 version 4 and up."
                    )
                    continue
                if flag == "embed_level":
                    value = int(value)
                set_flag = getattr(font, f"set_{flag}_flag")
                set_flag(value)

            if head_copy.compile(font) != head.compile(font) or os2_copy.compile(font) != os2.compile(font):
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
            else:
                file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_os2.command()
@click.option("-v", "target_version", type=click.IntRange(1, 5), required=True, help="Target version")
@add_file_or_path_argument()
@add_common_options()
def set_version(
    input_path: Path,
    target_version: int,
    output_dir: Path = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Upgrades OS/2 table version.
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            os_2: TableOS2 = font["OS/2"]
            current_version = getattr(os_2, "version")

            if target_version <= current_version:
                generic_warning_message(f"Current OS/2 table version is already {current_version}")
                file_not_changed_message(file=file.relative_to(CWD))
                continue

            setattr(os_2, "version", target_version)

            # When upgrading from version 0, ulCodePageRanges are to be recalculated.
            if current_version < 1:
                temp_otf_fd, temp_otf_file = font.make_temp_otf()
                temp_otf_font = Font(temp_otf_file)
                temp_os_2: TableOS2 = temp_otf_font["OS/2"]
                os_2.set_codepage_ranges(temp_os_2.get_codepage_ranges())

                temp_otf_font.close()
                os.close(temp_otf_fd)
                os.remove(temp_otf_file)

            # Return if upgrading from version 0 to version 1.
            if target_version == 1:
                font.save(output_file)
                file_saved_message(output_file.relative_to(CWD))
                continue

            # Upgrading from version 1 requires creating sxHeight, sCapHeight, usDefaultChar, usBreakChar and
            # usMaxContext entries.
            if current_version < 2:
                os_2.set_x_height(font.recalc_x_height())
                os_2.set_cap_height(font.recalc_cap_height())
                os_2.set_default_char(0)
                os_2.set_break_char(32)
                os_2.set_max_context(font.recalc_max_context())

            # Write default values if target_version == 5.
            if target_version > 4:
                setattr(os_2, "usLowerOpticalPointSize", 0)
                setattr(os_2, "usUpperOpticalPointSize", 65535 / 20)

            # Finally, make sure to clear bits 7, 8 and 9 in ['OS/2'].fsSelection when target version is lower than 4.
            if target_version < 4:
                for b in (7, 8, 9):
                    setattr(os_2, "fsSelection", unset_nth_bit(os_2.fsSelection, b))

            font.save(output_file)
            file_saved_message(file=output_file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@click.option("-w", "--weight", type=click.IntRange(1, 1000), required=True, help="usWeightClass value.")
@add_common_options()
def set_weight(
    input_path: Path, weight: int, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True
):
    """
    Sets the Weight class value.

    usWeightClass indicates the visual weight (degree of blackness or thickness of strokes) of the characters in the
    font. Values from 1 to 1000 are valid.
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            os_2: TableOS2 = font["OS/2"]

            if weight == os_2.get_weight_class():
                file_not_changed_message(file.relative_to(CWD))
                continue

            os_2.set_weight_class(weight)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@click.option("-w", "--width", type=click.IntRange(1, 9), required=True, help="usWidthClass value.")
@add_common_options()
def set_width(
    input_path: Path, width: int, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True
):
    """
    Sets the Width class value.

    usWidthClass indicates a relative change from the normal aspect ratio (width to height ratio) as specified by a font
    designer for the glyphs in a font. Values from 1 to 9 are valid.
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            os_2: TableOS2 = font["OS/2"]

            if width == os_2.get_width_class():
                file_not_changed_message(file.relative_to(CWD))
                continue

            os_2.set_width_class(width)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            font.save(output_file)
            file_saved_message(output_file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@tables.command()
@add_file_or_path_argument()
@click.option(
    "--italic-angle",
    type=click.FloatRange(-90.0, 90.0),
    help="""Sets the `italicAngle` value.""",
)
@click.option(
    "--ul-position",
    type=int,
    help="""Sets the `underlinePosition` value.""",
)
@click.option(
    "--ul-thickness",
    type=int,
    help="""Sets the `underlineThickness` value.""",
)
@click.option(
    "--fixed-pitch/--no-fixed-pitch",
    default=None,
    help="""Sets or clears the `isFixedPitch` value.""",
)
@add_common_options()
def post(input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overwrite: bool = None, **kwargs):
    """A command line tool to manipulate the 'post' table."""

    params = {k: v for k, v in kwargs.items() if v is not None}

    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            post_table: TablePost = font["post"]
            post_table_copy = copy(post_table)
            if font.is_otf:
                cff_table_copy = copy(font["CFF "])
            else:
                cff_table_copy = None

            # Process the arguments
            if "italic_angle" in params.keys():
                post_table.set_italic_angle(params.get("italic_angle"))
                if font.is_otf:
                    font["CFF "].cff.topDictIndex[0].ItalicAngle = int(params.get("italic_angle"))

            if "ul_position" in params.keys():
                post_table.set_underline_position(params.get("ul_position"))

            if "ul_thickness" in params.keys():
                post_table.set_underline_thickness(params.get("ul_thickness"))

            if "fixed_pitch" in params.keys():
                post_table.set_fixed_pitch(params.get("fixed_pitch"))

            font.save(output_file)

            # Check if tables have changed before saving the font. No need to compile here.
            if not font.is_otf:
                if (post_table.compile(font)) != post_table_copy.compile(font):
                    font.save(output_file)
                    file_saved_message(output_file.relative_to(CWD))
                else:
                    file_not_changed_message(file.relative_to(CWD))

            else:
                if cff_table_copy:
                    if (post_table.compile(font), font["CFF "].compile(font)) != (
                        post_table_copy.compile(font),
                        cff_table_copy.compile(font),
                    ):
                        font.save(output_file)
                        file_saved_message(output_file.relative_to(CWD))
                else:
                    file_not_changed_message(file.relative_to(CWD))

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[tables],
    help="""
    A set of tools to manipulate font tables
    """,
)

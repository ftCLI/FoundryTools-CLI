from copy import deepcopy

import click
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib import constants
from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import check_input_path, check_output_dir
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    file_saved_message,
    file_not_changed_message,
    generic_error_message,
)


@click.group()
def set_namerecord():
    pass


@set_namerecord.command(epilog=constants.language_codes)
@add_file_or_path_argument()
@click.option(
    "-n",
    "--name-id",
    type=click.IntRange(0, 32767),
    required=True,
    help="The nameID of the namerecord to add.",
)
@click.option("-s", "--string", required=True, help="String to write in the namerecord.")
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    help="""
              Use this option to write the namerecord only in the specified table:
              
              \b
              1: Macintosh
              3: Windows
              
              If not specified, namerecord will be written in both tables.""",
)
@click.option(
    "-l",
    "--language-string",
    default="en",
    show_default=True,
    help="""
              Use this option to write the namerecord in a language different than 'en' (e.g.: 'it', 'nl', 'de').
              
              See epilog for a list of valid language strings
              """,
)
@add_common_options()
def set_name(
    input_path,
    name_id,
    platform_id,
    language_string,
    string,
    recalcTimestamp=False,
    outputDir=None,
    overWrite=True,
):
    """
    Adds a namerecord to one or more font files

    `INPUT_PATH` can be a single font file or a directory. If it's a directory, all valid font files found in it will
    be processed.

    If the namerecord is already present, it will be overwritten.
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    # platform_id must be converted to integer because click.Choice() doesn't accept integers (only strings)
    if platform_id is not None:
        platform_id = int(platform_id)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            name_table_copy = deepcopy(font.name_table)

            font.name_table.add_name(
                string=string,
                font=font,
                name_id=name_id,
                platform_id=platform_id,
                language_string=language_string,
            )

            # The copied, and the current `name` tables must be compiled to reorder namerecords before comparison.
            if font.name_table.compile(font) != name_table_copy.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)

            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def del_mac_namerecords():
    pass


@del_mac_namerecords.command()
@add_file_or_path_argument()
@click.option(
    "--del-all",
    is_flag=True,
    help="""
              Deletes also nameIDs 1, 2, 4, 5 and 6.
              """,
)
@add_common_options()
def del_mac_names(input_path, del_all=False, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Deletes all the Macintosh namerecords from the name table, except nameIDs 1, 2, 4, 5, and 6.

    According to Apple (https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html), "names with
    platformID 1 were required by earlier versions of macOS. Its use on modern platforms is discouraged. Use names with
    platformID 3 instead for maximum compatibility. Some legacy software, however, may still require names with
    platformID 1, platformSpecificID 0".
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            name_table_copy = deepcopy(font.name_table)
            name_ids = set(name.nameID for name in font.name_table.names if name.platformID == 1)
            if not del_all:
                for n in (1, 2, 4, 5, 6):
                    try:
                        name_ids.remove(n)
                    except KeyError:
                        pass

            font.name_table.del_names(name_ids=name_ids, platform_id=1)

            if name_table_copy.compile(font) != font.name_table.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def del_namerecords():
    pass


@del_namerecords.command(epilog=constants.language_codes)
@add_file_or_path_argument()
@click.option(
    "-n",
    "--name-id",
    "name_ids",
    type=int,
    required=True,
    multiple=True,
    help="""
              NameID(s) to delete.
              
              This option can be repeated to delete multiple namerecords at once. For example: -n 1 -n 2 -n 6
              """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["0", "1", "3"]),
    help="""
              PlatformID of the namerecords to delete:
              
              \b
              0: Unicode
              1: Macintosh
              3: Windows
              
              If no platform is specified, namerecords will be deleted from all tables.
              """,
)
@click.option(
    "-l",
    "--language-string",
    default=None,
    show_default=True,
    help="""
              Use this option to filter the namerecords to delete by language string (for example: 'it', 'de', 'nl').
              See epilog for a list of valid language strings.
              """,
)
@add_common_options()
def del_names(
    input_path,
    name_ids,
    platform_id,
    language_string,
    recalcTimestamp=False,
    outputDir=None,
    overWrite=True,
):
    """
    Deletes one or more namerecords

    `INPUT_PATH` can be a single font file or a directory. If it's a directory, all valid font files found in it will
    be processed.
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    if platform_id is not None:
        platform_id = int(platform_id)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            name_table_copy = deepcopy(font.name_table)

            font.name_table.del_names(
                name_ids=name_ids,
                platform_id=platform_id,
                language_string=language_string,
            )

            if name_table_copy.compile(font) != font.name_table.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def append_prefix_suffix():
    pass


@append_prefix_suffix.command(epilog=constants.language_codes)
@add_file_or_path_argument()
@click.option(
    "-n",
    "--name-id",
    "name_ids",
    required=True,
    multiple=True,
    type=int,
    help="""
              NameID where to append the prefix/suffix. This option can be repeated to prepend/append the string to
              multiple namerecords. For example: -n 1 -n 2 -n 16 -n 17
              """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["0", "1", "3"]),
    help="""
              Use this option to add the prefix/suffix only to the namerecords matching the provided platformID.
              
              \b
              0: Unicode
              1: Macintosh
              3: Windows
              """,
)
@click.option(
    "-l",
    "--language-string",
    help="""
              Use this option to append the prefix/suffix only to the namerecords matching the provided language string.
              
              See epilog for a list of valid language strings.
              """,
)
@click.option("--prefix", type=str, help="The string to be prepended to the namerecords")
@click.option("--suffix", type=str, help="The suffix to append to the namerecords")
@add_common_options()
def append(
    input_path,
    name_ids,
    platform_id,
    language_string,
    prefix,
    suffix,
    recalcTimestamp=False,
    outputDir=None,
    overWrite=True,
):
    """
    Appends a prefix, or a suffix to the specified namerecords

    `INPUT_PATH` can be a single font file or a directory. If it's a directory, all valid font files found in it will
    be processed.
    """

    if prefix is None and suffix is None:
        generic_error_message("Please, insert at least a prefix or a suffix to append")
        return

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    # Convert to integer because click.Choice() doesn't accept integers
    if platform_id is not None:
        platform_id = int(platform_id)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            name_table_copy = deepcopy(font.name_table)

            font.name_table.append_string(
                name_ids=name_ids,
                platform_id=platform_id,
                language_string=language_string,
                prefix=prefix,
                suffix=suffix,
            )

            # Compile the copy, and the current `name` tables and compare.
            # `if name_table_copy != font.name_table` doesn't work in this case.
            if font.name_table.compile(font) != name_table_copy.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def find_and_replace():
    pass


@find_and_replace.command()
@add_file_or_path_argument()
@click.option("-os", "--old-string", required=True, help="The string to be replaced")
@click.option(
    "-ns",
    "--new-string",
    required=True,
    help="The string to replace the old string with",
    show_default=True,
)
@click.option(
    "-n",
    "--name-id",
    "name_ids",
    type=int,
    multiple=True,
    help="""
              nameIDs where to search and replace the string. If not specified, the string will be replaced in all
              namerecords. This option can be repeated to perform search and replace in multiple namerecords
              (e.g.: -n 1 -n 4 -n 6)
              """,
)
@click.option(
    "-x",
    "--exclude-name-id",
    type=int,
    multiple=True,
    help="""
              NameID to ignore. The specified nameID won't be changed. This option can be repeated multiple
              times (e.g.: -ex 3 -ex 5 -ex 16).
              """,
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    help="""
              platform id [1: macintosh, 3: windows]. If no platform is specified, the string will be replaced in
              both tables.
              """,
)
@add_common_options()
def find_replace(
    input_path,
    old_string,
    new_string,
    name_ids,
    platform_id,
    exclude_name_id,
    recalcTimestamp=False,
    outputDir=None,
    overWrite=True,
):
    """
    Finds a string in the specified namerecords and replaces it with a new string
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    if platform_id is not None:
        platform_id = int(platform_id)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            name_table_copy = deepcopy(font.name_table)

            font.name_table.find_replace(
                old_string=old_string,
                new_string=new_string,
                name_ids_to_include=name_ids,
                name_ids_to_skip=exclude_name_id,
                platform_id=platform_id,
            )

            if name_table_copy.compile(font) != font.name_table.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)

            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


cli = click.CommandCollection(
    sources=[
        set_namerecord,
        append_prefix_suffix,
        del_namerecords,
        del_mac_namerecords,
        find_and_replace,
    ],
    help="""
    Command line name table editor.
    """,
)

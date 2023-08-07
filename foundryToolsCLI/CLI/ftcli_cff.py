from copy import deepcopy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.tables.CFF_ import TableCFF
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, get_output_dir, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    generic_error_message,
    file_saved_message,
    file_not_changed_message,
)

tbl_cff = click.Group("subcommands")


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
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

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
    input_path: Path, recalc_timestamp: bool = False, output_dir: Path = None, overwrite: bool = True, **kwargs
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
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

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
    overwrite: bool = True,
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
                output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[tbl_cff],
    help="""
A set of command line tools to manipulate the 'CFF' table.
""",
)

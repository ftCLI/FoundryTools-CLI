import typing as t

from copy import deepcopy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.tables.CFF_ import TableCFF
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_recursive_option,
    add_common_options,
)
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.timer import Timer

tbl_cff = click.Group("subcommands")


@tbl_cff.command()
@add_file_or_path_argument()
@click.option(
    "--full-name", "FullName", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] FullName"
)
@click.option(
    "--family-name", "FamilyName", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] FamilyName"
)
@click.option("--weight", "Weight", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Weight")
@click.option("--version", "version", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] version")
@click.option(
    "--copyright", "Copyright", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Copyright"
)
@click.option("--notice", "Notice", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Copyright")
@click.option("--unique-id", "UniqueID", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] UniqueID")
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def del_names(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
    **kwargs
):
    """
    Deletes CFF names in topDict.
    """
    params = {k: v for k, v in kwargs.items() if v}
    if len(params) == 0:
        logger.error(Logs.no_parameter)
        return

    fonts = get_fonts_in_path(
        input_path=input_path,
        recursive=recursive,
        recalc_timestamp=recalc_timestamp,
        allow_ttf=False,
        allow_variable=False,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            cff_table: TableCFF = font["CFF "]
            cff_table_copy = deepcopy(cff_table)
            cff_table.del_top_dict_names(list(params.keys()))

            if cff_table.compile(font) != cff_table_copy.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)
        except Exception as e:
            logger.exception(e)
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
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def set_names(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
    **kwargs
):
    """
    Sets CFF names in topDict. If the name is not present, it will be added. If the name is present, it will be
    replaced.
    """

    params = {k: v for k, v in kwargs.items() if v is not None}
    if len(params) == 0:
        logger.error(Logs.no_parameter)
        return

    fonts = get_fonts_in_path(
        input_path=input_path,
        recursive=recursive,
        recalc_timestamp=recalc_timestamp,
        allow_ttf=False,
        allow_variable=False,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            cff_table: TableCFF = font["CFF "]
            cff_table_copy = deepcopy(cff_table)
            cff_table.set_top_dict_names(params)

            if cff_table.compile(font) != cff_table_copy.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
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
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def find_replace(
    input_path: Path,
    old_string: str,
    new_string: str,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Finds a string in the following items of CFF table topDict and replaces it with a new string: `version`, `FullName`,
    `FamilyName`, `Weight`, `Copyright`, `Notice`.
    """

    fonts = get_fonts_in_path(
        input_path=input_path,
        recursive=recursive,
        recalc_timestamp=recalc_timestamp,
        allow_ttf=False,
        allow_variable=False,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            cff_table: TableCFF = font["CFF "]
            cff_table_copy = deepcopy(cff_table)

            cff_table.top_dict_find_replace(old_string=old_string, new_string=new_string)

            if cff_table.compile(font) != cff_table_copy.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[tbl_cff],
    help="""
A set of command line tools to manipulate the 'CFF' table.
""",
)

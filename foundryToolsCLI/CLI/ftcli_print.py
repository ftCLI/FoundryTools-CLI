from pathlib import Path
from typing import Optional

import click

from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, get_variable_fonts_in_path
from foundryToolsCLI.Lib.utils.click_tools import add_file_or_path_argument
from foundryToolsCLI.Lib.utils.logger import logger

ftcli_printer = click.Group("subcommands")


@ftcli_printer.command()
@add_file_or_path_argument()
def font_info(input_path: Path):
    """
    Prints detailed font info.
    """
    from foundryToolsCLI.Lib.printer.UI import print_font_info

    fonts = get_fonts_in_path(input_path=input_path)
    for font in fonts:
        try:
            print_font_info(font)
        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@ftcli_printer.command()
@add_file_or_path_argument()
@click.option(
    "-ml",
    "--max-lines",
    type=click.INT,
    default=None,
    help="Maximum number of lines to be printed for each NameRecord",
)
@click.option(
    "-m",
    "--minimal",
    is_flag=True,
    help="""
    Prints a minimal set of NameRecords, omitting the ones with nameID not in 1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22, 25
    """,
)
def font_names(input_path: Path, max_lines: Optional[int] = None, minimal: bool = False):
    """
    Prints the 'name' table and, if the font is CFF, the names in the 'CFF' table topDict.
    """
    from foundryToolsCLI.Lib.printer.UI import print_font_names

    fonts = get_fonts_in_path(input_path=input_path)
    for font in fonts:
        try:
            print_font_names(font, max_lines=max_lines, minimal=minimal)
        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@ftcli_printer.command()
@add_file_or_path_argument()
def fonts_list(input_path: Path):
    """
    Prints a list of fonts with basic information.
    """
    from foundryToolsCLI.Lib.printer.UI import print_fonts_list

    fonts = get_fonts_in_path(input_path=input_path)
    print_fonts_list(fonts=fonts)


@ftcli_printer.command()
@add_file_or_path_argument()
def tbl_os2(input_path: Path):
    """
    Prints the OS/2 table.
    """
    from foundryToolsCLI.Lib.printer.UI import print_os2_table

    fonts = get_fonts_in_path(input_path=input_path)
    for font in fonts:
        try:
            print_os2_table(font)
        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@ftcli_printer.command()
@add_file_or_path_argument()
def vf_instances(input_path: Path):
    """
    Prints a table of the named instances of a variable font.
    """
    from foundryToolsCLI.Lib.printer.UI import print_instances

    variable_fonts = get_variable_fonts_in_path(input_path)
    for variable_font in variable_fonts:
        try:
            print_instances(variable_font)
            variable_font.close()
        except Exception as e:
            logger.exception(e)
        finally:
            variable_font.close()


cli = click.CommandCollection(
    sources=[ftcli_printer],
    help="""
    Prints various fonts information and tables.
    """,
)

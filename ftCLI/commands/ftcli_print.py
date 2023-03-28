import os
from pprint import pprint

import click

from ftCLI.Lib.Font import Font
from ftCLI.Lib.cui import CUI
from ftCLI.Lib.utils.cli_tools import get_fonts_list
from ftCLI.Lib.utils.click_tools import generic_error_message, add_file_or_path_argument


@click.group()
def print_font_list():
    pass


@print_font_list.command()
@add_file_or_path_argument()
def fonts_list(input_path):
    """
    Prints a list of fonts with basic information.
    """
    files = get_fonts_list(input_path)
    if len(files) == 0:
        generic_error_message(f"No valid font files found in {input_path}.")
        return
    CUI.print_fonts_list(files)


@click.group()
def print_font_info():
    pass


@print_font_info.command()
@add_file_or_path_argument()
def font_info(input_path):
    """
    Prints detailed font info.
    """
    if len(get_fonts_list(input_path)) > 0:
        for file in get_fonts_list(input_path):
            try:
                font = Font(file)
                CUI.print_font_info(font)
            except Exception as e:
                generic_error_message(e)
    else:
        click.secho("\nNo valid fonts found in {}".format(input_path), fg="red")


@click.group()
def print_font_os2_table():
    pass


@print_font_os2_table.command()
@add_file_or_path_argument()
def os2_table(input_path):
    """
    Prints the OS/2 table.
    """
    if len(get_fonts_list(input_path)) > 0:
        for file in get_fonts_list(input_path):
            try:
                font = Font(file)
                CUI.print_os2_table(font)
            except Exception as e:
                generic_error_message(e)
    else:
        generic_error_message("No valid font files found")


@click.group()
def print_font_names():
    pass


@print_font_names.command()
@add_file_or_path_argument()
@click.option(
    "-ml",
    "--max-lines",
    type=click.INT,
    default=None,
    help="Maximum number of lines to be printed for each namerecord",
)
@click.option(
    "-m",
    "--minimal",
    is_flag=True,
    help="""
              Prints a minimal set of namerecords, omitting the ones with nameID not in 1, 2, 3, 4, 5, 6, 16, 17, 18, 
              21, 22, 25
              """,
)
def font_names(input_path, max_lines, minimal=False):
    """
    Prints the `name` table and, if the font is CFF, the names in the `CFF` table topDict.
    """
    if len(get_fonts_list(input_path)) > 0:
        for file in get_fonts_list(input_path):
            try:
                font = Font(file)
                CUI.print_font_names(font, max_lines=max_lines, minimal=minimal)
            except Exception as e:
                generic_error_message(e)
    else:
        generic_error_message("No valid font files found.")


cli = click.CommandCollection(
    sources=[print_font_list, print_font_info, print_font_names, print_font_os2_table],
    help="""
Prints various fonts information and tables.
""",
)
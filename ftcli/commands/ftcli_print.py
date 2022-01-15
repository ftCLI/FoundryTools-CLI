import click

from ftcli.Lib.CUI import CUI
from ftcli.Lib.utils import getFontsList


# printName

@click.group()
def printName():
    pass


@printName.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-n', '--name-id', type=click.IntRange(0, 32767), required=True,
              help="nameID (Integer between 0 and 32767)")
@click.option('-ml', '--max-lines', type=click.INT, default=None,
              help="Maximum number of lines to be printed.")
def ft_name(input_path, name_id, max_lines):
    """Prints a single namerecord.

    Use the -ml, --max-lines option to limit the printed line numbers to the desired value.
    """
    CUI().printFtName(input_path, name_id=name_id, max_lines=max_lines)


# printNames


@click.group()
def printNames():
    pass


@printNames.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-ml', '--max-lines', type=click.INT, default=None,
              help="Maximum number of lines to be printed for each namerecord")
@click.option('-min', '--minimal', is_flag=True,
              help="Prints only nameIDs 1, 2, 3, 4, 5, 6, 16, 17, 18, 21 and 22.")
def ft_names(input_path, max_lines, minimal):
    """Prints the 'name' table and 'CFF' names (if present).

    Use the -ml / --max-lines option to limit the printed line numbers, and the -min / --minimal one to print a minimal
    set of namerecords.
    """

    if len(getFontsList(input_path)) > 0:
        CUI().printFtNames(input_path, max_lines=max_lines, minimal=minimal)
    else:
        click.secho('\n{} is not a valid font'.format(input_path), fg='red')


# printFontInfo


@click.group()
def printFontInfo():
    pass


@printFontInfo.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
def ft_info(input_path):
    """Prints detailed font information.
    """

    if len(getFontsList(input_path)) > 0:
        CUI().printFtInfo(input_path)
    else:
        click.secho('\n{} is not a valid font'.format(input_path), fg='red')


# printFontsList


@click.group()
def printFontsList():
    pass


@printFontsList.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
def ft_list(input_path):
    """Prints a list of fonts with basic information.
    """
    if len(getFontsList(input_path)) > 0:
        CUI().printFtList(input_path)
    else:
        click.secho('\nNo valid fonts found in {}'.format(
            input_path), fg='red')


# printHeadTable
@click.group()
def printHeadTable():
    pass


@printHeadTable.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True, dir_okay=False))
def tbl_head(input_path):
    """Prints the 'head' table.
    """
    if len(getFontsList(input_path)) > 0:
        CUI().printTableHead(input_path)
    else:
        click.secho('No valid font found.', fg='red')


# printOS2Table


@click.group()
def printOS2Table():
    pass


@printOS2Table.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True, dir_okay=False))
def tbl_os2(input_path):
    """Prints the 'OS/2' table.
    """
    if len(getFontsList(input_path)) > 0:
        CUI().printTableOS2(input_path)
    else:
        click.secho('No valid font found.', fg='red')


cli = click.CommandCollection(sources=[printName, printNames, printFontInfo, printFontsList, printOS2Table,
                                       printHeadTable], help="""
Prints various font's information.
""")

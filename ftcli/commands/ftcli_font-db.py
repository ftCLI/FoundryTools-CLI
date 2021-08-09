import os.path

import click

from ftcli.Lib.DataHandler import DataHandler
from ftcli.Lib.configHandler import configHandler
from ftcli.Lib.utils import getConfigPath, getJsonPath


@click.group()
def resetFtDb():
    pass


@resetFtDb.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-c', '--config-file', type=click.Path(exists=True, resolve_path=True),
              help='Use a custom configuration file instead of the default config.json file located in the same folder '
                   'of INPUT_PATH.')
def reset(input_path, config_file):

    if not config_file:
        config_file = getConfigPath(input_path)

    if not os.path.exists(config_file):
        configHandler(config_file).resetConfig()
        click.secho("\n{} didn't exist and has been created".format(
            config_file), fg='green')

    json_file = getJsonPath(input_path)

    DataHandler(json_file).resetFontsDatabase(config_file=config_file)

    print(f'\n{json_file} saved.')


@click.group()
def recalcFtDb():
    pass


@recalcFtDb.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-c', '--config-file', type=click.Path(exists=True, resolve_path=True),
              help='Use a custom configuration file instead of the default config.json file located in the same folder'
                   ' of INPUT_PATH.')
@click.option('-f', '--family-name', default=None,
              help="The desired family name. This string will be used to recalculate the CSV lines.")
@click.option('-s', '--source-string', type=click.Choice(
    choices=('fname', '1_1_2', '1_4', '1_6', '1_16_17', '1_18', '3_1_2', '3_4', '3_6', '3_16_17', 'cff_1', 'cff_2')),
              default='fname', show_choices=True, show_default=True,
              help="""
The source string be used to recalculate the CSV lines can be the file name, a namerecord, a combination of namerecords
or values stored in the 'CFF' table.

For example, -s '1_1_2' will read a combination of namerecords 1 and 2 in the Mac table.
""")
def recalc(input_path, config_file, family_name, source_string):

    if not config_file:
        config_file = getConfigPath(input_path)

    if not os.path.exists(config_file):
        configHandler(config_file).resetConfig()
        click.secho("\n{} didn't exist and has been created".format(
            config_file), fg='green')

    json_file = getJsonPath(input_path)
    if not os.path.exists(json_file):
        DataHandler(json_file).resetFontsDatabase(config_file=config_file)

    DataHandler(json_file).recalcFontsDatabase(config_file=config_file, family_name=family_name,
                                               source_string=source_string)

    print(f'\n{json_file} saved.')


cli = click.CommandCollection(
    sources=[resetFtDb, recalcFtDb],
    help=
    """
    help here
    """
)

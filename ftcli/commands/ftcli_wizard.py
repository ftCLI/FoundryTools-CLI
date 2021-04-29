import os
import sys

import click
from fontTools.ttLib import TTFont
from ftcli.Lib.configHandler import configHandler
from ftcli.Lib.csvHandler import csvHandler
from ftcli.Lib.pyFont import pyFont
from ftcli.Lib.GUI import GUI
from ftcli.Lib.utils import (getConfigPath, getCsvPath, getFontsList,
                             makeOutputFileName)


# edit-csv
@click.group()
def editCSV():
    pass


@editCSV.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-c', '--config-file', type=click.Path(exists=True, resolve_path=True),
              help='Use a custom configuration file instead of the default config.json file located in the same folder of INPUT_PATH.')
def edit_csv(input_path, config_file):
    """
    Command line editor for 'data.csv' files.

    This tool is not intended to replace a code editor for CSV files,
    but can help to make small edits without leaving the command line.
    For complex projects, it's strongly recommendedto use a code
    editor like Visual Studio Code or even Excel.
    """

    if not config_file:
        config_file = getConfigPath(input_path)

    if not os.path.exists(config_file):
        configHandler(config_file).resetConfig()

    csv_file = getCsvPath(input_path)
    if not os.path.exists(csv_file):
        confirm = click.confirm(
            "\n%s doesn't exist. Do you want to create it" % csv_file, default=True)
        if confirm:
            csvHandler(csv_file).resetCSV(config_file=config_file)
        else:
            return

    GUI().csvEditor(config_file=config_file, csv_file=csv_file)


# edit-cfg
@click.group()
def editCFG():
    pass


@editCFG.command()
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def edit_cfg(config_file):
    """
Command line editor for JSON configuration files.

Example:

    ftcli wizard edit-cfg "C:\\Fonts\\config.json"

It is strongly recommended to use this tool to edit the JSON configuration
files. It prevents malformed JSON errors and errors due to wrong values (for
example, an out of range usWeightClass, or a string where's an integer is
expected).
    """

    GUI().cfgEditor(config_file)


# init-csv
@click.group()
def initCSV():
    pass


@initCSV.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-c', '--config-file', type=click.Path(exists=True, resolve_path=True),
              help='Use a custom configuration file instead of the default config.json file located in the same folder of INPUT_PATH.')
@click.option('-q', '--quiet', is_flag=True,
              help='Suppress the overwrite confirmation message if the data.csv and/or config.json files already exist.')
def init_csv(input_path, config_file, quiet):
    """
Creates or resets the CSV database file (data.csv).

Example 1:

    ftcli wizard init-csv "C:\\Fonts\\"

The above command will create the 'data.csv' file in C:\\Fonts\\
(and a configuration file with default values if it does not exist).

Example 2:

    ftcli wizard init-csv "C:\\Fonts\\pyFont.otf"

The above command will create the 'data.csv' in the INPUT_PATH folder
(or parent folder, if INPUT_PATH is a file).

data.csv file contains:

- the file names;

- the usWidthClass, usWeightClass, bold and italic bits values of all
font files found in INPUT_PATH;

- tries to guess the family name reading the name table. It also
contains weight and widths literals, retrieved parsing the config.json
file.

It can be edited manually or using the 'ftcli wizard edit-csv INPUT_PATH'
command.
    """

    if not config_file:
        config_file = getConfigPath(input_path)

    if not os.path.exists(config_file) or quiet:
        configHandler(config_file).resetConfig()
        click.secho('\n{} didn\'t exist and has been created'.format(
            config_file), fg='green')

    csv_file = getCsvPath(input_path)
    if not os.path.exists(csv_file) or quiet:
        confirm_overwrite = True
    else:
        confirm_overwrite = click.confirm(
            '{} already exists. Do you want to overwrite it?'.format(csv_file))

    if confirm_overwrite:
        if not os.path.exists(config_file):
            configHandler(config_file).resetConfig()
        csvHandler(csv_file).resetCSV(config_file=config_file)
        click.secho('{} created'.format(csv_file), fg='green')


# init-cfg
@click.group()
def initCFG():
    pass


@initCFG.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True, file_okay=False))
@click.option('-q', '--quiet', is_flag=True,
              help='Suppress the overwrite confirmation message if the config.json file already exists.')
def init_cfg(input_path, quiet):
    """
    Creates a JSON configuration file containing the default values in the specified INPUT_PATH folder.
    """
    config_file = getConfigPath(input_path)

    if not os.path.exists(config_file) or quiet:
        confirm_overwrite = True
    else:
        confirm_overwrite = click.confirm(
            '\n{} already exists. Do you want to overwrite it?'.format(config_file))
    if confirm_overwrite:
        configHandler(config_file).resetConfig()
        click.secho('{} created'.format(config_file), fg='green')


# recalc-csv
@click.group()
def recalcCSV():
    pass


@recalcCSV.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-c', '--config-file', type=click.Path(exists=True, resolve_path=True),
              help='Use a custom configuration file instead of the default config.json file located in the same folder of INPUT_PATH.')
@click.option('-f', '--family-name', default=None,
              help="The desired family name. This string will be used to recalculate the CSV lines.")
@click.option('-s', '--source-string', type=click.Choice(
    choices=('fname', '1_1_2', '1_4', '1_6', '1_16_17', '1_18', '3_1_2', '3_4', '3_6', '3_16_17', 'cff_1', 'cff_2', 'cff_3')),
    default='fname', show_choices=True, show_default=True,
    help="""
The source string be used to recalculate the CSV lines can be the file name, a namerecord, a combination of namerecords or values sotred in the 'CFF' table.

For example, -s '1_1_2' will read a combination of namerecords 1 and 2 in the Mac table.
""")
@click.option('-q', '--quiet', is_flag=True,
              help='Suppress the overwrite confirmation message if the data.csv file already exists.')
def recalc_csv(input_path, config_file, family_name, source_string, quiet):
    """
Recalculates the CSV database file (data.csv).
    """
    csv_file = getCsvPath(input_path)

    if not config_file:
        config_file = getConfigPath(input_path)

    # If config.json doesn't exist, it has to be created before.
    if not os.path.exists(config_file):
        configHandler(config_file).resetConfig()
        click.secho('\n{} didn\'t exist and has been created'.format(
            config_file), fg='yellow')

    if os.path.exists(csv_file) and not quiet:
        confirmation = click.confirm(
            '\n{} already exists. Do you want to overwrite it?'.format(csv_file))
        if confirmation is True:
            csvHandler(csv_file).recalcCSV(
                config_file=config_file, family_name=family_name, source_string=source_string)
            click.secho('\n{} created'.format(csv_file), fg='green')
    else:
        # Let's ensure that, if the data.csv file doesn't exist,
        # it is created before recalculation.
        if not os.path.exists(csv_file):
            csvHandler(csv_file).resetCSV(config_file=config_file)

        csvHandler(csv_file).recalcCSV(
            config_file=config_file, family_name=family_name, source_string=source_string)
        click.secho('\n{} created'.format(csv_file), fg='green')


# recalc-names
@click.group()
def recalcNames():
    pass


@recalcNames.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-c', '--config-file', type=click.Path(exists=True, resolve_path=True),
              help='Use a custom configuration file instead of the default config.json file located in the same folder of INPUT_PATH.')
@click.option('-ls', '--linked-styles', type=(click.IntRange(1, 1000), click.IntRange(1, 1000)), default=(None, None),
              help="Use this option to activate linked styles. If this option is active, linked styles must be specified. For example: -ls 400 700, or -ls 300 600.")
@click.option('-ex', '--exclude-namerecords', type=click.Choice(choices=['1', '2', '3', '4', '5', '6', '16', '17', '18']), multiple=True,
              help="Name IDs to skip. The specified name IDs won't be recalculated. This option can be repeated (example: -ex 3 -ex 5 -ex 6...).")
@click.option('-swdt', '--shorten-width', type=click.Choice(choices=['1', '2', '3', '4', '5', '6', '16', '17', '18']), multiple=True,
              help="Name IDs where to use the short word for width style name (example: 'Cond' instead of 'Condensed'). This option can be repeated (example: -swdt 3 -swdt 5 -swdt 6...).")
@click.option('-swgt', '--shorten-weight', type=click.Choice(choices=['1', '2', '3', '4', '5', '6', '16', '17', '18']), multiple=True,
              help="Name IDs where to use the short word for weight style name (example: 'Md' instead of 'Medium'). This option can be repeated (example: -swgt 3 -swgt 5 -swgt 6...).")
@click.option('-sita', '--shorten-italic', type=click.Choice(choices=['1', '2', '3', '4', '5', '6', '16', '17', '18']), multiple=True,
              help="Name IDs where to use the short word for italic style name (example: 'It' instead of 'Italic'). This option can be repeated (example: -sita 3 -sita 5 -sita 6...).")
@click.option('-sf', '--super-family', is_flag=True,
              help="Superfamily mode. This option affects name IDs 3, 6, 16 and 17 in case of families with widths different than 'Normal'. If this option is active, name ID 6 will be 'FamilyName-WidthWeightSlope' instead of 'FamilyNameWidth-WeightSlope'. Mac and OT family/subfamily names will be Family Name / Width Weight Slope' instead of 'Family Name Width / Weight Slope'.")
@click.option('-aui', '--alt-uid', is_flag=True,
              help="Use alternate unique identifier. By default, namerecord 3 (Unique identifier) is calculated according to the following scheme: 'Version;Vendor code;PostscriptName'. The alternate unique identifier is calculated according to the following scheme: 'Manufacturer: Full pyFont Name: creation year'")
@click.option('-ri', '--regular-italic', is_flag=True,
              help="Use '-RegularItalic' instead of '-Italic' in name ID 6.")
@click.option('-kr', '--keep-regular', is_flag=True,
              help="Use '-RegularItalic' instead of '-Italic' in name ID 6 and 'Regular Italic' instead of 'Italic' in name IDs 2 (Mac only), 4, 17 and 18.")
@click.option('-offn', '--old-full-font-name', is_flag=True,
              help="Full font name in Microsoft name table is generally a combination of name IDs 1 and 2 or 16 and 17. With this option active, it will be equal to name ID 6 (PostScriptName).")
@click.option('-cff', '--fix-cff', is_flag=True,
              help="fontNames, FullName, FamilyName and Weight values in the 'CFF' table will be recalculated.")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file name). By default, files are overwritten.')
def recalc_names(
    input_path,
    config_file,
    linked_styles,
    exclude_namerecords,
    shorten_width,
    shorten_weight,
    shorten_italic,
    fix_cff,
    super_family,
    alt_uid,
    regular_italic,
    keep_regular,
    old_full_font_name,
    output_dir,
    recalc_timestamp,
    overwrite
):
    """
    Recalculates namerecords according to the values stored in the data.csv file.
    """

    files = getFontsList(input_path)
    if len(files) == 0:
        click.secho('\nNo fonts found.', fg='red')
        sys.exit()

    if not config_file:
        config_file = getConfigPath(input_path)

    # If config.json doesn't exist, it has to be created before.
    if not os.path.exists(config_file):
        configHandler(config_file).resetConfig()
        click.secho('\n{} didn\'t exist and has been created'.format(
            config_file), fg='yellow')

    config = configHandler(config_file).getConfig()

    italics = config['italics']
    italics.sort(key=len)

    csv_file = getCsvPath(input_path)
    if not os.path.exists(csv_file):
        csvHandler(csv_file).resetCSV(config_file=config_file)
    data = csvHandler(csv_file).getData()

    # Checks if the file name is present in the CSV data. If the file name
    # is not present, the file is removed from the list of files and will
    # not be processed.
    csv_filenames = [row['file_name'] for row in data]
    files = [f for f in files if os.path.basename(f) in csv_filenames]

    shorten_width = [int(i) for i in shorten_width]
    shorten_weight = [int(i) for i in shorten_weight]
    shorten_italic = [int(i) for i in shorten_italic]
    exclude_namerecords = [int(i) for i in exclude_namerecords]

    # We convert the linked_styles tuple to a list and then sort it.
    linked_styles = tuple(set(linked_styles))
    linked_styles = list(linked_styles)
    linked_styles.sort()

    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)
            font_data = {}
            for row in data:
                if str(row['file_name']) == os.path.basename(f):
                    font_data = row

            pyFont(font).recalcNames(
                font_data, italics,
                linked_styles=linked_styles, namerecords_to_ignore=exclude_namerecords,
                shorten_weight=shorten_weight, shorten_width=shorten_width, shorten_italic=shorten_italic,
                alt_uid=alt_uid, fixCFF=fix_cff, isSuperFamily=super_family, regular_italic=regular_italic, keep_regular=keep_regular, old_full_font_name=old_full_font_name)

            output_file = makeOutputFileName(
                f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('{} saved'.format(output_file), fg='green')
        except:
            click.secho('{} is not a valid font'.format(f), fg='red')
            pass


cli = click.CommandCollection(sources=[editCFG, editCSV, initCFG, initCSV, recalcCSV, recalcNames], help="""
A set of tools to correctly compile the name table and set proper values
for usWeightClass, usWidthClass, bold and italic bits.

The process requires a JSON configuration file and a CSV file that will be
used to fix the fonts. Both files can be automatically created and
eventually edited manually or using the integrated command line editor.

1) The JSON configuration file.

The 'config.json' file contains the desired style names to pair with each
usWidthClass and usWeightClass values of the family, as well as the italic
literals:

\b
{
    "italics": ["It", "Italic"],
\b
    "weights": {
        "250": ["Th", "Thin"],
        "275": ["ExLt", "ExtraLight"],
        ...
    },
\b
    "widths": {
        "1": ["Cm", "Compressed"],
        "2": ["ExCn", "ExtraCondensed"],
        ...
    }
}

Unless you have previously created a configuration file and want to reuse
it, you need to create a standard configuration file and eventually
customize it.

    ftcli wizard init-cfg INPUT_PATH

The above command will create a file named 'config.json' in the INPUT_PATH
folder (or parent folder if INPUT_PATH is a file).

Once created the configuration file, you may be in need to edit it according
to your needs.

    ftcli wizard edit-cfg CONFIG_FILE

Values contained in the configuration file will be used to fill the data.csv
file in the next steps.

2) The CSV data file.

The final data.csv file will contain the desired style names, family name,
italic bits, usWidth class and usWeightClass values. Once properly filled,
the values contained in this file will be written to the fonts.

It contains 10 columns:

\b
file_name
is_bold 
is_italic
uswidthclass
wdt
width
usweightclass
wgt
weight
family_name

The 'is_bold' column is present only for completeness, but it's values will be
ignored. A font will be set as bold only and only if, during the names recalculation,
the user will choose to use linked styles (-ls / --linked styles option).

The 'wdt' and 'width' columns contain the short and long literals for the width
style names (for example: Cn; Condensed).

The 'wgt' and 'weight' columns contain the short and long literals for the weight
style names (for example: Lt, Light).

The user will choose the namerecords where to write long or short literals.

The 'data.csv' file can be created using the following command:

    ftcli wizard init-csv INPUT_PATH

At this point, the CSV file will contain a representation of the actual state of the
fonts (the family_name column will contain values of nameID 16, or nameID 1 if 16 is
not present). It can be edited manually, using the 'ftcli wizard edit-csv' command and
also automatically recalculated using the 'ftcli wizard-recalc-csv' command.

The 'ftcli wizard-recalc-csv' command will recalculate style names, italic bits, width
and weight style names according to the values contained in the JSON configuration file.

When the 'data.csv' file contains the desired values, these values can be applied to fonts
running the 'ftcli wizard recalc-names' command (see 'ftcli wizard recalc-names --help' for
more informations).

    """)

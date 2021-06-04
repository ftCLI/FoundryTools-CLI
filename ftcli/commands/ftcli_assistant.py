import os
import sys

import click

from ftcli.Lib.GUI import GUI
from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.configHandler import configHandler
from ftcli.Lib.csvHandler import csvHandler
from ftcli.Lib.utils import (getConfigPath, getCsvPath, getFontsList, makeOutputFileName)


# edit-csv
@click.group()
def editCSV():
    pass


@editCSV.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-c', '--config-file', type=click.Path(exists=True, resolve_path=True),
              help='Use a custom configuration file instead of the default config.json file located in the same folder'
                   'of INPUT_PATH.')
def edit_csv(input_path, config_file):
    """Command line editor for 'data.csv' files.

    This tool is not intended to replace a code editor for CSV files, but can help to make small edits without leaving
    the command line. For complex projects, it's strongly recommended to use an editor like Notepad++, Visual Studio
    Code or even Excel.
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
    """Command line editor for JSON configuration files.

    Example:

        ftcli assistant edit-cfg "C:\\Fonts\\config.json"

    It is strongly recommended to use this tool to edit the JSON configuration files. It prevents malformed JSON errors
    and errors due to wrong values (for example, an out of range usWeightClass, or a string where's an integer is
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
              help='Use a custom configuration file instead of the default config.json file located in the same folder'
                   ' of INPUT_PATH.')
@click.option('-q', '--quiet', is_flag=True,
              help='Suppress the overwrite confirmation message if the data.csv and/or config.json files already'
                   ' exist.')
def init_csv(input_path, config_file, quiet):
    """Creates or resets the CSV database file (data.csv).

    Example 1:

        ftcli assistant init-csv "C:\\Fonts\\"

    The above command will create the 'data.csv' file in C:\\Fonts\\
    (and a configuration file with default values if it does not exist).

    Example 2:

        ftcli assistant init-csv "C:\\Fonts\\Font.otf"

    The above command will create the 'data.csv' in the INPUT_PATH folder
    (or parent folder, if INPUT_PATH is a file).

    data.csv file contains:

    - the file names;

    - the usWidthClass, usWeightClass, bold and italic bits values of all
    font files found in INPUT_PATH;

    - tries to guess the family name reading the name table. It also
    contains weight and widths literals, retrieved parsing the config.json
    file.

    It can be edited manually or using the 'ftcli assistant edit-csv INPUT_PATH'
    command.
    """

    if not config_file:
        config_file = getConfigPath(input_path)

    if not os.path.exists(config_file) or quiet:
        configHandler(config_file).resetConfig()
        click.secho("\n{} didn't exist and has been created".format(
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
@click.option('-q', '--quiet', is_flag=True,
              help='Suppress the overwrite confirmation message if the data.csv file already exists.')
def recalc_csv(input_path, config_file, family_name, source_string, quiet):
    """Recalculates font attributes and style names in the CSV database file (data.csv).

    The script will try to recalculate font attributes (usWidthClass, usWeightClass, italic and oblique bits) and style
    names parsing a string provided by the user with the '-s/--source string option'. The source string can be a
    namerecord, a combination of two namerecords, a name in CFF table or the file name.
    """
    csv_file = getCsvPath(input_path)

    if not config_file:
        config_file = getConfigPath(input_path)

    # If config.json doesn't exist, it has to be created before.
    if not os.path.exists(config_file):
        configHandler(config_file).resetConfig()
        click.secho("\n{} didn't exist and has been created".format(
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
              help='Use a custom configuration file instead of the default config.json file located in the same folder'
                   ' of INPUT_PATH.')
@click.option('-ls', '--linked-styles', type=(click.IntRange(1, 1000), click.IntRange(1, 1000)), default=(None, None),
              help="Use this option to activate linked styles. If this option is active, linked styles must be"
                   " specified. For example: -ls 400 700, or -ls 300 600.")
@click.option('-ex', '--exclude-namerecords', type=click.Choice(
    choices=['1', '2', '3', '4', '5', '6', '16', '17', '18']), multiple=True,
              help="Name IDs to skip. The specified name IDs won't be recalculated. This option can be repeated"
                   " (example: -ex 3 -ex 5 -ex 6...).")
@click.option('-swdt', '--shorten-width', type=click.Choice(choices=['1', '2', '3', '4', '5', '6', '16', '17', '18']),
              multiple=True,
              help="Name IDs where to use the short word for width style name (example: 'Cond' instead of 'Condensed')."
                   " This option can be repeated (example: -swdt 3 -swdt 5 -swdt 6...).")
@click.option('-swgt', '--shorten-weight', type=click.Choice(choices=['1', '2', '3', '4', '5', '6', '16', '17', '18']),
              multiple=True,
              help="Name IDs where to use the short word for weight style name (example: 'Md' instead of 'Medium')."
                   " This option can be repeated (example: -swgt 3 -swgt 5 -swgt 6...).")
@click.option('-sslp', '--shorten-slope', type=click.Choice(choices=['1', '2', '3', '4', '5', '6', '16', '17', '18']),
              multiple=True,
              help="Name IDs where to use the short word for slope style name (example: 'It' instead of 'Italic')."
                   " This option can be repeated (example: -sita 3 -sita 5 -sita 6...).")
@click.option('-sf', '--super-family', is_flag=True,
              help="Superfamily mode. This option affects name IDs 3, 6, 16 and 17 in case of families with widths"
                   " different than 'Normal'. If this option is active, name ID 6 will be 'FamilyName-WidthWeightSlope'"
                   " instead of 'FamilyNameWidth-WeightSlope'. Mac and OT family/subfamily names will be FamilyName / "
                   " Width Weight Slope' instead of 'Family Name Width / Weight Slope'.")
@click.option('-aui', '--alt-uid', is_flag=True,
              help="Use alternate unique identifier. By default, nameID 3 (Unique identifier) is calculated"
                   " according to the following scheme: 'Version;Vendor code;PostscriptName'. The alternate unique"
                   " identifier is calculated according to the following scheme: 'Manufacturer: Full Font Name:"
                   " Creation Year'")
@click.option('-ri', '--regular-italic', is_flag=True,
              help="Keep '-Regular' in nameID 6.")
@click.option('-kr', '--keep-regular', is_flag=True,
              help="Keep the 'Regular' word in all nameIDs")
@click.option('-offn', '--old-full-font-name', is_flag=True,
              help="Full font name in Microsoft name table is generally a combination of name IDs 1 and 2 or 16 and 17."
                   " With this option active, it will be equal to nameID 6 (PostScriptName).")
@click.option('-cff', '--fix-cff', is_flag=True,
              help="fontNames, FullName, FamilyName and Weight values in the 'CFF' table will be recalculated.")
@click.option('-obni', '--oblique-not-italic', is_flag=True, default=False,
              help="By default, if a font has the oblique bit set, the italic bits will be set too. Use this option to"
                   " override the default behaviour (for example, when the family has both italic and oblique styles"
                   " and you need to keep oblique and italic styles separate). The italic bits will be cleared when the"
                   " oblique bit is set.")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t'
                   ' exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   ' default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   ' name). By default, files are overwritten.')
def recalc_names(
        input_path,
        config_file,
        linked_styles,
        exclude_namerecords,
        shorten_width,
        shorten_weight,
        shorten_slope,
        fix_cff,
        super_family,
        alt_uid,
        regular_italic,
        keep_regular,
        old_full_font_name,
        oblique_not_italic,
        output_dir,
        recalc_timestamp,
        overwrite
):
    """Recalculates namerecords according to the values stored in the data.csv file.
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
        click.secho("\n{} didn't exist and has been created".format(
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
    shorten_slope = [int(i) for i in shorten_slope]
    exclude_namerecords = [int(i) for i in exclude_namerecords]

    # We convert the linked_styles tuple to a list and then sort it.
    linked_styles = tuple(set(linked_styles))
    linked_styles = list(linked_styles)
    linked_styles.sort()

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            font_data = {}
            for row in data:
                if str(row['file_name']) == os.path.basename(f):
                    font_data = row

            font.recalcNames(
                font_data,
                linked_styles=linked_styles, namerecords_to_ignore=exclude_namerecords, shorten_weight=shorten_weight,
                shorten_width=shorten_width, shorten_slope=shorten_slope, alt_uid=alt_uid, fixCFF=fix_cff,
                isSuperFamily=super_family, regular_italic=regular_italic, keep_regular=keep_regular,
                old_full_font_name=old_full_font_name, oblique_not_italic=oblique_not_italic)

            output_file = makeOutputFileName(
                f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('{} saved'.format(output_file), fg='green')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')
            pass


cli = click.CommandCollection(sources=[editCFG, editCSV, initCFG, initCSV, recalcCSV, recalcNames], help="""
A set of tools to correctly compile the name table and set proper values for usWeightClass, usWidthClass, bold, italic
and oblique bits.

With the aide of a JSON configuration file, that can be edited according to user's needs, this tool will help create a
CSV file containing, for each file in a set of fonts, the following values:

\b
- is_bold
- is_italic
- is_oblique
- usWidthClass
- usWeightClass
- width (short and long literals, e.g.: 'Cn', 'Condensed')
- weight (short and long literals, e.g.: 'Lt', 'Light')
- slope (short and long literals, e.g.: 'It', 'Italic')
- family name

The values can be recalculated with the help of the automation provided by the tool (using the 'init-csv' and
'recalc-csv' commands) or manually edited using a suitable editor.

When the CSV file is correctly compiled, values contained in it can be written into the fonts using the 'recalc-names'
command. This command will not only correctly compile the name table, but will also change usWidthClass and
usWeightClass values, as well as the italic and oblique bits. The bold bits are another matter: they will be set only in
the bold styles of a family with linked styles and only if the user opts for using linked styles. In all other cases,
the bold bits will be cleared.

1) The JSON configuration file.

The configurationn file, normally named 'config.json' and stored in the work folder, contains the desired style names to
pair with each usWidthClass and usWeightClass values of the family, as well as the desired italic and oblique literals:

\b
{
    "italics": ["It", "Italic"],
\b
    "obliques": ["Obl", "Oblique"],
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

Unless you have previously created a configuration file and want to reuse it, you need to create a standard
configuration file and eventually customize it.

    ftcli assistant init-cfg INPUT_PATH

The above command will create a file named 'config.json' in the INPUT_PATH folder (or parent folder if INPUT_PATH is a
file).

Once created the configuration file, you may be in need to edit it according to your needs.

    ftcli assistant edit-cfg CONFIG_FILE
    
This command will open a command line editor that allows to add, delete and edit weights, widths, italic and oblique
style names and values.
    
Both steps can be skipped directly running the following command:

    ftcli assistant edit-csv INPUT_PATH
    
This command will create inside the INPUT_PATH folder, a file named 'config.json', a file named 'data.csv' and will open
a command line editor that allows to edit both them.

Values contained in the configuration file will be used to fill the data.csv file in the next steps.

2) The CSV data file.

The final data.csv file will contain the desired style names, family name, italic and oblique bits, usWidthClass and
usWeightClass values. Once properly filled, the values contained in this file will be written to the fonts.

It contains 13 columns:

file_name, family_name, is_bold, is_italic, is_oblique, uswidthclass, wdt, width, usweightclass, wgt, weight, slp,
slope.

The 'is_bold' column is present only for completeness, but it's values will be ignored. A font will be set as bold only
and only if, during the names recalculation, the user will choose to use linked styles (-ls / --linked styles option).

The 'wdt' and 'width' columns contain the short and long literals for the width style names (for example: Cn;
Condensed).

The 'wgt' and 'weight' columns contain the short and long literals for the weight style names (for example: Lt, Light).

The 'slp' and 'slope' columns contain the short and long literals for the slope style names (for example: It, Italic).

The user will choose the namerecords where to write long or short literals.

The 'data.csv' file can be created using the following command:

    ftcli assistant init-csv INPUT_PATH

At this point, the CSV file will contain a representation of the actual state of the fonts (the family_name column will
contain values of nameID 16, or nameID 1 if 16 is not present). It can be edited manually, using the 'ftcli assistant
edit-csv' command and also automatically recalculated using the 'ftcli assistant recalc-csv' command.

The 'ftcli assistant recalc-csv' command will recalculate style names, italic bits, width and weight style names
according to the values contained in the JSON configuration file.

When the 'data.csv' file contains the desired values, these values can be applied to fonts running the 'ftcli assistant
recalc-names' command (see 'ftcli assistant recalc-names --help' for more information).
    """)

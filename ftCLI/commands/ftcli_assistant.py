import os
from copy import copy, deepcopy

import click
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.assistant.fonts_data import FontsDataFile
from ftCLI.Lib.assistant.styles_mapping import StylesMappingFile
from ftCLI.Lib.cui.CUI import AssistantUI
from ftCLI.Lib.utils.cli_tools import (
    get_style_mapping_file_path,
    get_fonts_data_file_path,
    check_output_dir,
    check_input_path,
)
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    file_overwrite_prompt,
    generic_error_message,
    file_saved_message,
    file_not_changed_message,
    generic_warning_message,
    file_not_selected_message,
    add_path_argument,
)


@click.group()
def styles_mapping_editor():
    pass


@styles_mapping_editor.command()
@add_file_or_path_argument()
def edit_styles(input_path):
    editor = AssistantUI(input_path).styles_mapping_editor()
    editor.run()


@click.group()
def init_fonts_data_csv():
    pass


@init_fonts_data_csv.command()
@add_file_or_path_argument()
@click.option(
    "-s",
    "--styles-mapping-file",
    type=click.Path(exists=True, resolve_path=True, dir_okay=False),
    help="""
              Use a custom styles mapping file instead of the default styles_mapping.json file located in the
              ftCLI_files folder.""",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="""
              Suppress the overwrite confirmation message if the fonts_data.csv and/or styles_mapping.json files already
              exist in the ftCLI_files folder.""",
)
def init_data(input_path, styles_mapping_file=None, quiet=False):
    """
    Creates the CSV database file `fonts_data.csv` in the `ftCLI_files` subdirectory.

    Example 1:

        ftCLI assistant init-data "C:\\Fonts\\"

    Example 2:

        ftCLI assistant init-data "C:\\Fonts\\font.otf"

    Both commands will create the `fonts_data.csv` file in the C:\\Fonts\\ftCLI_files\\) (and the styles_mapping.json
    file in the same subdirectory, if it doesn't exist).

    `font_data.csv` file contains:

    - the file paths;

    - the usWidthClass, usWeightClass, bold and italic bits values of all font files found in INPUT_PATH;

    - tries to guess the family name reading the name table. It also contains weight and widths literals, retrieved
    parsing the config.json file.

    It can be edited manually or using the 'ftCLI assistant ui INPUT_PATH' command.
    """

    _ = check_input_path(input_path, allow_variable=False)

    if not styles_mapping_file:
        styles_mapping_file = get_style_mapping_file_path(input_path)

    style_mapping_file = StylesMappingFile(styles_mapping_file)

    if not os.path.exists(styles_mapping_file):
        style_mapping_file.reset_defaults()

    csv_file = get_fonts_data_file_path(input_path)

    if os.path.exists(csv_file) and not quiet:
        overwrite = file_overwrite_prompt(csv_file)
        if not overwrite:
            file_not_changed_message(csv_file)
            return

    try:
        FontsDataFile(fonts_data_file=csv_file).reset_data()
        file_saved_message(csv_file)
    except Exception as e:
        generic_error_message(e)


@click.group()
def recalc_fonts_data():
    pass


@recalc_fonts_data.command()
@add_file_or_path_argument()
@click.option(
    "-s",
    "--input-string",
    type=click.Choice(choices=["0", "1", "2", "3", "4", "5"]),
    default="0",
    help="""
              The string to be used to recalculate data. Default is 0 (file name).

              \b
              0: File Name
              1: PostScript Name
              2: Family Name + SubFamily Name
              3: Full Font Name
              4: CFF fontNames
              5: CFF FullName
              """,
)
@click.option(
    "-m",
    "--styles-mapping-file",
    type=click.Path(exists=True, resolve_path=True),
    help="""Use a custom styles mapping file instead of the default styles_mapping.json""",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="""
              Suppress the confirmation message if the fonts_data.csv already exists in the ftCLI_files folder.
              """,
)
def recalc_data(input_path, input_string, quiet=False):
    _ = check_input_path(input_path, allow_ttf=False, allow_variable=False)

    styles_mapping_file = get_style_mapping_file_path(input_path)

    if not os.path.exists(styles_mapping_file):
        StylesMappingFile(styles_mapping_file).reset_defaults()

    fonts_data_file = get_fonts_data_file_path(input_path)
    if not os.path.exists(fonts_data_file):
        FontsDataFile(fonts_data_file).reset_data(styles_mapping_file=styles_mapping_file)

    if os.path.exists(fonts_data_file) and not quiet:
        confirmation = click.confirm(f"{fonts_data_file} already exists. Do you want to overwrite it?")
        if not confirmation:
            return

    FontsDataFile(fonts_data_file).recalc_data(source_type=input_string, styles_mapping_file=styles_mapping_file)


@click.group()
def write_data_to_fonts():
    pass


@write_data_to_fonts.command()
@add_path_argument()
@click.option(
    "--width-elidable",
    default="Normal",
    show_default=True,
    help="""
              The width word to elide when building the namerecords.
              """,
)
@click.option(
    "--weight-elidable",
    default="Regular",
    show_default=True,
    help="""
              The weight word to elide when building the namerecords.
              """,
)
@click.option(
    "-ls",
    "--linked-styles",
    type=(click.IntRange(1, 1000), click.IntRange(1, 1000)),
    help="""
              Use this option to activate linked styles. If this option is active, linked styles must be specified.
              For example: -ls 400 700, or -ls 300 600.
              """,
)
@click.option(
    "-x",
    "--exclude-namerecords",
    type=click.Choice(choices=["1", "2", "3", "4", "5", "6", "16", "17", "18"]),
    multiple=True,
    help="""
              Name IDs to skip. The specified name IDs won't be recalculated. This option can be repeated (for example:
              -x 3 -x 5 -x 6...).
              """,
)
@click.option(
    "-swdt",
    "--shorten-width",
    type=click.Choice(choices=["1", "4", "6", "16", "17"]),
    multiple=True,
    help="""
              Name IDs where to use the short word for width style name (for example, 'Cn' instead of 'Condensed'). This
              option can be repeated (for example: -swdt 1 -swdt 5, -swdt 16...).
              """,
)
@click.option(
    "-swgt",
    "--shorten-weight",
    type=click.Choice(choices=["1", "4", "6", "17"]),
    multiple=True,
    help="""
              Name IDs where to use the short word for weight style name (for example, 'Md' instead of 'Medium'). This
              option can be repeated (for example: -swgt 1 -swgt 5 -swgt 6...).
              """,
)
@click.option(
    "-kwdt",
    "--keep-width-elidable",
    is_flag=True,
    help="""
              Doesn't remove the width elidable words (by default, "Nor" and "Normal").
              """,
)
@click.option(
    "-kwgt",
    "--keep-weight-elidable",
    is_flag=True,
    help="""
              Doesn't remove the weight elidable words (by default, "Rg" and "Regular").
              """,
)
@click.option(
    "-sslp",
    "--shorten-slope",
    type=click.Choice(choices=["4", "6", "16", "17"]),
    multiple=True,
    help="""
              Name IDs where to use the short word for slope style name (for example, 'It' instead of 'Italic'). This
              option can be repeated (for example: -sslp 3 -sslp 5 -sslp 6...).
              """,
)
@click.option(
    "-sf",
    "--super-family",
    is_flag=True,
    help="""
              Superfamily mode. This option affects name IDs 3, 6, 16 and 17 in case of families with widths different
              than 'Normal'. If this option is active, name ID 6 will be 'FamilyName-WidthWeightSlope' instead of
              'FamilyNameWidth-WeightSlope'. Mac and OT family/subfamily names will be FamilyName /  Width Weight Slope'
              instead of 'Family Name Width / Weight Slope'.
              """,
)
@click.option(
    "-aui",
    "--alt-uid",
    is_flag=True,
    help="""
              Use alternate unique identifier. By default, nameID 3 (Unique identifier) is calculated according to the
              following scheme: 'Version;Vendor code;PostscriptName'. The alternate unique identifier is calculated
              according to the following scheme: 'Manufacturer: Full Font Name: Creation Year'.
              """,
)
@click.option(
    "-obni",
    "--oblique-not-italic",
    is_flag=True,
    help="""
              By default, if a font has the oblique bit set, the italic bits will be set too. Use this option to
              override the default behaviour (for example, when the family has both italic and oblique styles and you
              need to keep oblique and italic styles separate). The italic bits will be cleared when the oblique bit is
              set.
              """,
)
@click.option(
    "--no-auto-shorten",
    "auto_shorten",
    is_flag=True,
    default=True,
    help="""
              When name id 1, 4 or 6 are longer than maximum allowed (27 characters for nameID 1, 31 for nameID 4 and 29
              for nameID 6), the script tries to auto shorten those names replacing long words with short words. Use
              this option to prevent the script from auto shortening names.
              """,
)
@click.option(
    "-cff",
    is_flag=True,
    help="""
              If this option is active, fontNames, FullName, FamilyName and Weight values in the 'CFF' table will be
              recalculated.
              """,
)
@add_common_options()
def commit(
    input_path,
    width_elidable,
    weight_elidable,
    linked_styles=None,
    exclude_namerecords=None,
    shorten_width=None,
    shorten_weight=None,
    keep_width_elidable=False,
    keep_weight_elidable=False,
    shorten_slope=None,
    super_family=False,
    alt_uid=False,
    oblique_not_italic=False,
    auto_shorten=True,
    cff=False,
    outputDir=None,
    recalcTimestamp=False,
    overWrite=True,
):
    """
    Writes data from CSV to fonts.
    """

    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    if linked_styles:
        linked_styles = sorted(linked_styles)
    if exclude_namerecords:
        exclude_namerecords = sorted(set(int(i) for i in exclude_namerecords))
    if shorten_width:
        shorten_width = sorted(set(int(i) for i in shorten_width))
    if shorten_weight:
        shorten_weight = sorted(set(int(i) for i in shorten_weight))
    if shorten_slope:
        shorten_slope = sorted(set(int(i) for i in shorten_slope))

    csv_file = get_fonts_data_file_path(input_path)
    try:
        fonts_data_file = FontsDataFile(csv_file)
        data = fonts_data_file.get_data()
    except Exception as e:
        generic_error_message(e)
        return

    for row in data:
        file = row["file_name"]

        file_exists = os.path.exists(file)
        if not file_exists:
            generic_warning_message(f"{file} {click.style('file does not exist', fg='yellow')}")
            continue

        file_is_selected = bool(int(row["selected"]))
        if not file_is_selected:
            file_not_selected_message(file)
            continue

        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            name_table_copy = deepcopy(font.name_table)
            os_2_table_copy = copy(font.os_2_table)
            head_table_copy = copy(font.head_table)
            if not font.is_cff:
                cff_table_copy = None
            else:
                cff_table_copy = deepcopy(font["CFF "])

            fonts_data_file.write_data_to_font(
                font=font,
                row=row,
                width_elidable=width_elidable,
                weight_elidable=weight_elidable,
                keep_width_elidable=keep_width_elidable,
                keep_weight_elidable=keep_weight_elidable,
                linked_styles=linked_styles,
                exclude_namerecords=exclude_namerecords,
                shorten_width=shorten_width,
                shorten_weight=shorten_weight,
                shorten_slope=shorten_slope,
                super_family=super_family,
                auto_shorten=auto_shorten,
                alt_uid=alt_uid,
                oblique_not_italic=oblique_not_italic,
                cff=cff,
            )

            font_has_changed = False

            if font.os_2_table != os_2_table_copy:
                font_has_changed = True
            if font.head_table != head_table_copy:
                font_has_changed = True
            if font.name_table.compile(font) != name_table_copy.compile(font):
                font_has_changed = True
            if cff_table_copy:
                if cff_table_copy.compile(font) != font["CFF "].compile(font):
                    font_has_changed = True

            if font_has_changed:
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def init_styles_mapping_json():
    pass


@init_styles_mapping_json.command()
@add_file_or_path_argument()
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Suppress the overwrite confirmation message if the config.json file already exists.",
)
def init_config(input_path, quiet):
    """
    Creates the `styles_mapping.json` containing the default values in the `ftCLI_files` folder.

    Default values are the following:

    \b
    +------------------------------------------+
    | WEIGHTS                                  |
    +------------------------------------------+
    | 250 : Th, Thin                           |
    | 275 : XLt, ExtraLight                    |
    | 300 : Lt, Light                          |
    | 350 : Bk, Book                           |
    | 400 : Rg, Regular                        |
    | 500 : Md, Medium                         |
    | 600 : SBd, SemiBold                      |
    | 700 : Bd, Bold                           |
    | 800 : XBd, ExtraBold                     |
    | 850 : Hvy, Heavy                         |
    | 900 : Blk, Black                         |
    | 950 : Ult, Ultra                         |
    +------------------------------------------+
    | WIDTHS                                   |
    +------------------------------------------+
    | 1 : Cm, Compressed                       |
    | 2 : XCn, ExtraCondensed                  |
    | 3 : Cn, Condensed                        |
    | 4 : Nr, Narrow                           |
    | 5 : Nor, Normal                          |
    | 6 : Wd, Wide                             |
    | 7 : Ext, Extended                        |
    | 8 : XExt, ExtraExtended                  |
    | 9 : Exp, Expanded                        |
    +------------------------------------------+
    | ITALICS                                  |
    +------------------------------------------+
    | Short word : It                          |
    | Long word  : Italic                      |
    +------------------------------------------+
    | OBLIQUES                                 |
    +------------------------------------------+
    | Short word : Obl                         |
    | Long word  : Oblique                     |
    +------------------------------------------+

    These values are used by the scripts involving the `font_data.csv` file to fill the CSV rows.
    """

    styles_mapping_file_path = get_style_mapping_file_path(input_path)

    if os.path.exists(styles_mapping_file_path) and not (quiet is True):
        overwrite = file_overwrite_prompt(styles_mapping_file_path)
        if overwrite is not True:
            file_not_changed_message(styles_mapping_file_path)
            return

    try:
        style_mapping_file = StylesMappingFile(styles_mapping_file_path)
        style_mapping_file.reset_defaults()
        file_saved_message(style_mapping_file.file)
    except Exception as e:
        generic_error_message(e)


@click.group()
def assistant_ui():
    pass


@assistant_ui.command()
@add_file_or_path_argument()
def ui(input_path):
    """
    Opens the character user interface to edit the styles_mapping.json and fonts_data.csv files.
    """

    styles_mapping_file = get_style_mapping_file_path(input_path)
    if not os.path.exists(styles_mapping_file):
        StylesMappingFile(styles_mapping_file).reset_defaults()

    fonts_data_file = get_fonts_data_file_path(input_path)
    if not os.path.exists(fonts_data_file):
        FontsDataFile(fonts_data_file).reset_data()

    AssistantUI(input_path).run()


cli = click.CommandCollection(
    sources=[
        init_fonts_data_csv,
        write_data_to_fonts,
        init_styles_mapping_json,
        assistant_ui,
    ],
    help="""
    Helps to correctly fill name table, as well as other values as usWeightClass, usWidthClass, bold, italic and oblique
    bits.
    """,
)

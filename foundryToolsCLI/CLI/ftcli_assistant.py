import typing as t
from copy import copy, deepcopy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.assistant.UI import AssistantUI
from foundryToolsCLI.Lib.assistant.fonts_data import FontsData
from foundryToolsCLI.Lib.assistant.styles_mapping import StylesMapping
from foundryToolsCLI.Lib.utils.cli_tools import (
    get_style_mapping_path,
    get_fonts_data_path,
)
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    file_overwrite_prompt,
    linked_styles_callback,
    choice_to_int_callback,
)
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.timer import Timer

assistant = click.Group("subcommands")


@assistant.command()
@add_file_or_path_argument()
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="""
    Suppress the overwrite confirmation message if the fonts_data.csv and/or styles_mapping.json
    files already exist in the ftCLI_files folder.""",
)
def init(input_path: Path, quiet: bool = False):
    """
    Creates the ``styles_mapping.json`` and the ``fonts_data.csv`` files in the ``ftCLI_files``
    directory. If one or both files already exist, user will be prompted for overwrite.

    Both files can be edited manually or using the ``ftcli assistant ui`` command.
    """

    try:
        styles_mapping_file = get_style_mapping_path(input_path)
        styles_mapping = StylesMapping(styles_mapping_file)
        if Path.exists(styles_mapping_file) and quiet is False:
            styles_mapping_overwrite = file_overwrite_prompt(styles_mapping_file)
        else:
            styles_mapping_overwrite = True

        if styles_mapping_overwrite is True:
            styles_mapping.reset_defaults()
            logger.success(Logs.file_saved, file=styles_mapping_file)
        else:
            logger.skip(Logs.file_not_changed, file=styles_mapping_file)

        fonts_data_file = get_fonts_data_path(input_path)
        fonts_data = FontsData(fonts_data_file)
        if Path.exists(fonts_data_file) and not quiet:
            fonts_data_overwrite = file_overwrite_prompt(fonts_data_file)
        else:
            fonts_data_overwrite = True
        if fonts_data_overwrite is True:
            fonts_data.reset_data(styles_mapping=styles_mapping)
            logger.success(Logs.file_saved, file=fonts_data_file)
        else:
            logger.skip(Logs.file_not_changed, file=fonts_data_file)
    except Exception as e:
        logger.exception(e)


@assistant.command()
@add_file_or_path_argument(file_okay=False)
@click.option(
    "--width-elidable",
    default="Normal",
    show_default=True,
    help="""The width word to elide when building the namerecords.""",
)
@click.option(
    "--weight-elidable",
    default="Regular",
    show_default=True,
    help="""The weight word to elide when building the namerecords.""",
)
@click.option(
    "-ls",
    "--linked-styles",
    type=(click.IntRange(1, 1000), click.IntRange(1, 1000)),
    callback=linked_styles_callback,
    help="""Use this option to activate linked styles. If this option is active, linked styles must
    be specified. For example: -ls 400 700, or -ls 300 600.
    """,
)
@click.option(
    "-x",
    "--exclude-namerecords",
    type=click.Choice(choices=["1", "2", "3", "4", "5", "6", "16", "17", "18"]),
    multiple=True,
    callback=choice_to_int_callback,
    help="""
    Name IDs to skip. The specified name IDs won't be recalculated. This option can be repeated
    (for example: -x 3 -x 5 -x 6...).
    """,
)
@click.option(
    "-swdt",
    "--shorten-width",
    type=click.Choice(choices=["1", "4", "6", "16", "17"]),
    multiple=True,
    callback=choice_to_int_callback,
    help="""
    Name IDs where to use the short word for width style name (for example, 'Cn' instead of
    'Condensed'). This option can be repeated (for example: -swdt 1 -swdt 5, -swdt 16...).
    """,
)
@click.option(
    "-swgt",
    "--shorten-weight",
    type=click.Choice(choices=["1", "4", "6", "17"]),
    multiple=True,
    callback=choice_to_int_callback,
    help="""
    Name IDs where to use the short word for weight style name (for example, 'Md' instead of
    'Medium'). This option can be repeated (for example: -swgt 1 -swgt 5 -swgt 6...).
    """,
)
@click.option(
    "-sslp",
    "--shorten-slope",
    type=click.Choice(choices=["4", "6", "16", "17"]),
    multiple=True,
    callback=choice_to_int_callback,
    help="""
    Name IDs where to use the short word for slope style name (for example, 'It' instead of
    'Italic'). This option can be repeated (for example: -sslp 3 -sslp 5 -sslp 6...).
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
    "-sf",
    "--super-family",
    is_flag=True,
    help="""
    Superfamily mode. This option affects name IDs 3, 6, 16 and 17 in case of families with widths
    different than 'Normal'. If this option is active, name ID 6 will be
    'FamilyName-WidthWeightSlope' instead of 'FamilyNameWidth-WeightSlope'. Mac and OT
    family/subfamily names will be FamilyName /  Width Weight Slope' instead of 'Family Name Width /
    Weight Slope'.
    """,
)
@click.option(
    "-aui",
    "--alt-uid",
    is_flag=True,
    help="""
    Use alternate unique identifier. By default, nameID 3 (Unique identifier) is calculated
    according to the following scheme: 'Version;Vendor code;PostscriptName'. The alternate unique
    identifier is calculated according to the following scheme: 'Manufacturer: Full Font Name:
    Creation Year'.
    """,
)
@click.option(
    "-obni",
    "--oblique-not-italic",
    is_flag=True,
    help="""
    By default, if a font has the oblique bit set, the italic bits will be set too. Use this option
    to override the default behaviour (for example, when the family has both italic and oblique
    styles and you need to keep oblique and italic styles separate). The italic bits will be cleared
    when the oblique bit is set.
    """,
)
@click.option(
    "--no-auto-shorten",
    "auto_shorten",
    is_flag=True,
    default=True,
    help="""
    When name id 1, 4 or 6 are longer than maximum allowed (27 characters for nameID 1, 31 for
    nameID 4 and 29 for nameID 6), the script tries to auto shorten those names replacing long words
    with short words. Use this option to prevent the script from auto shortening names.
    """,
)
@click.option(
    "-cff",
    is_flag=True,
    help="""
    If this option is active, fontNames, FullName, FamilyName and Weight values in the 'CFF' table
    will be recalculated.
    """,
)
@add_common_options()
@Timer(logger=logger.info)
def commit(
        input_path: Path,
        linked_styles: t.Optional[t.Tuple[int, int]] = None,
        exclude_namerecords: t.Union[t.Tuple[int], t.Tuple[()]] = (),
        shorten_width: t.Union[t.Tuple[int], t.Tuple[()]] = (),
        shorten_weight: t.Union[t.Tuple[int], t.Tuple[()]] = (),
        shorten_slope: t.Union[t.Tuple[int], t.Tuple[()]] = (),
        width_elidable: str = "Normal",
        weight_elidable: str = "Regular",
        keep_width_elidable: bool = False,
        keep_weight_elidable: bool = False,
        super_family: bool = False,
        alt_uid: bool = False,
        oblique_not_italic: bool = False,
        auto_shorten: bool = True,
        cff: bool = False,
        output_dir: t.Optional[Path] = None,
        recalc_timestamp: bool = False,
        overwrite: bool = True,
):
    """
    Writes data from CSV to fonts.
    """

    if output_dir is not None:
        try:
            output_dir.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            logger.exception(e)

    try:
        fonts_data = FontsData(get_fonts_data_path(input_path))
        data = fonts_data.get_data()
    except Exception as e:
        logger.exception(e)
        return

    for row in data:
        file = Path(row["file_name"])
        if not Path.exists(file):
            logger.warning(Logs.file_not_exists, file=file)
            continue

        file_is_selected = bool(int(row["selected"]))
        if not file_is_selected:
            logger.warning(Logs.file_not_selected, file=file)
            continue

        try:
            font = Font(file, recalcTimestamp=recalc_timestamp)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            name_table = font["name"]
            name_table_copy = deepcopy(name_table)
            os2_table = font["OS/2"]
            os2_table_copy = copy(os2_table)
            head_table = font["head"]
            head_table_copy = copy(head_table)
            if not font.is_otf:
                cff_table_copy = None
            else:
                cff_table_copy = deepcopy(font["CFF "])

            fonts_data.write_data_to_font(
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

            if os2_table != os2_table_copy:
                font_has_changed = True
            if head_table != head_table_copy:
                font_has_changed = True
            if name_table.compile(font) != name_table_copy.compile(font):
                font_has_changed = True
            if cff_table_copy:
                if cff_table_copy.compile(font) != font["CFF "].compile(font):
                    font_has_changed = True

            if font_has_changed:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)


@assistant.command()
@add_file_or_path_argument()
def ui(input_path: Path):
    """
    Opens the character user interface to edit the styles_mapping.json and fonts_data.csv files.
    """

    styles_mapping_file = get_style_mapping_path(input_path)
    if not styles_mapping_file.exists():
        StylesMapping(styles_mapping_file).reset_defaults()

    fonts_data_file = get_fonts_data_path(input_path)
    if not fonts_data_file.exists():
        FontsData(fonts_data_file).reset_data()

    AssistantUI(input_path).run()


cli = click.CommandCollection(
    sources=[assistant],
    help="""
Helps the user to correctly compile 'name' table and to set the proper values for usWeightClass,
usWidthClass, bold, italic and oblique flags.

The first step consists in creating two files in a folder named ftCLI_files under the current
directory:

1) ``styles_mapping.json``: contains the default Style Names to pair with usWidthClass,
usWeightClass and Slope class (e.g.: 500: Md, Medium; 3: Cnd, Condensed; It, Italic; Obl, Oblique).

2) ``fonts_data.csv``: is a CSV file containing the following columns:

* 'file_name': path the font file\n
* 'family_name': family name (read from the font)\n
* 'is_bold': bold flag (read from the font: "1" if the bold flag is set, "0" it the bold flag is
clear)\n
* 'is_italic': italic flag (read from the font: "1" if the italic flag is set, "0" it the italic
flag is clear)\n
* 'is_oblique': oblique flag (read from the font: "1" if the oblique flag is set, "0" it the oblique
flag is clear)\n
* 'us_width_class': usWidthClass value (read from the font)\n
* 'wdt': short word for width style name (read from styles_mapping.json, if usWidthClass is
present)\n
* 'width': long word for width style name (read from styles_mapping.json, if usWidthClass is
present)\n
* 'us_weight_class': usWeightClass value (read from the font)\n
* 'wgt': short word for weight style name (read from styles_mapping.json, if usWeightClass is
present)\n
* 'weight': long word for weight style name (read from styles_mapping.json, if usWeightClass is
present)\n
* 'slp': short word for slope class (read from styles_mapping.json. None if the font is not italic
nor oblique)\n
* 'slope': long word for slope class (read from styles_mapping.json. None if the font is not italic
nor oblique)\n
* 'selected': "1" to select the file, "0" to deselect (it will not be processed by ftcli assistant
commit)\n

Files can be created with ``ftcli assistant init INPUT_PATH`` or ``ftcli assistant ui INPUT_PATH``.
The first command will create both files (if one or both already exist, user will be prompted for
overwrite). The second command will create the files (unless they already exist) and will open the
editor.

When the data in the 'fonts_data.csv' file are filled as desired by the user, fonts can be patched
running the ``ftcli assistant commit`` command.
""",
)

from typing import Optional

import os.path
from shutil import get_terminal_size

from fontTools.ttLib.tables._n_a_m_e import _MAC_LANGUAGES, _WINDOWS_LANGUAGES
from rich import box
from rich.console import Console
from rich.table import Table

from foundryToolsCLI.Lib import constants
from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.VFont import VariableFont
from foundryToolsCLI.Lib.tables.OS_2 import TableOS2
from foundryToolsCLI.Lib.tables.name import TableName
from foundryToolsCLI.Lib.utils.logger import logger
from foundryToolsCLI.Lib.utils.text_tools import wrap_string


def print_fonts_list(fonts: list[Font]) -> None:
    """
    Prints list of fonts in `input_path` with basic information: Family name, Style name, usWidthClass, usWeightClass,
    Bold value, Italic value, Oblique value
    """
    rows = []
    for font in fonts:
        try:
            font_info = font.get_font_info()
            row = dict(
                file_name=os.path.basename(font_info["file_name"]["value"]),
                family_name=font_info["family_name"]["value"],
                subfamily_name=font_info["subfamily_name"]["value"],
                us_width_class=str(font_info["us_width_class"]["value"]),
                us_weight_class=str(font_info["us_weight_class"]["value"]),
                is_regular=str(int(font.is_regular)),
                is_italic=str(int(font.is_italic)),
                is_oblique=str(int(font.is_oblique)),
                is_bold=str(int(font.is_bold)),
            )
            rows.append(row)
        except Exception as e:
            logger.exception(e)

    table = Table(box=box.HORIZONTALS)
    table.add_column("#", justify="right")
    table.add_column("File name")
    table.add_column("Family name")
    table.add_column("Style name")
    table.add_column("Width", justify="right")
    table.add_column("Weight", justify="right")
    table.add_column("Regular", justify="right")
    table.add_column("Italic", justify="right")
    table.add_column("Bold", justify="right")
    table.add_column("Oblique", justify="right")
    table.header_style = "bold cyan"

    for i, row in enumerate(rows, start=1):
        table.add_row(
            str(i),
            row["file_name"],
            row["family_name"],
            row["subfamily_name"],
            row["us_width_class"],
            row["us_weight_class"],
            row["is_regular"],
            row["is_italic"],
            row["is_bold"],
            row["is_oblique"],
        )

    console = Console()
    console.print(table, highlight=True)


def print_instances(variable_font: VariableFont):
    """
    Prints the named instances of a variable font

    :param variable_font: The VariableFont object
    :type variable_font: VariableFont
    """
    table = Table(
        title="\nftCLI - Variable Font Instances Viewer",
        title_style="bold green",
        header_style="bold cyan",
        caption=f"{variable_font.reader.file.name}",
    )
    instances = variable_font.get_instances()
    table.add_section()
    table.add_column("#")
    axes = variable_font.get_axes()
    for axis in axes:
        table.add_column(axis.axisTag)
    table.add_column("subfamilyNameID")
    table.add_column("postscriptNameID")

    for count, instance in enumerate(instances, start=1):
        subfamily_name = (
            f"{instance.subfamilyNameID}: "
            f"{variable_font['name'].getDebugName(instance.subfamilyNameID)}"
        )
        postscript_name = (
            f"{instance.postscriptNameID}: "
            f"{variable_font['name'].getDebugName(instance.postscriptNameID)}"
        )
        table.add_row(
            str(count),
            *[str(v) for k, v in instance.coordinates.items() if k in [a.axisTag for a in axes]],
            subfamily_name,
            postscript_name,
        )

    console = Console()
    console.print(table)


def print_font_info(font: Font):
    """
    Prints a table with the font's basic information, vertical metrics, font tables, and font features

    :param font: The Font object to print information about
    :type font: Font
    """

    terminal_width = min(90, get_terminal_size()[0] - 1)

    table = Table(
        title="\nftCLI - Font Info Viewer",
        title_style="bold green",
        caption=f"{font.reader.file.name}",
        show_header=False,
    )

    font_info = font.get_font_info()
    font_v_metrics = font.get_font_v_metrics()
    feature_tags = font.get_font_feature_tags()

    sub_table_1 = Table(box=None, show_header=False)
    for v in font_info.values():
        if v["label"] == "File name":
            v["value"] = os.path.basename(v["value"])
        sub_table_1.add_row(f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value'])}")

    sub_table_2 = Table(box=None, show_header=False)
    for v in font_v_metrics["os2_metrics"]:
        sub_table_2.add_row(
            f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}"
        )

    sub_table_3 = Table(box=None, show_header=False)
    for v in font_v_metrics["hhea_metrics"]:
        sub_table_3.add_row(
            f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}"
        )

    sub_table_4 = Table(box=None, show_header=False)
    for v in font_v_metrics["head_metrics"]:
        sub_table_4.add_row(
            f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}"
        )

    table.add_row("[bold green]BASIC INFORMATION")
    table.add_section()
    table.add_row(sub_table_1)
    table.add_section()
    table.add_row("[bold green]VERTICAL METRICS")
    table.add_section()
    table.add_row("[bold magenta]OS/2 table")
    table.add_row(sub_table_2)
    table.add_row("\n[bold magenta]hhea table")
    table.add_row(sub_table_3)
    table.add_row("\n[bold magenta]head table")
    table.add_row(sub_table_4)
    table.add_section()
    table.add_row(f"[bold green]FONT TABLES[reset] ({len(font)})")
    table.add_section()
    table.add_row(
        wrap_string(
            string=", ".join([t for t in font.keys()]),
            initial_indent=0,
            indent=0,
            width=terminal_width,
        )
    )
    if len(feature_tags) > 0:
        table.add_section()
        table.add_row(f"[bold green]FONT FEATURES[reset] ({len(feature_tags)})")
        table.add_section()
        table.add_row(
            wrap_string(
                string=", ".join([str(t) for t in feature_tags]),
                initial_indent=0,
                indent=0,
                width=terminal_width,
            )
        )

    console = Console()
    console.print(table)


def print_font_names(font: Font, max_lines: Optional[int] = None, minimal: bool = False):
    """
    Prints the names in the name table and in the CFF table if present

    :param font: The Font object to print the names from
    :type font: Font
    :param max_lines: The maximum number of lines to print for each NameRecord string. If the name string is longer than
        this, it will be truncated
    :param minimal: Prints only namerecords with nameID in 1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22, 25
    :type minimal: bool
    """
    terminal_width = min(90, get_terminal_size()[0] - 1)

    table = Table(
        title="\nftCLI - Name Table Viewer",
        show_header=False,
        title_style="bold green",
    )

    name_table: TableName() = font["name"]

    subtables = []
    for name in name_table.names:
        subtables.append((name.platformID, name.platEncID, name.langID))

    # Remove duplicates and sort subtables by platformID
    subtables = list(set(subtables))
    subtables = sorted(subtables, key=lambda tup: tup[0])

    for t in subtables:
        platform_id = t[0]
        plat_enc_id = t[1]
        language_id = t[2]

        platform_string = constants.PLATFORMS.get(platform_id)
        plat_enc_string = ""
        language_string = ""
        if platform_id == 1:
            plat_enc_string = constants.MAC_ENCODING_IDS.get(plat_enc_id)
            language_string = _MAC_LANGUAGES.get(language_id)
        if platform_id == 3:
            plat_enc_string = constants.WINDOWS_ENCODING_IDS.get(plat_enc_id)
            language_string = _WINDOWS_LANGUAGES.get(language_id)

        table.add_section()

        table.add_row(
            f"PlatformID: {platform_id} ({platform_string}), PlatEncID: {plat_enc_id} ({plat_enc_string}), "
            f"LangID: {language_id} ({language_string})",
            style="bold green",
        )

        table.add_section()

        names = name_table.filter_namerecords(
            platform_id=platform_id, plat_enc_id=plat_enc_id, lang_id=language_id
        )
        if minimal:
            names = [n for n in names if n.nameID in (1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22, 25)]

        for name in names:
            if name.nameID in constants.NAME_IDS.keys():
                name_id_description = constants.NAME_IDS.get(name.nameID)
            else:
                name_id_description = str(name.nameID)

            row_string = (
                f"[bold cyan]{str(name.nameID).rjust(5)}[reset] : {name_id_description.ljust(22)} : "
                f"{name.toUnicode()}"
            )

            row_string = wrap_string(
                string=row_string,
                initial_indent=0,
                indent=33,
                max_lines=max_lines,
                width=terminal_width,
            )

            table.add_row(row_string)
        table.add_section()

    if "CFF " in font.keys():
        cff_table = font["CFF "]
        table.add_section()
        table.add_row("CFF Names", style="bold green")
        table.add_section()

        cff_names_to_skip = [
            "UnderlinePosition",
            "UnderlineThickness",
            "FontMatrix",
            "FontBBox",
            "charset",
            "Encoding",
            "Private",
            "CharStrings",
            "isFixedPitch",
            "ItalicAngle",
        ]
        minimal_cff_names = ["version", "FullName", "FamilyName", "Weight"]

        cff_names = [
            {k: v}
            for k, v in cff_table.cff.topDictIndex[0].rawDict.items()
            if k not in cff_names_to_skip
        ]

        if minimal:
            cff_names = [
                {k: v}
                for k, v in cff_table.cff.topDictIndex[0].rawDict.items()
                if k in minimal_cff_names
            ]

        table.add_row(
            "[bold cyan]{0:<30}".format("fontNames") + "[reset] : " + str(cff_table.cff.fontNames)
        )
        for cff_name in cff_names:
            for k, v in cff_name.items():
                row_string = "[bold cyan]{0:<30}".format(k) + "[reset] : " + str(v)
                row_string = wrap_string(
                    string=row_string,
                    initial_indent=0,
                    indent=33,
                    max_lines=max_lines,
                    width=terminal_width,
                )
                table.add_row(row_string)

    console = Console()
    console.print(table)


def print_os2_table(font: Font):
    """
    Converts the OS/2 table to a dictionary, and then prints it out in a table

    :param font: The font object to print the OS/2 table from
    :type font: Font
    """
    os2_table: TableOS2 = font["OS/2"]

    table = Table(
        title="\nftCLI - OS/2 Table Viewer",
        show_header=False,
        title_style="bold green",
        caption=font.reader.file.name,
    )

    os2_dict = os2_table.to_dict()
    panose_dict = os2_table.panose_to_dict()

    for k, v in os2_dict.items():
        table.add_row(f"[bold cyan]{k.ljust(19)}[reset] : {v}")
        if k == "tableTag":
            table.add_section()
        if k == "panose":
            table.add_row()
            for key, value in panose_dict.items():
                table.add_row(f"  [bold cyan]{key.ljust(18)}[reset]: {value}")
            table.add_row()

    console = Console()
    console.print(table)

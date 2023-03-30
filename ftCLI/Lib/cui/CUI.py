import os.path
import sys
from shutil import get_terminal_size

import click
from fontTools.ttLib.tables._n_a_m_e import _MAC_LANGUAGES, _WINDOWS_LANGUAGES
from rich import box
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from ftCLI.Lib import constants
from ftCLI.Lib.Font import Font
from ftCLI.Lib.assistant.fonts_data import FontsDataFile
from ftCLI.Lib.assistant.styles_mapping import (
    StylesMappingFile,
    DEFAULT_WEIGHTS,
    DEFAULT_WIDTHS,
)
from ftCLI.Lib.utils.cli_tools import (
    get_style_mapping_file_path,
    get_fonts_data_file_path,
    get_fonts_list,
)
from ftCLI.Lib.utils.click_tools import generic_error_message, no_valid_fonts_message, OptionalParamType
from ftCLI.Lib.utils.misc import wrap_string


class AssistantUI(object):
    def __init__(self, input_path):
        self.input_path = input_path

        if len(self.files_list) == 0:
            no_valid_fonts_message(input_path)
            sys.exit()

        self.styles_mapping_file = StylesMappingFile(get_style_mapping_file_path(self.input_path))
        if not os.path.exists(self.styles_mapping_file.file):
            self.styles_mapping_file.reset_defaults()

        self.fonts_data_file = FontsDataFile(get_fonts_data_file_path(self.input_path))
        if not os.path.exists(self.fonts_data_file.file):
            self.fonts_data_file.reset_data(styles_mapping_file=self.styles_mapping_file.file)

        self.console = Console()

    def run(self):
        click.clear()
        self.console.set_window_title("ftCLI assistant UI")

        rows = get_fonts_list_rows(files=get_fonts_list(self.input_path))
        table = get_fonts_list_table(rows=rows)
        table.title = "ftCLI Assistant - Main"
        table.title_style = "bold green"
        table.header_style = "bold cyan"
        table.box = box.HORIZONTALS
        table.caption = self.input_path

        self.console.print(table)

        commands = dict(s="Styles Mapping Editor", d="Fonts Data Editor", x="Exit")
        command = self.__prompt_for_command(commands)

        if command == "s":
            self.styles_mapping_editor()
            self.run()
        if command == "d":
            self.fonts_data_editor()
            self.run()

    def styles_mapping_editor(self):
        click.clear()
        self.console.set_window_title("Styles Mapping Editor")
        table = self.__get_styles_mapping_table()
        commands = {
            "g": "Edit Weights",
            "t": "Edit Widths",
            "i": "Edit Italics",
            "o": "Edit Obliques",
            "r": "Reset defaults",
            "x": "Exit",
        }
        self.console.print(table)

        command = self.__prompt_for_command(commands)
        if command == "g":
            self.__widths_weights_editor(key="weights")
        if command == "t":
            self.__widths_weights_editor(key="widths")
        if command == "i":
            self.__set_slope(key="italics")
        if command == "o":
            self.__set_slope(key="obliques")
        if command == "r":
            if self.__prompt_for_confirmation(text="Reset default values?"):
                self.styles_mapping_file.reset_defaults()
        if command == "x":
            return

        self.styles_mapping_editor()

    def fonts_data_editor(self):
        fonts_data = self.fonts_data_file.get_data()

        commands = {
            "s": "Select files",
            "d": "Deselect files",
            "f": "Set Family Name",
            "i": "Set/Unset Italic",
            "o": "Set/Unset Oblique",
            "t": "Set Width",
            "g": "Set Weight",
            "l": "Set Slope",
            "r": "Reset data",
            "c": "Recalc data",
            "x": "Exit",
        }
        table = self.__get_fonts_data_table()

        click.clear()
        self.console.print(table)

        command = self.__prompt_for_command(commands)
        if command == "s":
            self.__select_deselect_files(action="select")
        if command == "d":
            self.__select_deselect_files(action="deselect")
        if command == "f":
            family_name = click.prompt("Family name")
            if self.__prompt_for_confirmation():
                for row in fonts_data:
                    if row["selected"] == "1":
                        row["family_name"] = family_name
                self.fonts_data_file.save(fonts_data)
        if command == "i":
            italic_value = click.prompt(
                f"Italic value {click.style('[0/1]', bold=True, fg='cyan')}",
                type=click.Choice(choices=("0", "1")),
                show_choices=False,
            )
            if self.__prompt_for_confirmation():
                for row in fonts_data:
                    if row["selected"] == "1":
                        row["is_italic"] = italic_value
                self.fonts_data_file.save(fonts_data)
        if command == "o":
            oblique_value = click.prompt(
                f"Oblique value {click.style('[0/1]', bold=True, fg='cyan')}",
                type=click.Choice(choices=("0", "1")),
                show_choices=False,
            )
            if self.__prompt_for_confirmation():
                for row in fonts_data:
                    if row["selected"] == "1":
                        row["is_oblique"] = oblique_value
                self.fonts_data_file.save(fonts_data)
        if command == "t":
            us_width_class = click.prompt(
                f"usWidthClass {click.style('[1-9]', bold=True, fg='cyan')} (Enter  to skip)",
                type=OptionalParamType(click.IntRange(1, 9)),
                default="",
                show_default=False,
            )
            wdt = click.prompt(
                "Short word (Enter to skip)",
                type=OptionalParamType(click.STRING),
                default="",
                show_default=False,
            )
            width = click.prompt(
                "Long word (Enter to skip)",
                type=OptionalParamType(click.STRING),
                default="",
                show_default=False,
            )

            if self.__prompt_for_confirmation():
                for row in fonts_data:
                    if row["selected"] == "1":
                        row["us_width_class"] = us_width_class if us_width_class else row["us_width_class"]
                        words = [
                            wdt if wdt else row["wdt"],
                            width if width else row["width"],
                        ]
                        words.sort(key=len)
                        row["wdt"] = words[0]
                        row["width"] = words[1]
                self.fonts_data_file.save(fonts_data)
        if command == "g":
            us_weight_class = click.prompt(
                f"usWeightClass {click.style('[1-1000]', bold=True, fg='cyan')} " f"(Enter to skip)",
                type=OptionalParamType(click.IntRange(1, 1000)),
                default="",
                show_default=False,
            )
            wgt = click.prompt(
                "Short word (Enter to skip)",
                type=OptionalParamType(click.STRING),
                default="",
                show_default=False,
            )
            weight = click.prompt(
                "Long word (Enter to skip)",
                type=OptionalParamType(click.STRING),
                default="",
                show_default=False,
            )

            if self.__prompt_for_confirmation():
                for row in fonts_data:
                    if row["selected"] == "1":
                        if us_weight_class:
                            row["us_weight_class"] = us_weight_class
                        words = [
                            wgt if wgt else row["wgt"],
                            weight if weight else row["weight"],
                        ]
                        words.sort(key=len)
                        row["wgt"] = words[0]
                        row["weight"] = words[1]
                self.fonts_data_file.save(fonts_data)
        if command == "l":
            slp = click.prompt(
                "Short word (Enter to skip)",
                type=OptionalParamType(click.STRING),
                default="",
                show_default=False,
            )
            slope = click.prompt(
                "Long word (Enter to skip)",
                type=OptionalParamType(click.STRING),
                default="",
                show_default=False,
            )
            if self.__prompt_for_confirmation():
                for row in fonts_data:
                    if row["selected"] == "1":
                        words = [
                            slp if slp else row["slp"],
                            slope if slope else row["slope"],
                        ]
                        words.sort(key=len)
                        row["slp"] = words[0]
                        row["slope"] = words[1]
                self.fonts_data_file.save(fonts_data)
        if command == "r":
            if self.__prompt_for_confirmation(text="Reset data?"):
                self.fonts_data_file.reset_data(styles_mapping_file=self.styles_mapping_file.file)
        if command == "c":
            click.echo("\nPlease, select the string to use to recalculate data")
            click.secho("[0]", bold=True, fg="cyan", nl=False)
            click.echo(" : File Name")
            click.secho("[1]", bold=True, fg="cyan", nl=False)
            click.echo(" : PostScript Name")
            click.secho("[2]", bold=True, fg="cyan", nl=False)
            click.echo(" : Family Name + SubFamily Name")
            click.secho("[3]", bold=True, fg="cyan", nl=False)
            click.echo(" : Full Font Name")
            click.secho("[4]", bold=True, fg="cyan", nl=False)
            click.echo(" : CFF fontNames")
            click.secho("[5]", bold=True, fg="cyan", nl=False)
            click.echo(" : CFF FullName")
            source_type = self.__prompt_for_int_range("Your selection", min_value=0, max_value=5, default=0)
            if self.__prompt_for_confirmation(text="Recalc data?"):
                self.fonts_data_file.recalc_data(
                    source_type=source_type,
                    styles_mapping_file=self.styles_mapping_file.file,
                )

        if command == "x":
            return

        self.fonts_data_editor()

    def __widths_weights_editor(self, key: str):
        if key == "weights":
            max_value = 1000
            defaults = DEFAULT_WEIGHTS
        elif key == "widths":
            max_value = 9
            defaults = DEFAULT_WIDTHS
        else:
            return

        data = self.styles_mapping_file.get_data()
        table = self.__get_widths_weights_table(key)

        commands = {
            "a": "Add/edit item",
            "d": "Delete item",
            "r": "Reset defaults",
            "x": "Exit",
        }

        click.clear()
        self.console.print(table)
        command = self.__prompt_for_command(commands)

        if command == "a":
            self.__add_width_weight(key=key, max_value=max_value)
        if command == "d":
            choices = [k for k in data[key].keys()]
            value = click.prompt(
                f"Value to delete {click.style('[' + ', '.join(choices) + ']', bold=True, fg='cyan')}",
                type=click.Choice(choices=choices),
                show_choices=False,
            )
            if self.__prompt_for_confirmation():
                del data[key][value]
                self.styles_mapping_file.save(data)
        if command == "r":
            if self.__prompt_for_confirmation(text="Reset default values?"):
                data[key] = defaults
                self.styles_mapping_file.save(data)
        if command == "x":
            return

        self.__widths_weights_editor(key)

    def __select_deselect_files(self, action):
        data = self.fonts_data_file.get_data()

        start = self.__prompt_for_int_range(text="From line", min_value=1, max_value=len(data), default=1)
        end = self.__prompt_for_int_range(text="To line", min_value=start, max_value=len(data), default=len(data))

        for i in range(start - 1, end):
            if action == "select":
                data[i]["selected"] = 1
            if action == "deselect":
                data[i]["selected"] = 0
        self.fonts_data_file.save(data)

    def __get_fonts_data_table(self) -> Table:
        data = self.fonts_data_file.get_data()

        table = Table(
            title="ftCLI Assistant - Fonts Data Editor",
            title_style="bold green",
            header_style="bold cyan",
            caption=self.fonts_data_file.file,
            box=box.HORIZONTALS,
        )

        table.add_column("#", justify="right")
        table.add_column("[+]")
        table.add_column("File name")
        table.add_column("Family name")
        table.add_column("B")
        table.add_column("I")
        table.add_column("O")
        table.add_column("Width")
        table.add_column("Weight")
        table.add_column("Slope")

        for count, row in enumerate(data, start=1):
            if row["selected"] == "1":
                selected_string = "[bold cyan][+]"
            else:
                selected_string = "[ ]"
            file_name = row["file_name"]
            family_name = row["family_name"]
            is_bold = row["is_bold"]
            is_italic = row["is_italic"]
            is_oblique = row["is_oblique"]
            width = f"{row['us_width_class']} : {row['wdt']}, {row['width']}"
            weight = f"{row['us_weight_class']} : {row['wgt']}, {row['weight']}"
            if (row["slp"], row["slope"]) == ("", ""):
                slope = ""
            else:
                slope = ", ".join([row["slp"], row["slope"]])

            table.add_row(
                str(count),
                selected_string,
                os.path.basename(file_name),
                family_name,
                is_bold,
                is_italic,
                is_oblique,
                width,
                weight,
                slope,
            )

        return table

    def __get_styles_mapping_table(self) -> Table:
        """
        Returns a Table object of the styles mapping
        """
        data = self.styles_mapping_file.get_data()

        table = Table(
            show_header=False,
            title="ftCLI Assistant - Styles Mapping Editor",
            title_style="bold green",
            caption=self.styles_mapping_file.file,
            box=box.HORIZONTALS,
        )

        table.add_row("Weight", "Short word", "Long word", style="bright_cyan", end_section=True)
        for k, v in data["weights"].items():
            table.add_row(k, v[0], v[1])
        table.add_section()
        table.add_row("Width", "Short word", "Long word", style="bright_cyan", end_section=True)
        for k, v in data["widths"].items():
            table.add_row(k, v[0], v[1])
        table.add_section()
        table.add_row("Slope", "Short word", "Long word", style="bright_cyan", end_section=True)
        table.add_row("Italic", data["italics"][0], data["italics"][1])
        table.add_row("Oblique", data["obliques"][0], data["obliques"][1])

        return table

    def __get_widths_weights_table(self, key) -> Table:
        data = self.styles_mapping_file.get_data()
        table = Table(
            show_header=False,
            title=f"ftCLI Assistant - {key.capitalize()} Editor",
            title_style="bold green",
            box=box.HORIZONTALS,
        )
        table.add_row(
            f"{key[0:-1]}".capitalize(),
            "Short word",
            "Long word",
            style="bold cyan",
            end_section=True,
        )
        for k, v in data[key].items():
            table.add_row(k, v[0], v[1])
        table.add_section()

        return table

    def __add_width_weight(self, key: str, max_value: int):
        data = self.styles_mapping_file.get_data()
        value = str(self.__prompt_for_int_range(text="Value", min_value=1, max_value=max_value))

        defaults = [None, None]
        if value in data[key].keys():
            defaults = data[key].get(value)
            new_value = str(
                self.__prompt_for_int_range(
                    text="New value",
                    min_value=1,
                    max_value=max_value,
                    default=int(value),
                )
            )
            del data[key][value]
            value = new_value

        short_word = click.prompt(
            f"Short word " f"{click.style(f'[{defaults[0]}]', bold=True, fg='cyan') if defaults[0] else ''}",
            default=defaults[0],
            show_default=False,
        )
        long_word = click.prompt(
            f"Long word  " f"{click.style(f'[{defaults[1]}]', bold=True, fg='cyan') if defaults[1] else ''}",
            default=defaults[1],
            show_default=False,
        )

        if self.__prompt_for_confirmation():
            # del data[key][value]
            data[key][value] = sorted([short_word, long_word], key=len)
            self.styles_mapping_file.save(data)

    def __set_slope(self, key: str):
        data = self.styles_mapping_file.get_data()

        short_word = click.prompt(
            f"Short word{click.style(f' [{data[key][0]}]', bold=True, fg='cyan')}",
            default=data[key][0],
            show_default=False,
        )
        long_word = click.prompt(
            f"Long word{click.style(f' [{data[key][1]}]', bold=True, fg='cyan')}",
            default=data[key][1],
            show_default=False,
        )

        data[key] = sorted([short_word, long_word], key=len)

        if self.__prompt_for_confirmation():
            self.styles_mapping_file.save(data)

    @staticmethod
    def __prompt_for_command(commands: dict) -> str:
        click.secho("\nAVAILABLE COMMANDS:\n", bold=True, fg="green")
        for k, v in commands.items():
            click.secho(f" {click.style(k, bold=True, fg='cyan')} : ", nl=False)
            click.secho(f"{v} ", nl=True)

        choices = [k for k in commands.keys()]
        # command = click.prompt(f"\nSelect command [{click.style(', '.join(choices), bold=True, fg='cyan')}]",
        command = click.prompt(
            "\nSelect command",
            type=click.Choice(choices=choices, case_sensitive=False),
            show_choices=False,
            show_default=False,
            err=True,
        )
        return command

    @staticmethod
    def __prompt_for_int_range(
        text: str,
        min_value: int,
        max_value: int,
        default: int = None,
        bold: bool = True,
        fg_color: str = "cyan",
    ) -> int:
        """
        > Prompt the user for an integer value within a specified range, and return the value as a string

        :param text: The text to display to the user
        :type text: str
        :param min_value: The minimum value that the user can enter
        :type min_value: int
        :param max_value: The maximum value that the user can enter
        :type max_value: int
        :param default: The default value to use if no input happens. If a default value is given, it is shown in square
            brackets in place of the min-max range
        :type default: int
        :param bold: bool = True, defaults to True
        :type bold: bool (optional)
        :param fg_color: The color of the highlighted text, defaults to cyan
        :type fg_color: str (optional)
        :return: An integer
        """
        highlighted_text = click.style(
            f"[{default}]" if default is not None else f"[{min_value}-{max_value}]",
            bold=bold,
            fg=fg_color,
        )
        message = f"{text} {highlighted_text}"
        value = click.prompt(
            message,
            type=click.IntRange(min_value, max_value),
            default=default,
            show_default=False,
        )
        return value

    @staticmethod
    def __prompt_for_confirmation(text="Save changes?") -> bool:
        """
        > Prompt the user for a yes/no confirmation, and return a boolean value

        :param text: The text to display to the user, defaults to Save changes? (optional)
        :return: A boolean value
        """
        return click.confirm(
            f"{text} {click.style('[Y/n]', bold=True, fg='cyan')}",
            default=True,
            show_default=False,
        )

    @property
    def files_list(self):
        return get_fonts_list(self.input_path)


def get_commands_tree(commands: dict) -> Tree:
    """
    Takes a dictionary of commands and returns a Tree object

    :param commands: the dictionary of commands
    :type commands: dict
    :return: A Tree object with the label "COMMANDS" and the style "green"
    """
    commands_tree = Tree(label="COMMANDS", style="green", guide_style="green")
    for k, v in commands.items():
        commands_tree.add(f"[bold green]{k}[reset] : [bold cyan]{v}")
    return commands_tree


def get_fonts_list_rows(files) -> list:
    rows = []
    for file in files:
        try:
            font = Font(file)
            row = dict(
                file_name=os.path.basename(font.file),
                family_name=font.name_table.getBestFamilyName(),
                subfamily_name=font.name_table.getBestSubFamilyName(),
                us_width_class=str(font.os_2_table.usWidthClass),
                us_weight_class=str(font.os_2_table.usWeightClass),
                is_bold=str(int(font.is_bold)),
                is_italic=str(int(font.is_italic)),
                is_oblique=str(int(font.is_oblique)),
            )
            rows.append(row)
        except Exception as e:
            generic_error_message(e)
    return rows


def get_fonts_list_table(rows: list) -> Table:
    table = Table(box=box.HORIZONTALS)

    table.add_column("#", justify="right")
    table.add_column("File name")
    table.add_column("Family name")
    table.add_column("Style name")
    table.add_column("Width", justify="right")
    table.add_column("Weight", justify="right")
    table.add_column("Bold", justify="right")
    table.add_column("Italic", justify="right")
    table.add_column("Oblique", justify="right")

    for i, row in enumerate(rows, start=1):
        table.add_row(
            str(i),
            row["file_name"],
            row["family_name"],
            row["subfamily_name"],
            row["us_width_class"],
            row["us_weight_class"],
            row["is_bold"],
            row["is_italic"],
            row["is_oblique"],
        )

    return table


def print_fonts_list(files: list):
    """
    Prints list of fonts in `input_path` with basic information: Family name, Style name, usWidthClass, usWeightClass,
    Bold value, Italic value, Oblique value
    """

    rows = get_fonts_list_rows(files)
    table = get_fonts_list_table(rows)
    table.header_style = "bold cyan"
    console = Console()
    console.print(table, highlight=True)


def print_font_info(font: Font):
    """
    Prints a table with the font's basic information, vertical metrics, font tables, and font features

    :param font: The Font object to print information about
    :type font: Font
    """

    terminal_width = min(90, get_terminal_size()[0] - 1)

    table = Table(
        title="ftCLI - Font Info Viewer",
        title_style="bold green",
        caption=f"{font.file}",
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
        sub_table_2.add_row(f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}")

    sub_table_3 = Table(box=None, show_header=False)
    for v in font_v_metrics["hhea_metrics"]:
        sub_table_3.add_row(f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}")

    sub_table_4 = Table(box=None, show_header=False)
    for v in font_v_metrics["head_metrics"]:
        sub_table_4.add_row(f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}")

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


def print_font_names(font: Font, max_lines=None, minimal=False):
    """
    Prints the names in the name table and in the CFF table if present

    :param font: The Font object to print the names from
    :type font: Font
    :param max_lines: The maximum number of lines to print for each namerecord string. If the name string is longer than
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

    subtables = []
    for name in font.name_table.names:
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

        names = font.name_table.filter_namerecords(
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

        cff_names = [{k: v} for k, v in cff_table.cff.topDictIndex[0].rawDict.items() if k not in cff_names_to_skip]

        if minimal:
            cff_names = [{k: v} for k, v in cff_table.cff.topDictIndex[0].rawDict.items() if k in minimal_cff_names]

        table.add_row("[bold cyan]{0:<30}".format("fontNames") + "[reset] : " + str(cff_table.cff.fontNames))
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

    table = Table(
        title="\nftCLI - OS/2 Table Viewer",
        show_header=False,
        title_style="bold green",
        caption=font.file,
    )

    os2_dict = font.os_2_table.to_dict()

    for k, v in os2_dict.items():
        table.add_row(f"[bold cyan]{k.ljust(20)}[reset] : {v}")
        if k == "tableTag":
            table.add_section()

    console = Console()
    console.print(table)

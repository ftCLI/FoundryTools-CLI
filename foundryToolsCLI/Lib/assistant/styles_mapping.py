import json
from pathlib import Path


class StylesMapping(object):
    def __init__(self, styles_mapping_file: Path):
        self.file = styles_mapping_file

    def get_data(self) -> dict:
        """
        Opens the styles mapping file and returns its data as a dictionary

        :return: A dictionary of the styles mapping file.
        """
        with open(self.file) as f:
            styles_mapping = json.load(f)
        return styles_mapping

    def save(self, data: dict) -> None:
        """
        Saves the styles mapping file

        :param data: The styles mapping dictionary to save
        :type data: dict
        """
        Path.mkdir(self.file.parent, exist_ok=True)
        with open(self.file, "w") as f:
            json.dump(data, f, sort_keys=True, indent=4)

    def reset_defaults(self) -> None:
        """
        Writes the default values to the styles mapping file
        """
        Path.mkdir(self.file.parent, exist_ok=True)
        with open(self.file, "w") as f:
            json.dump(
                dict(
                    weights=DEFAULT_WEIGHTS,
                    widths=DEFAULT_WIDTHS,
                    italics=DEFAULT_ITALICS,
                    obliques=DEFAULT_OBLIQUES,
                ),
                f,
                sort_keys=True,
                indent=4,
            )


DEFAULT_WEIGHTS = {
    250: ["Th", "Thin"],
    275: ["XLt", "ExtraLight"],
    300: ["Lt", "Light"],
    350: ["Bk", "Book"],
    400: ["Rg", "Regular"],
    500: ["Md", "Medium"],
    600: ["SBd", "SemiBold"],
    700: ["Bd", "Bold"],
    800: ["XBd", "ExtraBold"],
    850: ["Hvy", "Heavy"],
    900: ["Blk", "Black"],
    950: ["Ult", "Ultra"],
}

DEFAULT_WIDTHS = {
    1: ["Cm", "Compressed"],
    2: ["XCn", "ExtraCondensed"],
    3: ["Cn", "Condensed"],
    4: ["Nr", "Narrow"],
    5: ["Nor", "Normal"],
    6: ["Wd", "Wide"],
    7: ["Ext", "Extended"],
    8: ["XExt", "ExtraExtended"],
    9: ["Exp", "Expanded"],
}

DEFAULT_ITALICS = ["It", "Italic"]

DEFAULT_OBLIQUES = ["Obl", "Oblique"]

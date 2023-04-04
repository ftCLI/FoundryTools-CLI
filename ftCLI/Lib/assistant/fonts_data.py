import csv
import os.path

from fontTools.misc.timeTools import timestampToString

from ftCLI.Lib.Font import Font
from ftCLI.Lib.assistant.styles_mapping import StylesMappingFile
from ftCLI.Lib.constants import (
    MAX_FAMILY_NAME_LEN,
    MAX_FULL_NAME_LEN,
    MAX_POSTSCRIPT_NAME_LEN,
)
from ftCLI.Lib.utils.cli_tools import get_fonts_list, get_style_mapping_file_path
from ftCLI.Lib.utils.click_tools import (
    generic_error_message,
    generic_info_message,
    generic_warning_message,
)


class FontsDataFile(object):
    def __init__(self, fonts_data_file):
        self.file = fonts_data_file

    def get_data(self) -> list:
        with open(self.file, "r") as f:
            data = [row for row in csv.DictReader(f, delimiter=";")]
        return data

    def recalc_data(self, source_type: int, styles_mapping_file):
        styles_mapping_data = StylesMappingFile(styles_mapping_file).get_data()

        weights: dict = styles_mapping_data["weights"]
        widths: dict = styles_mapping_data["widths"]
        italics: list = styles_mapping_data["italics"]
        obliques: list = styles_mapping_data["obliques"]

        all_words_list = []

        weights_list = []
        for values in weights.values():
            for value in values:
                weights_list.append(value)
        all_words_list.extend(weights_list)

        widths_list = []
        for values in widths.values():
            for value in values:
                widths_list.append(value)
        all_words_list.extend(widths_list)

        all_words_list.extend(italics)

        all_words_list.extend(obliques)

        all_words_list.sort(key=len, reverse=True)

        data = self.get_data()
        for row in data:
            if row["selected"] == "0":
                continue
            try:
                file_name = row["file_name"]
                font = Font(file_name)
                if source_type in (4, 5):
                    if not font.is_cff:
                        source_type = 0
                full_name = self.__normalize_string(font.get_file_name(source=source_type))
                family_name = row["family_name"]
                style_name = full_name.replace(self.__normalize_string(family_name), "")

                weight_string = self.__match_string(
                    input_string=style_name,
                    remove_list=all_words_list,
                    keep_list=weights_list,
                )
                if weight_string in [self.__normalize_string(str(word)) for word in weights_list]:
                    us_weight_class = self.__get_key_from_value(weights, weight_string)
                    wgt, weight = weights.get(us_weight_class)
                else:
                    us_weight_class = self.__get_font_row(font, styles_mapping_data)["us_weight_class"]
                    wgt = self.__get_font_row(font, styles_mapping_data)["wgt"]
                    weight = self.__get_font_row(font, styles_mapping_data)["weight"]
                row["us_weight_class"], row["wgt"], row["weight"] = (
                    us_weight_class,
                    wgt,
                    weight,
                )

                width_string = self.__match_string(
                    input_string=style_name,
                    remove_list=all_words_list,
                    keep_list=widths_list,
                )
                if width_string in [self.__normalize_string(str(word)) for word in widths_list]:
                    us_width_class = self.__get_key_from_value(widths, width_string)
                    wdt, width = widths.get(us_width_class)
                else:
                    us_width_class = self.__get_font_row(font, styles_mapping_data)["us_width_class"]
                    wdt = self.__get_font_row(font, styles_mapping_data)["wdt"]
                    width = self.__get_font_row(font, styles_mapping_data)["width"]
                row["us_width_class"], row["wdt"], row["width"] = (
                    us_width_class,
                    wdt,
                    width,
                )

                italic_string = self.__match_string(
                    input_string=style_name,
                    remove_list=all_words_list,
                    keep_list=italics,
                )
                oblique_string = self.__match_string(
                    input_string=style_name,
                    remove_list=all_words_list,
                    keep_list=obliques,
                )
                slp = slope = None
                if italic_string in [self.__normalize_string(str(word)) for word in italics] or font.is_italic:
                    is_italic = "1"
                    slp, slope = italics
                else:
                    is_italic = "0"
                if oblique_string in [self.__normalize_string(str(word)) for word in obliques] or font.is_oblique:
                    is_oblique = "1"
                    slp, slope = obliques
                else:
                    is_oblique = "0"
                row["is_italic"], row["is_oblique"], row["slp"], row["slope"] = (
                    is_italic,
                    is_oblique,
                    slp,
                    slope,
                )

            except Exception as e:
                generic_error_message(e)

        self.save(data)

    def write_data_to_font(
        self,
        font: Font,
        row: dict,
        width_elidable: str = "Normal",
        weight_elidable: str = "Regular",
        keep_width_elidable=False,
        keep_weight_elidable=False,
        linked_styles=None,
        exclude_namerecords=None,
        shorten_width=None,
        shorten_weight=None,
        shorten_slope=None,
        super_family=False,
        alt_uid=False,
        oblique_not_italic=False,
        auto_shorten=True,
        cff=False,
    ):
        family_name = row["family_name"]
        is_italic = bool(int(row["is_italic"]))
        is_oblique = bool(int(row["is_oblique"]))
        us_width_class = int(row["us_width_class"])
        us_weight_class = int(row["us_weight_class"])
        wdt = str(row["wdt"])
        width = str(row["width"])
        wgt = str(row["wgt"])
        weight = str(row["weight"])
        slp = str(row["slp"])
        slope = str(row["slope"])

        # We clear the bold and italic bits as first. Only the italic and oblique bits values are read from the CSV
        # file. The bold bits will be set only if the -ls / --linked-styles option is active.
        font.set_regular()

        # If is_italic is True, italic bits are set.
        if is_italic:
            font.set_italic()

        # If is_oblique is True, the oblique bit is set, as well as the italic bits. In case we don't want to set also
        # the italic bits, this can be achieved setting oblique_not_italic to True passing the -obni /
        # --oblique-not-italic option.
        if is_oblique:
            font.set_oblique()
            if oblique_not_italic:
                is_italic = False
                font.unset_italic()
            else:
                is_italic = True
                font.set_italic()

        # Set usWeightClass and usWidthClass values according to the data stored in the CSV file.
        font.os_2_table.set_width_class(us_width_class)
        font.os_2_table.set_weight_class(us_weight_class)

        # Build OT family and subfamily name
        family_name_ot = f"{family_name} {width}"
        subfamily_name_ot = weight
        # Remove width elidable from family name
        if not keep_width_elidable:
            if width.lower() == width_elidable.lower():
                family_name_ot = family_name

        # If super_family is True, prepend the width literal to OT Subfamily Name.
        if super_family is True:
            family_name_ot = family_name
            subfamily_name_ot = f"{width} {weight}"
            # Remove the width elidable from subfamily name
            if not keep_width_elidable:
                if width.lower() == width_elidable.lower():
                    subfamily_name_ot = weight

        # Finally, append the slope string to subfamily name
        if len(slope) > 0:
            subfamily_name_ot = f"{subfamily_name_ot} {slope}"
            if not keep_weight_elidable:
                if weight.lower() == weight_elidable.lower():
                    subfamily_name_ot = subfamily_name_ot.replace(weight, "").replace("  ", " ").strip()

        # Remove the elidable weight, but only if it's not the only word left.
        if subfamily_name_ot.lower() != weight.lower():
            if not keep_weight_elidable:
                if weight.lower() == weight_elidable.lower():
                    subfamily_name_ot = subfamily_name_ot.replace(weight, "").replace("  ", " ").strip()

        # Build Windows family and subfamily names
        family_name_win = f"{family_name} {width} {weight}"
        if not keep_width_elidable:
            if width.lower() == width_elidable.lower():
                family_name_win = f"{family_name} {weight}"

        # When there are both italic and oblique styles in a family, the italic bits are cleared and the oblique bit
        # is set in the oblique style. Consequently, in case the font is oblique, the slope is added to family name.
        if len(slope) > 0 and is_italic is False:
            family_name_win = f"{family_name_win} {slope}"

        # In platformID 3, Subfamily name can be only Regular, Italic, Bold, Bold Italic.
        subfamily_name_win = "Regular"
        if is_italic or (is_oblique and not oblique_not_italic):
            subfamily_name_win = "Italic"

        if linked_styles:
            # Remove Weight from Family Name
            if us_weight_class in linked_styles:
                family_name_win = family_name_win.replace(weight, "").replace("  ", " ").strip()

            linked_styles.sort()
            if us_weight_class == linked_styles[1]:
                # The bold bit is set HERE AND ONLY HERE.
                font.set_bold()
                subfamily_name_win = "Bold"
                if is_italic is True:
                    subfamily_name_win = "Bold Italic"

        # Apply the explicitly passed shortenings
        if 1 in shorten_width:
            family_name_win = family_name_win.replace(width, wdt)
        if 1 in shorten_weight:
            family_name_win = family_name_win.replace(weight, wgt)
        # Slope shouldn't be here, so it is not shortened

        # Check if Windows subfamily name is longer than 27 chars and try ro shorten it.
        if len(family_name_win) > MAX_FAMILY_NAME_LEN and auto_shorten:
            family_name_win = self.__auto_shorten_name(
                string=family_name_win,
                # Slope shouldn't be here, so only width and weight are shortened
                find_replace=[(weight, wgt), (width, wdt)],
                max_len=MAX_FAMILY_NAME_LEN,
            )
            generic_info_message(f"Windows Family Name shortened: {family_name_win}.")

        # Build PostScript Name
        postscript_name = str(font.name_table.getDebugName(6))
        if 6 not in exclude_namerecords:
            postscript_family_name = family_name_ot
            postscript_subfamily_name = subfamily_name_ot

            # Apply the explicitly passed shortenings
            if 6 in shorten_width:
                if not super_family:
                    # Width is in the family name string when super_family is False
                    postscript_family_name = postscript_family_name.replace(width, wdt)
                else:
                    # Width is in the subfamily name string when super_family is True
                    postscript_subfamily_name = postscript_subfamily_name.replace(width, wdt)
            if 6 in shorten_weight:
                postscript_subfamily_name = postscript_subfamily_name.replace(weight, wgt)
            if 6 in shorten_slope:
                postscript_subfamily_name = postscript_subfamily_name.replace(slope, slp)

            # Remove dots, dashes, commas etc. from PostScript family and subfamily name
            for char_to_remove in [".", ",", ":", ";", "-", " "]:
                postscript_family_name = postscript_family_name.replace(char_to_remove, "")
                postscript_subfamily_name = postscript_subfamily_name.replace(char_to_remove, "")

            # Remove illegal characters. The following characters are reserved in PostScript language.
            for illegal_char in ("[", "]", "{", "}", "<", ">", "/", "%"):
                postscript_family_name = postscript_family_name.replace(illegal_char, "")
                postscript_subfamily_name = postscript_subfamily_name.replace(illegal_char, "")

            # Finally, build the PostScript Name
            postscript_name = f"{postscript_family_name}-{postscript_subfamily_name}"

            # Check that the PostScript Name is not longer than 29 chars and try to shorten it.
            if len(postscript_name) > MAX_POSTSCRIPT_NAME_LEN and auto_shorten:
                postscript_name = self.__auto_shorten_name(
                    string=postscript_name,
                    find_replace=[
                        (slope.replace(" ", ""), slp.replace(" ", "")),
                        (weight.replace(" ", ""), wgt.replace(" ", "")),
                        (width.replace(" ", ""), wdt.replace(" ", "")),
                    ],
                    max_len=MAX_POSTSCRIPT_NAME_LEN,
                )
                generic_info_message(f"PostScript Name shortened: {postscript_name}.")

        # Print a warning if PostScript Name is longer than 29 chars.
        if len(postscript_name) > MAX_POSTSCRIPT_NAME_LEN:
            generic_warning_message(
                f"PostScript Name is longer than {MAX_POSTSCRIPT_NAME_LEN} characters "
                f"(actually {len(postscript_name)})."
            )

        # Build the Full Font Name
        full_font_name = font.name_table.getDebugName(4)

        if 4 not in exclude_namerecords:
            full_font_name = f"{family_name_ot} {subfamily_name_ot}"

            # Apply the explicitly passed shortenings
            if 4 in shorten_width:
                if not super_family:
                    full_font_name = f"{family_name_ot.replace(width, wdt)} {subfamily_name_ot}"
                else:
                    full_font_name = f"{family_name_ot} {subfamily_name_ot.replace(width, wdt)}"
            if 4 in shorten_weight:
                full_font_name = full_font_name.replace(weight, wgt)
            if 4 in shorten_slope:
                full_font_name = full_font_name.replace(slope, slp)

            # Check if the Full Font Name is longer than 31 chars and try to shorten it.
            if len(full_font_name) > MAX_FULL_NAME_LEN and auto_shorten:
                full_font_name = self.__auto_shorten_name(
                    string=full_font_name,
                    find_replace=[(slope, slp), (weight, wgt), (width, wdt)],
                    max_len=MAX_FULL_NAME_LEN,
                )
                generic_info_message(f"Full Font Name shortened: {full_font_name}.")

        # Print a warning if Full Font Name is longer than 31 chars.
        if len(full_font_name) > MAX_FULL_NAME_LEN:
            generic_warning_message(f"Full Font Name is longer than {MAX_FULL_NAME_LEN} characters.")

        # Build Unique Identifier
        ach_vend_id = str(font.os_2_table.achVendID).replace(" ", "").strip("\x00")
        font_revision = str(round(font.head_table.fontRevision, 3)).ljust(5, "0")
        unique_id = f"{font_revision};{ach_vend_id};{postscript_name}"

        if alt_uid:
            year_created = timestampToString(font.get_created_timestamp()).split(" ")[-1]
            manufacturer = font.name_table.getDebugName(8)
            unique_id = f"{manufacturer}: {family_name_ot}-{subfamily_name_ot}: {year_created}"

        # Build font revision
        version_string = f"Version {font_revision}"

        # Finally, write the namerecords!

        # nameID 1
        if 1 not in exclude_namerecords:
            # Nothing to shorten here. Windows family name is used only here and has already been shortened
            name_id_1 = family_name_win
            font.name_table.add_name(font=font, name_id=1, string=name_id_1)

        # nameID 2
        if 2 not in exclude_namerecords:
            # Windows Subfamily Name can be only Regular, Italic, Bold or Bold Italic and can't be shortened.
            name_id_2 = subfamily_name_win
            # Maximum length is 31 characters, but since we only use Regular, Italic, Bold and Bold Italic, there's no
            # need the check if the limit has been exceeded.
            font.name_table.add_name(font=font, name_id=2, string=name_id_2)

        # nameID 3
        if 3 not in exclude_namerecords:
            # This field has been already calculated and there's nothing to shorten here.
            name_id_3 = unique_id
            font.name_table.add_name(font=font, name_id=3, string=name_id_3)

        # nameID 4
        if 4 not in exclude_namerecords:
            # We have already shortened Full Font Name, and eventually auto shortened
            name_id_4 = full_font_name
            font.name_table.add_name(font=font, name_id=4, string=name_id_4)

        # nameID 5
        if 5 not in exclude_namerecords:
            # Version string has been already calculated, and there's nothing to shorten here.
            name_id_5 = version_string
            font.name_table.add_name(font=font, name_id=5, string=name_id_5)

        # nameID 6
        if 6 not in exclude_namerecords:
            # This field has already been calculated and shortened (and, eventually, auto shortened).
            name_id_6 = postscript_name
            font.name_table.add_name(font=font, name_id=6, string=name_id_6)

        # nameID 16
        if 16 not in exclude_namerecords:
            name_id_16 = family_name_ot
            # Let's apply the explicitly passed shortenings
            if 16 in shorten_width:
                # Width literal is here only if super_family is False
                if not super_family:
                    name_id_16 = name_id_16.replace(width, wdt)
            # Weight and Slope literals shouldn't be here, so they are not shortened.

            # If nameID 16 is not equal to nameID 1, write it. Otherwise, delete it in case is present.
            if name_id_16 != str(font.name_table.getName(nameID=1, platformID=3, platEncID=1, langID=0x409)):
                font.name_table.add_name(font=font, name_id=16, string=name_id_16)
            else:
                font.name_table.del_names(name_ids=[16])

        if 17 not in exclude_namerecords:
            name_id_17 = subfamily_name_ot
            # Let's apply the explicitly passed shortenings
            if 17 in shorten_width:
                # Width literal is here only if super_family is True
                if super_family:
                    name_id_17 = name_id_17.replace(width, wdt)
            if 17 in shorten_weight:
                name_id_17 = name_id_17.replace(weight, wgt)
            if 17 in shorten_slope:
                name_id_17 = name_id_17.replace(slope, slp)
            # If nameID 17 is not equal to nameID 2, write it. Otherwise, delete it in case is present.
            if name_id_17 != str(font.name_table.getName(nameID=2, platformID=3, platEncID=1, langID=0x409)):
                font.name_table.add_name(font=font, name_id=17, string=name_id_17)
            else:
                font.name_table.del_names(name_ids=[17])

        # Write CFF names
        if cff and font.is_cff:
            cff_family_name = f"{family_name} {width.replace(width_elidable, '')}".strip()
            if keep_width_elidable:
                cff_family_name = f"{family_name} {width}"
            font["CFF "].cff.fontNames = [postscript_name]
            font["CFF "].cff.topDictIndex[0].FullName = full_font_name
            font.fix_cff_top_dict_version()
            font["CFF "].cff.topDictIndex[0].FamilyName = cff_family_name
            font["CFF "].cff.topDictIndex[0].Weight = weight

    @staticmethod
    def __auto_shorten_name(string: str, find_replace: list, max_len: int) -> str:
        """
        Tries to shorten a string below the maximum allowed len by replacing long words (e.g.: 'ExtraBold', 'Condensed')
        with short ones (e.g.: 'XBd', 'Cn').

        :param string: The string to shorten
        :type string: str
        :param find_replace: a list of tuples, where the first element is the string to find (i.e.: the long word), and
            the second element is the string to replace it with (i.e.: the short word)
        :type find_replace: list
        :param max_len: The maximum length of the string
        :type max_len: int
        :return: A string that is no longer than max_len characters.
        """
        new_string = string

        for i in find_replace:
            new_string = new_string.replace(i[0], i[1])
            if len(new_string) <= max_len:
                return new_string

        return new_string

    @staticmethod
    def __match_string(input_string, remove_list, keep_list) -> str:
        """
        It takes a string, a list of words to remove, and a list of words to keep, and returns a string with the words
        to remove removed, and the words to keep kept. The returned string will be used to find a match abd recalculate
        data values.

        :param input_string: The string to remove words from
        :param remove_list: A list of words to be removed from the input string
        :param keep_list: A list of strings not to be removed from the input_string
        """
        for word in remove_list:
            if word not in keep_list:
                input_string = input_string.lower().replace(word.lower().replace(" ", ""), "")
                for k in keep_list:
                    if word.lower() in k.lower():
                        if len(input_string) > 0:
                            input_string = input_string.lower().replace(k.lower().replace(word.lower(), ""), k)
        return input_string

    @staticmethod
    def __get_key_from_value(d: dict, s: str):
        for key, values in d.items():
            for v in values:
                if s.lower().replace(" ", "") == v.lower().replace(" ", ""):
                    return key

    def reset_data(self, styles_mapping_file: str = None):
        """
        It takes a list of font files, and a styles mapping file, and creates a list of dictionaries, each dictionary
        representing a font, and each dictionary containing the font's name, style, weight, width, and selected status

        :param styles_mapping_file: The path to the styles mapping file
        :type styles_mapping_file: str
        """
        fonts_path = os.path.dirname(os.path.dirname(self.file))
        files = get_fonts_list(fonts_path)
        if not styles_mapping_file:
            styles_mapping_file = get_style_mapping_file_path(fonts_path)
        styles_mapping_data = StylesMappingFile(styles_mapping_file).get_data()
        rows = []
        for f in files:
            try:
                font = Font(f)
                font_row = self.__get_font_row(font, styles_mapping_data)
                font_row["selected"] = 1
                rows.append(font_row)
            except Exception as e:
                generic_error_message(e)
        self.save(rows)

    @staticmethod
    def __get_font_row(font: Font, styles_mapping_data: dict) -> dict:
        """
        Returns the row to write in the styles_mapping.json file.

        :param font: a Font object
        :param styles_mapping_data: a dictionary of the styles mapping file
        :return: A dictionary with the following keys:
        """

        font_info = font.get_font_info()
        file_name = font_info["file_name"]["value"]
        family_name = font_info["family_name"]["value"]
        is_bold = font_info["is_bold"]["value"]
        is_italic = font_info["is_italic"]["value"]
        is_oblique = font_info["is_oblique"]["value"]
        us_weight_class = str(font_info["us_weight_class"]["value"])
        us_width_class = str(font_info["us_width_class"]["value"])
        weights: dict = styles_mapping_data["weights"]
        widths: dict = styles_mapping_data["widths"]
        italics: list = styles_mapping_data["italics"]
        obliques: list = styles_mapping_data["obliques"]

        try:
            wgt, weight = weights[us_weight_class]
        except KeyError:
            wgt, weight = [us_weight_class, us_weight_class]

        try:
            wdt, width = widths[us_width_class]
        except KeyError:
            wdt, width = [us_width_class, us_width_class]

        slp = slope = None
        if is_italic:
            slp, slope = italics[0], italics[1]
        # If the font has both italic and oblique bits set, the oblique style name will be used.
        if is_oblique:
            slp, slope = obliques[0], obliques[1]

        row = dict(
            file_name=str(file_name),
            family_name=str(family_name),
            is_bold=int(is_bold),
            is_italic=int(is_italic),
            is_oblique=int(is_oblique),
            us_width_class=int(us_width_class),
            wdt=str(wdt),
            width=str(width),
            us_weight_class=int(us_weight_class),
            wgt=str(wgt),
            weight=str(weight),
            slp=str(slp).replace("None", ""),
            slope=str(slope).replace("None", ""),
        )

        return row

    def save(self, rows):
        header = (
            "file_name",
            "family_name",
            "is_bold",
            "is_italic",
            "is_oblique",
            "us_width_class",
            "wdt",
            "width",
            "us_weight_class",
            "wgt",
            "weight",
            "slp",
            "slope",
            "selected",
        )
        with open(self.file, "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, delimiter=";", fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def __normalize_string(string: str) -> str:
        return string.replace("-", "").replace("_", "").replace(" ", "").lower()

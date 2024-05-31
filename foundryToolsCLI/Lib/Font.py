import math
import os
import tempfile
import typing as t
from collections import Counter
from pathlib import Path

from cffsubr import subroutinize, desubroutinize
from fontTools.misc.psCharStrings import T2CharString
from fontTools.misc.timeTools import timestampToString
from fontTools.pens.statisticsPen import StatisticsPen
from fontTools.ttLib.ttFont import TTFont

from foundryToolsCLI.Lib.tables.OS_2 import TableOS2
from foundryToolsCLI.Lib.tables.head import TableHead
from foundryToolsCLI.Lib.tables.hhea import TableHhea
from foundryToolsCLI.Lib.tables.name import TableName
from foundryToolsCLI.Lib.tables.post import TablePost
from foundryToolsCLI.Lib.utils.otf_tools import correct_otf_contours
from foundryToolsCLI.Lib.utils.ps_recalc_zones import recalc_zones
from foundryToolsCLI.Lib.utils.ps_recalc_stems import recalc_stems
from foundryToolsCLI.Lib.utils.ttf_tools import correct_ttf_contours, decomponentize


# The Font class is a subclass of the fontTools.ttLib.TTFont class.
class Font(TTFont):
    def __init__(
        self,
        file=None,
        recalcBBoxes: bool = True,
        recalcTimestamp: bool = False,
        lazy: t.Optional[bool] = None,
    ):
        super().__init__(
            file=file, recalcBBoxes=recalcBBoxes, recalcTimestamp=recalcTimestamp, lazy=lazy
        )

    @property
    def is_otf(self) -> bool:
        """
        This function checks if the "CFF " table is present in the Font object and returns a boolean
        value.

        :return: A boolean value indicating whether the font is OpenType-PS.
        """
        return "CFF " in self

    @property
    def is_ttf(self) -> bool:
        """
        This function checks if the string "glyf" table is present in the Font object and returns a
        boolean value.

        :return: A boolean value indicating whether the font is TrueType.
        """
        return "glyf" in self

    @property
    def is_variable(self) -> bool:
        """
        This function checks if the "fvar" table is present in the Font object.

        :return: A boolean value indicating whether the font is variable.
        """
        return "fvar" in self

    @property
    def is_static(self) -> bool:
        """
        The function checks if the "fvar" table is not present in the Font object.

        :return: A boolean value indicating whether the font is static.
        """
        return "fvar" not in self

    @property
    def is_woff(self) -> bool:
        """
        This function checks if the flavor of a font file is "woff" and returns a boolean value.

        :return: A boolean value indicating whether the font flavor is "woff" flavored or not.
        """
        return self.flavor == "woff"

    @property
    def is_woff2(self) -> bool:
        """
        This function checks if the flavor of a font file is "woff2" and returns a boolean value.

        :return: A boolean value indicating whether the font is "woff2" flavored or not.
        """
        return self.flavor == "woff2"

    @property
    def is_web_font(self) -> bool:
        """
        This function checks if the font is in WOFF/WOFF2 format.

        :return: A boolean value indicating whether the "flavor" attribute of the object is None or
            not. If it is None, the function will return False, otherwise it will return True.
        """
        return self.flavor is not None

    @property
    def is_sfnt(self) -> bool:
        """
        This function checks if the font is in SFNT format.

        :return: A boolean value indicating whether the "flavor" attribute of the object is None or
            not. If it is None, the function will return True, otherwise it will return False.
        """
        return self.flavor is None

    @property
    def is_bold(self) -> bool:
        """
        > Checks if OS/2.fsSelection bit 5 and head.macStyle bit 0 are set

        :return: A boolean value.
        """
        head: TableHead = self["head"]
        os_2: TableOS2 = self["OS/2"]

        return head.is_bold_bit_set() and os_2.is_bold_bit_set()

    @property
    def is_italic(self) -> bool:
        """
        > Checks if  OS/2.fsSelection bit 0 and head.macStyle bit 1 are set

        :return: A boolean value.
        """
        head: TableHead = self["head"]
        os_2: TableOS2 = self["OS/2"]

        return head.is_italic_bit_set() and os_2.is_italic_bit_set()

    @property
    def is_regular(self) -> bool:
        """
        > Checks if the fsSelection bit 6 is set, and the bold and italic bits are not set

        :return: A boolean value.
        """
        os_2: TableOS2 = self["OS/2"]

        return os_2.is_regular_bit_set() and not self.is_bold and not self.is_italic

    @property
    def is_oblique(self) -> bool:
        """
        > Checks if OS/2.fsSelection bit 9 is set

        :return: A bool value.
        """
        os_2: TableOS2 = self["OS/2"]

        return os_2.is_oblique_bit_set()

    @property
    def is_upright(self) -> bool:
        """
        If the font is not italic and not oblique, then it is upright

        :return: A bool value.
        """
        return not self.is_italic and not self.is_oblique

    @property
    def created_timestamp(self) -> int:
        """
        This function returns the created timestamp stored in the 'head' table.

        :return: The function `get_created_timestamp` is returning an integer value representing the
        creation timestamp of the Font object.
        """
        return self["head"].created

    @property
    def modified_timestamp(self) -> int:
        """
        This function returns the modified timestamp stored in the "head" table.

        :return: an integer value representing the modified timestamp of the Font object.
        """
        return self["head"].modified

    @property
    def is_hinted_ttf(self) -> bool:
        return "fpgm" in self and self.is_ttf

    def set_bold_flag(self, value: bool) -> None:
        """
        Sets the bold bit in the OS/2 table and the head table, and clears the regular bit in the
        OS/2 table
        """

        head: TableHead = self["head"]
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_bold_bit()
            head.set_bold_bit()
            os_2.clear_regular_bit()
        else:
            os_2.clear_bold_bit()
            head.clear_bold_bit()
            if not self.is_italic:
                os_2.set_regular_bit()

    def set_italic_flag(self, value: bool) -> None:
        """
        Sets the italic bit in the OS/2 table and clears the regular bit
        """
        head: TableHead = self["head"]
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_italic_bit()
            head.set_italic_bit()
            os_2.clear_regular_bit()
        else:
            os_2.clear_italic_bit()
            head.clear_italic_bit()
            if not self.is_bold:
                os_2.set_regular_bit()

    def set_oblique_flag(self, value: bool) -> None:
        """
        Sets the oblique bit in the OS/2 table
        """
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_oblique_bit()
        else:
            os_2.clear_oblique_bit()

    def set_regular_flag(self, value: bool) -> None:
        """
        Sets the regular bit in the OS/2 table, clears the bold and italic bits in the OS/2 and head
        tables
        """
        if self.is_regular:
            return

        head: TableHead = self["head"]
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_regular_bit()
            os_2.clear_bold_bit()
            os_2.clear_italic_bit()
            head.clear_bold_bit()
            head.clear_italic_bit()
        else:
            if self.is_bold or self.is_italic:
                os_2.clear_regular_bit()

    def set_use_typo_metrics_flag(self, value: bool) -> None:
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_use_typo_metrics_bit()
        else:
            os_2.clear_use_typo_metrics_bit()

    def set_wws_consistent_flag(self, value: bool) -> None:
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_wws_consistent_bit()
        else:
            os_2.clear_wws_consistent_bit()

    def set_underscore_flag(self, value: bool) -> None:
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_underscore_bit()
        else:
            os_2.clear_underscore_bit()

    def set_negative_flag(self, value: bool) -> None:
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_negative_bit()
        else:
            os_2.clear_negative_bit()

    def set_outlined_flag(self, value: bool) -> None:
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_outlined_bit()
        else:
            os_2.clear_outlined_bit()

    def set_strikeout_flag(self, value: bool) -> None:
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_strikeout_bit()
        else:
            os_2.clear_strikeout_bit()

    def set_embed_level_flag(self, value: int) -> None:
        os2: TableOS2 = self["OS/2"]

        os2.set_embed_level(value)

    def set_bitmap_embedding_only_flag(self, value: bool) -> None:
        os2: TableOS2 = self["OS/2"]

        if value is True:
            os2.set_bitmap_embed_only_bit()
        else:
            os2.clear_bitmap_embed_only_bit()

    def set_no_subsetting_flag(self, value: bool) -> None:
        os_2: TableOS2 = self["OS/2"]

        if value is True:
            os_2.set_no_subsetting_bit()
        else:
            os_2.clear_no_subsetting_bit()

    def get_bounding_box(self):
        """Returns max and min bbox of the font"""
        y_min = 0
        y_max = 0
        if self.is_otf:
            y_min = self["head"].yMin
            y_max = self["head"].yMax
        else:
            for g in self["glyf"].glyphs:
                char = self["glyf"][g]
                if hasattr(char, "yMin") and y_min > char.yMin:
                    y_min = char.yMin
                if hasattr(char, "yMax") and y_max < char.yMax:
                    y_max = char.yMax
        return y_min, y_max

    def get_glyph_bounds(self, glyph_name: str) -> dict:
        glyph_set = self.getGlyphSet()
        if glyph_set.get(glyph_name) is None:
            return dict(xMin=0, yMin=0, xMax=0, yMax=0)
        bounds = T2CharString.calcBounds(glyph_set[glyph_name], glyph_set)
        if bounds:
            return dict(xMin=bounds[0], yMin=bounds[1], xMax=bounds[2], yMax=bounds[3])
        else:
            return dict(xMin=0, yMin=0, xMax=0, yMax=0)

    def recalc_x_height(self) -> int:
        return self.get_glyph_bounds("x")["yMax"]

    def recalc_cap_height(self) -> int:
        return self.get_glyph_bounds("H")["yMax"]

    def recalc_avg_char_width(self) -> int:
        avg_char_width = self["OS/2"].recalcAvgCharWidth(self)
        return avg_char_width

    def recalc_max_context(self) -> t.Optional[int]:
        if self["OS/2"].version < 2:
            return None
        from fontTools.otlLib.maxContextCalc import maxCtxFont

        max_context = maxCtxFont(self)
        return max_context

    def set_created_timestamp(self, timestamp: int) -> None:
        """
        This function sets the "created" attribute of the "head" table to the given timestamp.

        :param timestamp: an integer representing a Unix timestamp (number of seconds since January
            1, 1970) that indicates when the font was created
        :type timestamp: int
        """
        self["head"].created = timestamp

    def set_modified_timestamp(self, timestamp: int) -> None:
        """
        This function sets the "modified" attribute of the "head" table to the given timestamp.

        :param timestamp: an integer representing a Unix timestamp (number of seconds since January
            1, 1970) that indicates when the font was last modified
        :type timestamp: int
        """
        self["head"].modified = timestamp

    def get_real_extension(self) -> t.Optional[str]:
        """
        This function returns the file extension of a font file based on its flavor or type.

        :return: A string representing the file extension of a font file. If the font has a flavor,
            the extension will be ".woff" or ".woff2". If the font is a TrueType font, the extension
            will be ".ttf". If the font is an OpenType font, the extension will be ".otf".
        """
        if self.flavor is not None:
            return f".{self.flavor}"
        elif self.is_ttf:
            return ".ttf"
        elif self.is_otf:
            return ".otf"
        return None

    def ttf_decomponentize(self) -> None:
        """
        This function decomponentizes composite glyphs in a TrueType font.
        """
        if not self.is_ttf:
            return

        decomponentize(self)

    def ttf_dehint(self) -> None:
        """
        This function de-hints a TrueType font.
        """
        if not self.is_ttf:
            return

        from dehinter.font import dehint

        dehint(tt=self, verbose=False)

    def ttf_remove_overlaps(self, remove_hinting: bool = True, ignore_errors: bool = True):
        """
        This function removes overlaps in a TrueType font while optionally ignoring errors and
        removing hinting.

        :param remove_hinting: A boolean parameter that determines whether to remove hinting
            information when removing overlaps in the font.

        :type remove_hinting: bool (optional)

        :param ignore_errors: If set to True, any errors encountered during the overlap removal
            process will be ignored and the process will continue. If set to False, the process will
            stop and raise an error if any issues are encountered, defaults to True

        :type ignore_errors: bool (optional)
        """
        if self.is_otf or self.is_variable:
            return

        from fontTools.ttLib.removeOverlaps import removeOverlaps

        removeOverlaps(font=self, removeHinting=remove_hinting, ignoreErrors=ignore_errors)

    def ttf_scale_upem(self, units_per_em: int = 1000) -> None:
        """
        This function scales the UPM of a TrueType font. If the font is hinted, the hints will be
        removed before scaling the UPM.

        Args:
            units_per_em (int, optional): The target UPM. Defaults to 1000.

        Raises:
            ValueError: If the font is not a TrueType font.
        """
        if not self.is_ttf:
            raise ValueError("The font is not a TrueType font.")

        if self["head"].unitsPerEm == units_per_em:
            return

        from fontTools.ttLib.scaleUpem import scale_upem

        if self.is_hinted_ttf:
            self.ttf_dehint()
        scale_upem(self, new_upem=units_per_em)
        # TODO: If the font was hinted before scaling upem, rehint it after scaling upem

    def otf_dehint(self) -> None:
        """
        This function removes hints from the CFF table of an OpenType font.
        """
        if not self.is_otf:
            return

        self["CFF "].cff.remove_hints()

    def otf_desubroutinize(self) -> None:
        """
        This function removes subroutines from an OpenType font.
        """
        if not self.is_otf:
            return

        flavor = self.flavor
        self.flavor = None
        desubroutinize(otf=self)
        self.flavor = flavor

    def otf_subroutinize(self) -> None:
        """
        This function subroutinizes an OpenType font.
        """
        if not self.is_otf:
            return

        flavor = self.flavor
        self.flavor = None
        subroutinize(otf=self)
        self.flavor = flavor

    def otf_fix_contours(self, min_area: int = 25, verbose: bool = False) -> None:
        correct_otf_contours(font=self, min_area=min_area, verbose=verbose)

    def otf_recalc_zones(self) -> t.Optional[t.Tuple[t.List[int], t.List[int]]]:
        """
        This function recalculates the zones of an OpenType font.
        """
        if not self.is_otf:
            return

        zones = recalc_zones(font=self)
        return zones

    def otf_recalc_stems(self) -> t.Tuple[int, int]:
        """
        This function recalculates the stems of an OpenType font.
        """
        if not self.is_otf:
            raise ValueError("The font is not an OpenType font.")
        if not hasattr(self.reader, "file"):
            raise ValueError("The font is not a file-backed font.")

        stems = recalc_stems(file_path=Path(self.reader.file.name))
        return stems

    def set_zones(self, other_blues: t.List[int], blue_values: t.List[int]) -> None:
        """
        Set zones for a font.

        :param other_blues: Other blues.
        :param blue_values: Blue values.
        """
        if not self.is_otf:
            raise NotImplementedError("Setting zones is only supported for PostScript fonts.")

        self["CFF "].cff.topDictIndex[0].Private.BlueValues = blue_values
        self["CFF "].cff.topDictIndex[0].Private.OtherBlues = other_blues

    def set_stems(self, std_h_w: int, std_v_w: int) -> None:
        """
        Set stems for a font.

        :param std_h_w: StdHW.
        :param std_v_w: StdVW.
        """
        if not self.is_otf:
            raise NotImplementedError("Setting stems is only supported for PostScript fonts.")

        self["CFF "].cff.topDictIndex[0].Private.StdHW = std_h_w
        self["CFF "].cff.topDictIndex[0].Private.StdVW = std_v_w


    def ttf_fix_contours(
        self, min_area: int = 25, remove_hinting: bool = True, verbose: bool = False
    ) -> None:
        correct_ttf_contours(
            self, min_area=min_area, remove_hinting=remove_hinting, verbose=verbose
        )

    def add_dummy_dsig(self) -> None:
        """
        This function adds a dummy DSIG table to a font file if it does not already exist.
        """
        if self.flavor == "woff2":
            return

        from fontTools.ttLib import newTable

        values = dict(
            ulVersion=1,
            usFlag=0,
            usNumSigs=0,
            signatureRecords=[],
        )
        if "DSIG" not in self.keys():
            dsig = self["DSIG"] = newTable("DSIG")
            for k, v in values.items():
                setattr(dsig, k, v)

    def guess_family_name(self) -> str:
        """
        This function returns the font's family name, obtained from nameID 21, 16 or 1.

        :return: A string representing the font's family name.
        """
        return self["name"].getBestFamilyName()

    def guess_subfamily_name(self) -> str:
        """
        This function returns the font's subfamily name, obtained from nameID 22, 17 or 2.

        :return: A string representing the font's subfamily name.
        """
        return self["name"].getBestSubFamilyName()

    def get_file_name(self, source) -> str:
        """
        Returns the font's file name according to the passed source.

        1: FamilyName-StyleName (FamilyName is retrieved from nameID 21, 16 or 1; SubFamily name
        from nameID 22, 17 or 2)

        2: PostScript Name

        3: Full Font Name

        4: CFF TopDict fontNames. Valid for CFF fonts only. For TTF files will be used '1' as
        fallback value.

        5: CFF TipDict FullName (returns: Family Name Style Name or FamilyName-StyleName, depending
        on how FullName has been built). Valid for CFF fonts only. For TTF files will be used '1' as
        fallback value.

        :param source: The NameRecord or combination of NameRecords from which to build the file
            name.
        :return: A string representing the file name of the font.
        """

        if self.is_ttf:
            if source in (4, 5):
                source = 1

        if source == 1:
            return f"{self.guess_family_name()}-{self.guess_subfamily_name()}".replace(" ", "")
        elif source == 2:
            return self["name"].getDebugName(6)
        elif source == 3:
            return self["name"].getDebugName(4)
        elif source == 4:
            return self["CFF "].cff.fontNames[0]
        elif source == 5:
            return self["CFF "].cff.topDictIndex[0].FullName
        else:
            return Path(self.reader.file.name).stem

    def fix_cff_top_dict_version(self) -> None:
        if not self.is_otf:
            return
        font_revision = str(round(self["head"].fontRevision, 3)).split(".")
        major_version = int(font_revision[0])
        minor_version = int(font_revision[1])
        cff_font_version = f"{major_version}.{minor_version}"
        self["CFF "].cff.topDictIndex[0].version = cff_font_version

    def guess_foundry_name(self) -> str:
        """
        This function returns the foundry name of a font by checking the "name" or "OS/2" table.

        :return: a string that represents the foundry name. If nameID 8 is present in the "name"
            table, the Manufacturer Name string is returned. If nameID 8 is not present, but nameID
            9 is found, the Designer string is returned. If nor nameID 8 mor nameID 9 are present,
            the vendor code from the font's OS/2 table is returned. If also the vendor code is empty
            or not found, "Unknown" is returned.
        """
        manufacturer_name: str = self["name"].getDebugName(8)
        if manufacturer_name:
            return manufacturer_name

        designer: str = self["name"].getDebugName(9)
        if designer:
            return designer

        try:
            vendor_code: str = self["OS/2"].achVendID
            if vendor_code.strip().strip("\x00") == "":
                return "Unknown"
            else:
                return vendor_code
        except KeyError:
            return "Unknown"

    def make_temp_otf(self) -> tuple[int, Path]:
        from afdko.fdkutils import run_shell_command

        if self.flavor is None:
            source_file = self.reader.file.name
            remove_source_file = False
        else:
            self.flavor = None
            source_fd, source_file = tempfile.mkstemp(suffix=".tmp")
            self.save(source_file)
            remove_source_file = True
            os.close(source_fd)

        temp_t1_fd, temp_t1_file = tempfile.mkstemp(suffix=".t1")
        temp_otf_fd, temp_otf_file = tempfile.mkstemp(suffix=".otf")

        command_1 = ["tx", "-t1", source_file, temp_t1_file]
        command_2 = ["makeotf", "-f", temp_t1_file, "-o", temp_otf_file]

        run_shell_command(command_1, suppress_output=True)
        run_shell_command(command_2, suppress_output=True)

        os.close(temp_t1_fd)
        os.remove(temp_t1_file)
        if remove_source_file:
            os.remove(source_file)
        return temp_otf_fd, Path(temp_otf_file)

    def get_ui_name_ids(self) -> list:
        """
        Returns a list of all the UI name IDs in the font's GSUB table

        :return: A list of integers.
        """
        if "GSUB" not in self:
            return []
        else:
            ui_name_ids = []
            for record in self["GSUB"].table.FeatureList.FeatureRecord:
                if record.Feature.FeatureParams:
                    ui_name_ids.append(record.Feature.FeatureParams.UINameID)
        return sorted(set(ui_name_ids))

    def reorder_ui_name_ids(self) -> None:
        """
        Takes the IDs of the UI names in the name table and reorders them to start at 256
        """

        name_table: TableName = self["name"]

        if "GSUB" not in self:
            return
        ui_name_ids = self.get_ui_name_ids()
        for count, value in enumerate(ui_name_ids, start=256):
            for n in name_table.names:
                if n.nameID == value:
                    n.nameID = count
            for record in self["GSUB"].table.FeatureList.FeatureRecord:
                if record.Feature.FeatureParams:
                    if record.Feature.FeatureParams.UINameID == value:
                        record.Feature.FeatureParams.UINameID = count

    def modify_linegap_percent(self, percent):
        """
        Modifies the line spacing metrics

        Adapted from https://github.com/source-foundry/font-line
        """

        os2_table = self["OS/2"]
        head_table = self["head"]
        hhea_table = self["hhea"]

        # get observed start values from the font
        os2_typo_ascender = os2_table.sTypoAscender
        os2_typo_descender = os2_table.sTypoDescender
        os2_typo_linegap = os2_table.sTypoLineGap
        hhea_ascent = hhea_table.ascent
        hhea_descent = hhea_table.descent
        units_per_em = head_table.unitsPerEm

        # calculate necessary delta values
        os2_typo_ascdesc_delta = os2_typo_ascender + -os2_typo_descender
        hhea_ascdesc_delta = hhea_ascent + -hhea_descent

        # define percent UPM from command line request
        factor = 1.0 * int(percent) / 100

        # define line spacing units
        line_spacing_units = int(factor * units_per_em)

        # define total height as UPM + line spacing units
        total_height = line_spacing_units + units_per_em

        # height calculations for adjustments
        delta_height = total_height - hhea_ascdesc_delta
        upper_lower_add_units = int(0.5 * delta_height)

        # redefine hhea linegap to 0 in all cases
        hhea_linegap = 0

        # Define metrics based upon original design approach in the font
        # Google metrics approach
        if os2_typo_linegap == 0 and (os2_typo_ascdesc_delta > units_per_em):
            # define values
            os2_typo_ascender += upper_lower_add_units
            os2_typo_descender -= upper_lower_add_units
            hhea_ascent += upper_lower_add_units
            hhea_descent -= upper_lower_add_units
            os2_win_ascent = hhea_ascent
            os2_win_descent = -hhea_descent
        # Adobe metrics approach
        elif os2_typo_linegap == 0 and (os2_typo_ascdesc_delta == units_per_em):
            hhea_ascent += upper_lower_add_units
            hhea_descent -= upper_lower_add_units
            os2_win_ascent = hhea_ascent
            os2_win_descent = -hhea_descent
        else:
            os2_typo_linegap = line_spacing_units
            hhea_ascent = int(os2_typo_ascender + 0.5 * os2_typo_linegap)
            hhea_descent = -(total_height - hhea_ascent)
            os2_win_ascent = hhea_ascent
            os2_win_descent = -hhea_descent

        # define updated values from above calculations
        hhea_table.lineGap = hhea_linegap
        os2_table.sTypoAscender = os2_typo_ascender
        os2_table.sTypoDescender = os2_typo_descender
        os2_table.sTypoLineGap = os2_typo_linegap
        os2_table.usWinAscent = os2_win_ascent
        os2_table.usWinDescent = os2_win_descent
        hhea_table.ascent = hhea_ascent
        hhea_table.descent = hhea_descent

    def get_font_info(self) -> dict:
        """
        Returns a dictionary of font information

        :return: A dictionary of dictionaries.
        """
        head_table: TableHead = self["head"]
        hhea_table: TableHhea = self["hhea"]
        name_table: TableName = self["name"]
        os2_table: TableOS2 = self["OS/2"]
        post_table: TablePost = self["post"]

        from foundryToolsCLI.Lib.constants import EMBED_LEVEL_STRINGS

        font_info = dict(
            file_name={"label": "File name", "value": self.reader.file.name},
            sfnt_versions={
                "label": "SFNT version",
                "value": "PostScript" if self.sfntVersion == "OTTO" else "TrueType",
            },
            flavor={"label": "Flavor", "value": self.flavor},
            glyphs_number={
                "label": "Number of glyphs",
                "value": self["maxp"].numGlyphs,
            },
            family_name={
                "label": "Family name",
                "value": name_table.getBestFamilyName(),
            },
            subfamily_name={
                "label": "Subfamily name",
                "value": name_table.getBestSubFamilyName(),
            },
            full_name={
                "label": "Full name",
                "value": name_table.getBestFullName(),
            },
            postscript_name={
                "label": "PostScript name",
                "value": name_table.getDebugName(6),
            },
            unique_identifier={
                "label": "Unique ID",
                "value": name_table.getDebugName(3),
            },
            vendor_code={"label": "Vendor code", "value": os2_table.get_vend_id()},
            version={
                "label": "Version",
                "value": str(round(head_table.get_font_revision(), 3)),
            },
            date_created={
                "label": "Date created",
                "value": timestampToString(self.created_timestamp),
            },
            date_modified={
                "label": "Date modified",
                "value": timestampToString(self.modified_timestamp),
            },
            us_width_class={
                "label": "usWidthClass",
                "value": os2_table.get_width_class(),
            },
            us_weight_class={
                "label": "usWeightClass",
                "value": os2_table.get_weight_class(),
            },
            is_bold={"label": "Font is bold", "value": self.is_bold},
            is_italic={"label": "Font is italic", "value": self.is_italic},
            is_oblique={"label": "Font is oblique", "value": self.is_oblique},
            is_wws_consistent={
                "label": "WWS consistent",
                "value": os2_table.is_wws_bit_set(),
            },
            use_typo_metrics={
                "label": "Use Typo Metrics",
                "value": os2_table.is_use_typo_metrics_bit_set(),
            },
            underline_position={
                "label": "UL position",
                "value": post_table.underlinePosition,
            },
            underline_thickness={
                "label": "UL thickness",
                "value": post_table.underlineThickness,
            },
            italic_angle={"label": "Italic angle", "value": post_table.italicAngle},
            caret_slope_rise={
                "label": "Caret Slope Rise",
                "value": self["hhea"].caretSlopeRise,
            },
            caret_slope_run={
                "label": "Caret Slope Run",
                "value": self["hhea"].caretSlopeRun,
            },
            caret_offset={"label": "Caret Offset", "value": hhea_table.caretOffset},
            embed_level={
                "label": "Embedding",
                "value": f"{os2_table.get_embed_level()} "
                f"{EMBED_LEVEL_STRINGS.get(os2_table.get_embed_level())}",
            },
        )

        return font_info

    def get_font_v_metrics(self) -> dict:
        """
        The function returns a dictionary of dictionaries, where each dictionary contains a list of
        dictionaries.

        Each of the innermost dictionaries contains a label and a value.

        The label is the name of the metric, and the value is the value of the metric.

        The function returns the following metrics:

        - OS/2 Typographic Ascender
        - OS/2 Typographic Descender
        - OS/2 Typographic Line Gap
        - OS/2 Windows Ascent
        - OS/2 Windows Descent
        - hhea Ascent
        - hhea Descent
        - hhea Line Gap
        - head Units Per Em
        - head xMin
        - head yMin
        - head xMax
        - head yMax
        - head Font BBox

        The function returns the metrics in a dictionary of dictionaries, where each dictionary
        contains a list of dictionaries.

        The innermost dictionaries contain a label
        :return: A dictionary with three keys: os2_metrics, hhea_metrics, and head_metrics.
        """
        font_v_metrics = dict(
            os2_metrics=[
                {"label": "sTypoAscender", "value": self["OS/2"].sTypoAscender},
                {"label": "sTypoDescender", "value": self["OS/2"].sTypoDescender},
                {"label": "sTypoLineGap", "value": self["OS/2"].sTypoLineGap},
                {"label": "usWinAscent", "value": self["OS/2"].usWinAscent},
                {"label": "usWinDescent", "value": self["OS/2"].usWinDescent},
            ],
            hhea_metrics=[
                {"label": "ascent", "value": self["hhea"].ascent},
                {"label": "descent", "value": self["hhea"].descent},
                {"label": "lineGap", "value": self["hhea"].lineGap},
            ],
            head_metrics=[
                {"label": "unitsPerEm", "value": self["head"].unitsPerEm},
                {"label": "xMin", "value": self["head"].xMin},
                {"label": "yMin", "value": self["head"].yMin},
                {"label": "xMax", "value": self["head"].xMax},
                {"label": "yMax", "value": self["head"].yMax},
                {
                    "label": "Font BBox",
                    "value": f"({self['head'].xMin}, {self['head'].yMin}) "
                    f"({self['head'].xMax}, {self['head'].yMax})",
                },
            ],
        )

        return font_v_metrics

    def get_font_feature_tags(self) -> t.List[str]:
        """
        Returns a sorted list of all the feature tags in the font's GSUB and GPOS tables

        :return: A list of feature tags.
        """
        feature_tags = set[str]()
        for table_tag in ("GSUB", "GPOS"):
            if table_tag in self:
                if not self[table_tag].table.ScriptList or not self[table_tag].table.FeatureList:
                    continue
                feature_tags.update(
                    feature_record.FeatureTag
                    for feature_record in self[table_tag].table.FeatureList.FeatureRecord
                )
        return sorted(feature_tags)

    def calculate_italic_angle(self, min_slant: float = 2.0) -> int:
        """
        Calculates the italic angle of a font by drawing the glyph "H" and calculating the angle of
        the slant.

        :param min_slant: The minimum slant angle that will be considered as italic, defaults to 2.0
        :type min_slant: float (optional)

        :return: An integer representing the italic angle of the font.
        """
        glyph_set = self.getGlyphSet()
        pen = StatisticsPen(glyphset=glyph_set)
        for g in ("H", "uni0048"):
            try:
                glyph_set[g].draw(pen)
                italic_angle: int = -1 * round(math.degrees(math.atan(pen.slant)))
                if abs(italic_angle) >= abs(min_slant):
                    return italic_angle
                else:
                    return 0
            except KeyError:
                continue
        raise ValueError("The font does not contain the glyph 'H' or 'uni0048'.")

    def check_italic_angle(self, min_slant: float = 2.0) -> bool:
        # Allow .1 degrees tolerance
        return (
            abs(self.calculate_italic_angle(min_slant=min_slant) - self["post"].italicAngle) < 0.1
        )

    def calculate_caret_slope_rise(self) -> int:
        if self["post"].italicAngle == 0:
            return 1
        else:
            return self["head"].unitsPerEm

    def calculate_caret_slope_run(self) -> int:
        if self["post"].italicAngle == 0:
            return 0
        else:
            return round(
                math.tan(math.radians(-self["post"].italicAngle)) * self["head"].unitsPerEm
            )

    def calculate_run_rise_angle(self) -> float:
        rise = self["hhea"].caretSlopeRise
        run = self["hhea"].caretSlopeRun
        run_rise_angle = math.degrees(math.atan(-run / rise))
        return run_rise_angle

    def calculate_italic_bits(self, mode: int = 1):
        """
        If the italic angle is not 0, set the italic and/or oblique bits

        :param mode: click.IntRange(1, 3) = 1, defaults to 1
        :type mode: click.IntRange(1, 3) (optional)
        """

        italic_angle = self["post"].italicAngle

        if round(italic_angle) != 0:
            # Set italic bits only
            if mode == 1:
                self.set_italic_flag(True)
                self.set_oblique_flag(False)
            # Set italic and oblique bits
            if mode == 2:
                self.set_italic_flag(True)
                self.set_oblique_flag(True)
            # Set oblique bit only
            if mode == 3:
                self.set_oblique_flag(True)
                self.set_italic_flag(False)
        else:
            self.set_italic_flag(False)
            self.set_oblique_flag(False)

    # Copied from fontbakery/profiles/shared_conditions.py
    def glyph_metrics_stats(self) -> dict:
        """Returns a dict containing whether the font seems_monospaced,
        what's the maximum glyph width and what's the most common width.

        For a font to be considered monospaced, if at least 80% of ASCII
        characters have glyphs, then at least 80% of those must have the same
        width, otherwise all glyphs of printable characters must have one of
        two widths or be zero-width.
        """
        glyph_metrics = self["hmtx"].metrics
        # NOTE: `range(a, b)` includes `a` and does not include `b`.
        #       Here we don't include 0-31 as well as 127
        #       because these are control characters.
        ascii_glyph_names = [
            self.getBestCmap()[c] for c in range(32, 127) if c in self.getBestCmap()
        ]

        if len(ascii_glyph_names) > 0.8 * (127 - 32):
            ascii_widths = [
                adv
                for name, (adv, lsb) in glyph_metrics.items()
                if name in ascii_glyph_names and adv != 0
            ]
            ascii_width_count = Counter(ascii_widths)
            ascii_most_common_width = ascii_width_count.most_common(1)[0][1]
            seems_monospaced = ascii_most_common_width >= len(ascii_widths) * 0.8
        else:
            from fontTools import unicodedata

            # Collect relevant glyphs.
            relevant_glyph_names = set()
            # Add character glyphs that are in one of these categories:
            # Letter, Mark, Number, Punctuation, Symbol, Space_Separator.
            # This excludes Line_Separator, Paragraph_Separator and Control.
            for value, name in self.getBestCmap().items():
                if unicodedata.category(chr(value)).startswith(("L", "M", "N", "P", "S", "Zs")):
                    relevant_glyph_names.add(name)
            # Remove character glyphs that are mark glyphs.
            gdef = self.get("GDEF")
            if gdef and gdef.table.GlyphClassDef:
                marks = {name for name, c in gdef.table.GlyphClassDef.classDefs.items() if c == 3}
                relevant_glyph_names.difference_update(marks)

            widths = sorted(
                {
                    adv
                    for name, (adv, lsb) in glyph_metrics.items()
                    if name in relevant_glyph_names and adv != 0
                }
            )
            seems_monospaced = len(widths) <= 2

        width_max = max(adv for k, (adv, lsb) in glyph_metrics.items())
        most_common_width = Counter([g for g in glyph_metrics.values() if g[0] != 0]).most_common(
            1
        )[0][0][0]
        return {
            "seems_monospaced": seems_monospaced,
            "width_max": width_max,
            "most_common_width": most_common_width,
        }

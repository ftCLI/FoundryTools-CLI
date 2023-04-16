import math
import os

import click
from beziers.path import BezierPath, Line, Point
from fontTools.misc.timeTools import timestampToString
from fontTools.otlLib.maxContextCalc import maxCtxFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, registerCustomTableClass, newTable
from ufo2ft.fontInfoData import intListToNum
from ufo2ft.util import calcCodePageRanges

from ftCLI.Lib import constants
from ftCLI.Lib.tables.OS_2 import TableOS2
from ftCLI.Lib.tables.head import TableHead
from ftCLI.Lib.tables.hhea import TableHhea
from ftCLI.Lib.tables.name import TableName
from ftCLI.Lib.tables.post import TablePost
from ftCLI.Lib.utils.glyphs import get_glyph_bounds
from ftCLI.Lib.utils.misc import is_nth_bit_set, unset_nth_bit

registerCustomTableClass("OS/2", "ftCLI.Lib.tables.OS_2", "TableOS2")
registerCustomTableClass("head", "ftCLI.Lib.tables.head", "TableHead")
registerCustomTableClass("name", "ftCLI.Lib.tables.name", "TableName")
registerCustomTableClass("post", "ftCLI.Lib.tables.post", "TablePost")
registerCustomTableClass("hhea", "ftCLI.Lib.tables.hhea", "TableHhea")


class Font(TTFont):
    def __init__(self, file, recalcBBoxes=True, recalcTimestamp=False):
        super().__init__(file=file, recalcBBoxes=recalcBBoxes, recalcTimestamp=recalcTimestamp)

        self.file = file
        self.name_table: TableName = self["name"]
        self.os_2_table: TableOS2 = self["OS/2"]
        self.head_table: TableHead = self["head"]
        self.post_table: TablePost = self["post"]
        self.hhea_table: TableHhea = self["hhea"]

    @property
    def is_cff(self) -> bool:
        return self.sfntVersion == "OTTO"

    @property
    def is_true_type(self) -> bool:
        return "glyf" in self

    @property
    def is_woff(self) -> bool:
        return self.flavor == "woff"

    @property
    def is_woff2(self) -> bool:
        return self.flavor == "woff2"

    @property
    def is_variable(self) -> bool:
        return "fvar" in self

    @property
    def is_static(self) -> bool:
        """
        > Checks if ths font is static

        :return: A boolean value.
        """
        return "fvar" not in self

    @property
    def is_bold(self) -> bool:
        """
        > Checks if OS/2.fsSelection bit 5 and head.macStyle bit 0 are set

        :return: A boolean value.
        """
        return is_nth_bit_set(self.head_table.macStyle, 0) and is_nth_bit_set(self.os_2_table.fsSelection, 5)

    @property
    def is_italic(self) -> bool:
        """
        > Checks if  OS/2.fsSelection bit 0 and head.macStyle bit 1 are set

        :return: A boolean value.
        """
        return is_nth_bit_set(self["head"].macStyle, 1) and is_nth_bit_set(self["OS/2"].fsSelection, 0)

    @property
    def is_regular(self) -> bool:
        """
        > Checks if the fsSelection bit 6 is set, and the bold and italic bits are not set

        :return: A boolean value.
        """
        return self.os_2_table.is_regular_bit_set() and not self.is_bold and not self.is_italic

    @property
    def is_oblique(self) -> bool:
        """
        > Checks if OS/2.fsSelection bit 9 is set

        :return: A bool value.
        """
        return self.os_2_table.is_oblique_bit_set()

    @property
    def is_upright(self) -> bool:
        """
        If the font is not italic and not oblique, then it is upright

        :return: A bool value.
        """
        return not self.is_italic and not self.is_oblique

    @property
    def is_hinted_ttf(self) -> bool:
        return "fpgm" in self and self.is_true_type

    def set_bold(self):
        """
        Sets the bold bit in the OS/2 table and the head table, and clears the regular bit in the OS/2 table
        """
        self.os_2_table.set_bold_bit()
        self.head_table.set_bold_bit()
        self.os_2_table.clear_regular_bit()

    def unset_bold(self):
        """
        Clears the bold bit in the OS/2 table, and if the font is not italic, it sets the regular bit.
        """
        self.os_2_table.clear_bold_bit()
        self.head_table.clear_bold_bit()
        if not self.is_italic:
            self.os_2_table.set_regular_bit()

    def set_italic(self):
        """
        Sets the italic bit in the OS/2 table and clears the regular bit
        """
        self.os_2_table.set_italic_bit()
        self.head_table.set_italic_bit()
        self.os_2_table.clear_regular_bit()

    def unset_italic(self):
        """
        Clears the italic bit in the OS/2 table and the head table, and if the font is not bold, sets the regular bit
        in the OS/2 table
        """
        self.os_2_table.clear_italic_bit()
        self.head_table.clear_italic_bit()
        if not self.is_bold:
            self.os_2_table.set_regular_bit()

    def set_upright(self):
        """
        Clears the italic and oblique bits
        """
        self.os_2_table.clear_italic_bit()
        self.os_2_table.clear_oblique_bit()
        self.head_table.clear_italic_bit()
        if not self.is_bold:
            self.os_2_table.set_regular_bit()

    def set_regular(self):
        """
        Sets the regular bit in the OS/2 table, clears the bold and italic bits in the OS/2 and head tables
        """
        self.os_2_table.set_regular_bit()
        self.os_2_table.clear_bold_bit()
        self.os_2_table.clear_italic_bit()
        self.head_table.clear_bold_bit()
        self.head_table.clear_italic_bit()

    def set_oblique(self):
        """
        Sets the oblique bit in the OS/2 table
        """
        self.os_2_table.set_oblique_bit()

    def unset_oblique(self):
        """
        Clears the oblique bit in the OS/2 table
        """
        self.os_2_table.clear_oblique_bit()

    def calculate_italic_bits(self, mode: click.IntRange(1, 3) = 1):
        """
        If the italic angle is not 0, set the italic and/or oblique bits

        :param mode: click.IntRange(1, 3) = 1, defaults to 1
        :type mode: click.IntRange(1, 3) (optional)
        """

        italic_angle = self.post_table.italicAngle

        if round(italic_angle) != 0:
            # Set italic bits only
            if mode == 1:
                self.set_italic()
                self.unset_oblique()
            # Set italic and oblique bits
            if mode == 2:
                self.set_italic()
                self.set_oblique()
            # Set oblique bit only
            if mode == 3:
                self.set_oblique()
                self.unset_italic()
        else:
            self.unset_italic()
            self.unset_oblique()

    def calculate_italic_angle(self) -> float:
        """
        Calculates the italic angle of the font by processing the glyphs "bar" (uni007C), "bracketleft" (uni005B),
        "H" (uni0048), "I" (uni0049)

        Copied from fontbakery.profiles.post

        :return: The calculated italic angle.
        """

        # Calculating italic angle from the font's glyph outlines
        def x_leftmost_intersection(paths, y):
            for y_adjust in range(0, 20, 2):
                line = Line(Point(xMin - 100, y + y_adjust), Point(xMax + 100, y + y_adjust))
                for path in paths:
                    for s in path.asSegments():
                        intersections = s.intersections(line)
                        if intersections:
                            return intersections[0].point.x

        calculated_italic_angle = None
        for glyph_name in (
            "H",
            "uni0048",  # LATIN CAPITAL LETTER H
            "bar",
            "uni007C",  # VERTICAL LINE
            "I",
            "uni0049",  # LATIN CAPITAL LETTER I
            "bracketleft",
            "uni005B",  # LEFT SQUARE BRACKET
        ):
            try:
                paths = BezierPath.fromFonttoolsGlyph(self, glyph_name)
            except KeyError:
                continue

            # Get bounds
            bounds_pen = BoundsPen(self.getGlyphSet())
            self.getGlyphSet()[glyph_name].draw(bounds_pen)
            (xMin, yMin, xMax, yMax) = bounds_pen.bounds

            # Measure at 20% distance from bottom and top
            y_bottom = yMin + (yMax - yMin) * 0.2
            y_top = yMin + (yMax - yMin) * 0.8

            x_intsctn_bottom = x_leftmost_intersection(paths, y_bottom)
            x_intsctn_top = x_leftmost_intersection(paths, y_top)

            # Fails to calculate the intersection for some situations,
            # so try again with next glyph
            if not x_intsctn_bottom or not x_intsctn_top:
                continue

            x_d = x_intsctn_top - x_intsctn_bottom
            y_d = y_top - y_bottom

            calculated_italic_angle = -1 * math.degrees(math.atan2(x_d, y_d))

        # If the italic angle is < .5, this allows to not set the italic bits when using ftcli fix italic-angle command
        if abs(calculated_italic_angle) < 0.5:
            return 0
        else:
            return round(calculated_italic_angle)

    def check_italic_angle(self) -> bool:
        # Allow .1 degrees tolerance
        return abs(self.calculate_italic_angle() - self.post_table.italicAngle) < 0.1

    def calculate_caret_slope_rise(self) -> int:
        if self.post_table.italicAngle == 0:
            return 1
        else:
            return self.head_table.unitsPerEm

    def calculate_caret_slope_run(self) -> int:
        if self.post_table.italicAngle == 0:
            return 0
        else:
            return round(math.tan(math.radians(-self.post_table.italicAngle)) * self.head_table.unitsPerEm)

    def calculate_run_rise_angle(self) -> float:
        rise = self.hhea_table.caretSlopeRise
        run = self.hhea_table.caretSlopeRun
        run_rise_angle = math.degrees(math.atan(-run / rise))
        return run_rise_angle

    def calculate_codepage_ranges(self) -> (int, int):
        """
        Recalculates OS/2 table ulCodePageRange1 and ulCodPageRange1 values

        :return: ul_code_page_range1, ul_code_page_range2
        """
        unicodes = set()
        for table in self["cmap"].tables:
            if table.isUnicode():
                unicodes.update(table.cmap.keys())

        code_page_ranges = calcCodePageRanges(unicodes)
        codepage_range1 = intListToNum(code_page_ranges, 0, 32)
        codepage_range2 = intListToNum(code_page_ranges, 32, 32)

        return codepage_range1, codepage_range2

    def calculate_x_height(self) -> int:
        """
        If the OS/2 table version is 2 or higher, get the yMax value of the 'x' glyph and set the sxHeight value to that
        """
        if self.os_2_table.version >= 2:
            bounds = get_glyph_bounds(self.getGlyphSet(), "x")
            return bounds["yMax"]

    def calculate_cap_height(self) -> int:
        if self.os_2_table.version >= 2:
            bounds = get_glyph_bounds(self.getGlyphSet(), "H")
            return bounds["yMax"]

    def calculate_max_context(self) -> int:
        if self.os_2_table.version >= 2:
            max_context = maxCtxFont(self)
            return max_context

    def upgrade_os2_version(self, target_version: int) -> None:
        """
        Upgrades `OS/2` table version to `target_version`

        :param target_version: integer between 1 and 5
        :return: None
        """

        # Get the current version
        current_version = getattr(self.os_2_table, "version")

        # Target version must be greater than current version.
        if not target_version > current_version:
            return

        # Set the target version as first to suppress FontTools warnings
        setattr(self.os_2_table, "version", target_version)

        # When upgrading from version 0, ulCodePageRanges are to be recalculated.
        if current_version < 1:
            codepage_ranges = self.calculate_codepage_ranges()
            self.os_2_table.set_codepage_ranges(codepage_ranges)
            # Return if upgrading from version 0 to version 1.
            if target_version == 1:
                return

        # Upgrading from version 1 requires creating sxHeight, sCapHeight, usDefaultChar, usBreakChar and usMaxContext
        # entries.
        if current_version < 2:
            self.calculate_x_height()
            self.calculate_cap_height()
            setattr(self.os_2_table, "usDefaultChar", 0)
            setattr(self.os_2_table, "usBreakChar", 32)
            self.calculate_max_context()

        # Write default values if target_version == 5.
        if target_version > 4:
            setattr(self, "usLowerOpticalPointSize", 0)
            setattr(self, "usUpperOpticalPointSize", 65535 / 20)

        # Finally, make sure to clear bits 7, 8 and 9 in ['OS/2'].fsSelection when target version is lower than 4.
        if target_version < 4:
            for b in (7, 8, 9):
                setattr(self, "fsSelection", unset_nth_bit(self.os_2_table.fsSelection, b))

    def get_bounding_box(self):
        """Returns max and min bbox of the font"""
        y_min = 0
        y_max = 0
        if self.is_cff:
            y_min = self.head_table.yMin
            y_max = self.head_table.yMax
        else:
            for g in self["glyf"].glyphs:
                char = self["glyf"][g]
                if hasattr(char, "yMin") and y_min > char.yMin:
                    y_min = char.yMin
                if hasattr(char, "yMax") and y_max < char.yMax:
                    y_max = char.yMax
        return y_min, y_max

    def get_modified_timestamp(self):
        return self.head_table.modified

    def get_created_timestamp(self):
        return self.head_table.created

    def get_file_name(self, source) -> str:
        """
        Returns the font's file name according to the passed source.

        1: FamilyName-StyleName

        2: PostScript Name

        3: Full Font Name

        4: CFF TopDict fontNames. Valid for CFF fonts only. For TTF files will be used
        '1' as fallback value.

        5: CFF TipDict FullName (returns: Family Name Style Name or FamilyName-StyleName, depending on how FullName has
        been built). Valid for CFF fonts only. For TTF files will be used '1' as fallback value.

        :param source: The namerecord or combination of namerecords from which to build the file name.
        :return: The file name of the font.
        """

        if self.is_true_type:
            if source in (4, 5):
                source = 1

        if source == 1:
            return f"{self.guess_family_name()}-{self.guess_subfamily_name()}".replace(" ", "")
        elif source == 2:
            return self.name_table.getDebugName(6)
        elif source == 3:
            return self.name_table.getDebugName(4)
        elif source == 4:
            return self["CFF "].cff.fontNames[0]
        elif source == 5:
            return self["CFF "].cff.topDictIndex[0].FullName
        else:
            return os.path.basename(os.path.splitext(self.file)[0])

    def get_real_extension(self) -> str:
        if self.flavor is not None:
            return f".{self.flavor}"
        elif self.is_true_type:
            return ".ttf"
        elif self.is_cff:
            return ".otf"

    def guess_family_name(self) -> str:
        """
        If the font has a family name (nameID 16 or 1) in the English language, return it. Otherwise, return the family
        name in the first language in the font

        :return: The family name of the font.
        """
        family_name = self.name_table.getDebugName(16)
        if family_name is None:
            family_name = self.name_table.getDebugName(1)

        return family_name

    def guess_subfamily_name(self) -> str:
        """
        If the font has a subfamily name (nameID 17 or 2) in the English language, return it. Otherwise, return the
        subfamily name in the first language in the font

        :return: The family name of the font.
        """
        subfamily_name = self.name_table.getDebugName(17)
        if subfamily_name is None:
            subfamily_name = self.name_table.getDebugName(2)

        return subfamily_name

    def fix_cff_top_dict_version(self):
        if not self.is_cff:
            return
        font_revision = str(round(self.head_table.fontRevision, 3)).split(".")
        major_version = str(font_revision[0])
        minor_version = str(font_revision[1]).ljust(3, "0")
        cff_font_version = ".".join([major_version, str(int(minor_version))])
        self["CFF "].cff.topDictIndex[0].version = cff_font_version

    def get_font_info(self) -> dict:
        """
        Returns a dictionary of font information

        :return: A dictionary of dictionaries.
        """

        font_info = dict(
            file_name={"label": "File name", "value": self.file},
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
                "value": self.name_table.getBestFamilyName(),
            },
            subfamily_name={
                "label": "Subfamily name",
                "value": self.name_table.getBestSubFamilyName(),
            },
            full_name={
                "label": "Full name",
                "value": self.name_table.getBestFullName(),
            },
            postscript_name={
                "label": "PostScript name",
                "value": self.name_table.getDebugName(6),
            },
            unique_identifier={
                "label": "Unique ID",
                "value": self.name_table.getDebugName(3),
            },
            vendor_code={"label": "Vendor code", "value": self.os_2_table.achVendID},
            version={
                "label": "Version",
                "value": str(round(self.head_table.fontRevision, 3)),
            },
            date_created={
                "label": "Date created",
                "value": timestampToString(self.get_created_timestamp()),
            },
            date_modified={
                "label": "Date modified",
                "value": timestampToString(self.get_modified_timestamp()),
            },
            us_width_class={
                "label": "usWidthClass",
                "value": self.os_2_table.usWidthClass,
            },
            us_weight_class={
                "label": "usWeightClass",
                "value": self.os_2_table.usWeightClass,
            },
            is_bold={"label": "Font is bold", "value": self.is_bold},
            is_italic={"label": "Font is italic", "value": self.is_italic},
            is_oblique={"label": "Font is oblique", "value": self.is_oblique},
            is_wws_consistent={
                "label": "WWS consistent",
                "value": self.os_2_table.is_wws_bit_set(),
            },
            use_typo_metrics={
                "label": "Use Typo Metrics",
                "value": self.os_2_table.is_use_typo_metrics_bit_set(),
            },
            underline_position={
                "label": "UL position",
                "value": self.post_table.underlinePosition,
            },
            underline_thickness={
                "label": "UL thickness",
                "value": self.post_table.underlineThickness,
            },
            italic_angle={"label": "Italic angle", "value": self["post"].italicAngle},
            caret_slope_rise={
                "label": "Caret Slope Rise",
                "value": self["hhea"].caretSlopeRise,
            },
            caret_slope_run={
                "label": "Caret Slope Run",
                "value": self["hhea"].caretSlopeRun,
            },
            caret_offset={"label": "Caret Offset", "value": self["hhea"].caretOffset},
            embed_level={
                "label": "Embedding",
                "value": f"{self.os_2_table.get_embed_level()} "
                f"{constants.EMBED_LEVEL_STRINGS.get(self.os_2_table.get_embed_level())}",
            },
        )

        return font_info

    def get_font_v_metrics(self) -> dict:
        """
        The function returns a dictionary of dictionaries, where each dictionary contains a list of dictionaries.

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

        The function returns the metrics in a dictionary of dictionaries, where each dictionary contains a list of
        dictionaries.

        The innermost dictionaries contain a label
        :return: A dictionary with three keys: os2_metrics, hhea_metrics, and head_metrics.
        """
        font_v_metrics = dict(
            os2_metrics=[
                {"label": "sTypoAscender", "value": self.os_2_table.sTypoAscender},
                {"label": "sTypoDescender", "value": self.os_2_table.sTypoDescender},
                {"label": "sTypoLineGap", "value": self.os_2_table.sTypoLineGap},
                {"label": "usWinAscent", "value": self.os_2_table.usWinAscent},
                {"label": "usWinDescent", "value": self.os_2_table.usWinDescent},
            ],
            hhea_metrics=[
                {"label": "ascent", "value": self["hhea"].ascent},
                {"label": "descent", "value": self["hhea"].descent},
                {"label": "lineGap", "value": self["hhea"].lineGap},
            ],
            head_metrics=[
                {"label": "unitsPerEm", "value": self.head_table.unitsPerEm},
                {"label": "xMin", "value": self.head_table.xMin},
                {"label": "yMin", "value": self.head_table.yMin},
                {"label": "xMax", "value": self.head_table.xMax},
                {"label": "yMax", "value": self.head_table.yMax},
                {
                    "label": "Font BBox",
                    "value": f"({self.head_table.xMin}, {self.head_table.yMin}) "
                    f"({self.head_table.xMax}, {self.head_table.yMax})",
                },
            ],
        )

        return font_v_metrics

    def get_font_feature_tags(self) -> list:
        """
        Returns a sorted list of all the feature tags in the font's GSUB and GPOS tables

        :return: A list of feature tags.
        """

        feature_tags = set()
        for table_tag in ("GSUB", "GPOS"):
            if table_tag in self:
                if not self[table_tag].table.ScriptList or not self[table_tag].table.FeatureList:
                    continue
                feature_tags.update(
                    feature_record.FeatureTag for feature_record in self[table_tag].table.FeatureList.FeatureRecord
                )
        return sorted(feature_tags)

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

    def reorder_ui_name_ids(self):
        """
        Takes the IDs of the UI names in the name table and reorders them to start at 256
        """

        if "GSUB" not in self:
            return
        ui_name_ids = self.get_ui_name_ids()
        for count, value in enumerate(ui_name_ids, start=256):
            for n in self.name_table.names:
                if n.nameID == value:
                    n.nameID = count
            for record in self["GSUB"].table.FeatureList.FeatureRecord:
                if record.Feature.FeatureParams:
                    if record.Feature.FeatureParams.UINameID == value:
                        record.Feature.FeatureParams.UINameID = count

    def add_dummy_dsig(self):
        """
        Adds a dummy DSIG table to the font, unless the table is already present, or the font flavor is woff2
        """
        if self.flavor == "woff2":
            return
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

    def modify_linegap_percent(self, percent):
        """
        Modifies the line spacing metrics

        Adapted from https://github.com/source-foundry/font-line
        """

        # get observed start values from the font
        os2_typo_ascender = self.os_2_table.sTypoAscender
        os2_typo_descender = self.os_2_table.sTypoDescender
        os2_typo_linegap = self.os_2_table.sTypoLineGap
        hhea_ascent = self.hhea_table.ascent
        hhea_descent = self.hhea_table.descent
        units_per_em = self.head_table.unitsPerEm

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
        self.hhea_table.lineGap = hhea_linegap
        self.os_2_table.sTypoAscender = os2_typo_ascender
        self.os_2_table.sTypoDescender = os2_typo_descender
        self.os_2_table.sTypoLineGap = os2_typo_linegap
        self.os_2_table.usWinAscent = os2_win_ascent
        self.os_2_table.usWinDescent = os2_win_descent
        self.hhea_table.ascent = hhea_ascent
        self.hhea_table.descent = hhea_descent

    def decomponentize(self):
        if not self.is_true_type:
            return
        glyph_set = self.getGlyphSet()
        glyf_table = self["glyf"]
        dr_pen = DecomposingRecordingPen(glyph_set)
        tt_pen = TTGlyphPen(None)

        for glyph_name in self.glyphOrder:
            glyph = glyf_table[glyph_name]
            if not glyph.isComposite():
                continue

            dr_pen.value = []
            tt_pen.init()

            glyph.draw(dr_pen, glyf_table)
            dr_pen.replay(tt_pen)

            glyf_table[glyph_name] = tt_pen.glyph()

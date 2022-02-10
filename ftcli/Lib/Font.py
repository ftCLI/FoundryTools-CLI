import sys

import click
from fontTools.misc.textTools import num2binary
from fontTools.misc.timeTools import timestampToString
from fontTools.otlLib.maxContextCalc import maxCtxFont
from fontTools.ttLib import TTFont
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._n_a_m_e import (_MAC_LANGUAGE_CODES, _MAC_LANGUAGE_TO_SCRIPT, _WINDOWS_LANGUAGE_CODES)

from ftcli.Lib.utils import calcCodePageRanges, intListToNum


class Font(TTFont):

    def __init__(self, file, recalcTimestamp=False):
        super().__init__(file=file, recalcTimestamp=recalcTimestamp)

    def recalcNames(
            self, font_data, namerecords_to_ignore=None, shorten_weight=None, shorten_width=None, shorten_slope=None,
            fixCFF=False, linked_styles=None, is_superfamily=False, alt_uid=False, regular_italic=False,
            keep_regular=False, old_full_font_name=False, oblique_not_italic=False
    ):

        if linked_styles is None:
            linked_styles = []
        if shorten_width is None:
            shorten_width = []
        if shorten_weight is None:
            shorten_weight = []
        if shorten_slope is None:
            shorten_slope = []
        if namerecords_to_ignore is None:
            namerecords_to_ignore = []

        is_italic = bool(int(font_data['is_italic']))
        is_oblique = bool(int(font_data['is_oblique']))
        us_width_class = int(font_data['uswidthclass'])
        wdt = str(font_data['wdt'])
        width = str(font_data['width'])
        us_weight_class = int(font_data['usweightclass'])
        wgt = str(font_data['wgt'])
        weight = str(font_data['weight'])
        slp = str(font_data['slp'])
        slope = str(font_data['slope'])
        family_name = str(font_data['family_name'])

        # We clear the bold and italic bits. Only the italic bit value is read from the CSV file. The bold bits will be
        # set only if the -ls / --linked-styles option is active.
        self.setRegular()

        if is_italic:
            self.setItalic()

        # If is_oblique is True, the oblique bit is set, as well as the italic bits. In case we don't want to set
        # also the italic bits, this can be achieved setting oblique_not_italic to True.
        if is_oblique:
            self.setOblique()
            self.setItalic()
            if oblique_not_italic:
                is_italic = False
                self.unsetItalic()
                # If there are both obliques and italics in the same family, usWeightClass is increased by 10
                # us_weight_class += 10
        else:
            self.unsetOblique()

        # Set usWeightClass and usWidthClass values reading them from the CSV.
        self.setUsWeightClass(us_weight_class)
        self.setUsWidthClass(us_width_class)

        # OT family and subfamily name
        family_name_ot = family_name
        subfamily_name_ot = weight

        if width.lower() != "normal":
            if is_superfamily is False:
                family_name_ot = "{} {}".format(family_name, width)
            else:
                subfamily_name_ot = "{} {}".format(width, weight)

        if len(slope) > 0:
            subfamily_name_ot = "{} {}".format(subfamily_name_ot, slope)
            if not keep_regular:
                subfamily_name_ot = subfamily_name_ot.replace('Regular', '').replace('  ', ' ').strip()

        # Windows family and subfamily name
        family_name_win = "{} {} {}".format(
            family_name, width.replace("Normal", "").replace("Nor", ""), weight).replace("  ", " ").strip()

        # When there are both italic and oblique slopes in the family, the italic bits are cleared and the oblique bit
        # is set. Consequently, in case the font is oblique, the slope is added to family name.
        if len(slope) > 0 and is_italic is False:
            family_name_win = '{} {}'.format(family_name_win, slope)

        # In platformID 3, Subfamily name can be only Regular, Italic, Bold, Bold Italic.
        subfamily_name_win = "Regular"
        if is_italic is True or (is_oblique is True and oblique_not_italic is False):
            subfamily_name_win = "Italic"

        if len(linked_styles) == 2:

            # Remove Weight from Family Name
            if us_weight_class in linked_styles:
                family_name_win = family_name_win.replace(weight, "").replace("  ", " ").strip()

            linked_styles.sort()
            if us_weight_class == linked_styles[1]:
                # The bold bits are set HERE AND ONLY HERE.
                self.setBold()
                subfamily_name_win = "Bold"
                if is_italic is True:
                    subfamily_name_win = "Bold Italic"

        # Build the PostScript name.
        postscript_name = str(self['name'].getName(6, 3, 1, 0x409))

        if 6 not in namerecords_to_ignore:
            postscript_name = "{}-{}".format(
                # Remove dots and dashes from both family name and subfamily name
                family_name_ot.replace('.', '').replace('-', ''), subfamily_name_ot.replace('.', '').replace('-', ''))

            # Remove illegal characters
            for illegal_char in ('[', ']', '{', '}', '<', '>', '/', '%'):
                postscript_name = postscript_name.replace(illegal_char, '')

            if regular_italic:
                postscript_name = postscript_name.replace("-Italic", "-RegularItalic")

            # Let's replace long words (e.g. 'Italic') with short words (e.g. 'It') when --shorten-width,
            # --shorten-weight or --shorten-slope are active.
            postscript_name = postscript_name.replace(weight, wgt) if 6 in shorten_weight else postscript_name
            postscript_name = postscript_name.replace(width, wdt) if 6 in shorten_width else postscript_name
            postscript_name = postscript_name.replace(slope, slp) if 6 in shorten_slope else postscript_name

            # Do not remove spaces and dots before, if not the -swdt, -swgt and -sita switches won't work!
            postscript_name = postscript_name.replace(" ", "").replace(".", "")

        # Build the Unique Identifier
        ach_vend_id = str(self['OS/2'].achVendID).replace(" ", "").replace(r'\x00', "")
        font_revision = str(round(self['head'].fontRevision, 3)).ljust(5, "0")
        version_string = "Version {}".format(font_revision)

        unique_id = "{};{};{}".format(font_revision, ach_vend_id.ljust(4), postscript_name)

        if alt_uid:
            year_created = timestampToString(
                self['head'].created).split(" ")[-1]
            manufacturer = self['name'].getName(8, 3, 1, 0x409)
            unique_id = "{}: {}-{}: {}".format(manufacturer, family_name_ot, subfamily_name_ot, year_created)

        # Build the Full Font Name
        full_font_name = "{} {}".format(family_name_ot, subfamily_name_ot)

        # Finally, write the namerecords.

        # nameID 1
        if 1 not in namerecords_to_ignore:

            name_id_1 = family_name_win
            name_id_1 = name_id_1.replace(weight, wgt) if 1 in shorten_weight else name_id_1
            name_id_1 = name_id_1.replace(width, wdt) if 1 in shorten_width else name_id_1
            name_id_1 = name_id_1.replace(slope, slp) if 1 in shorten_slope else name_id_1
            if len(name_id_1) > 27:
                click.secho('WARNING: family name length is more than 27 characters', fg='yellow')
            self.setMultilingualName(nameID=1, string=name_id_1)

        # nameID 2
        if 2 not in namerecords_to_ignore:
            # Windows Subfamily Name can be only Regular, Italic, Bold or Bold Italic and can't be shortened.
            name_id_2 = subfamily_name_win

            # Maximum length is 31 characters, but since we only use Regular, Italic, Bold and Bold Italic, there's no
            # need the check if the limit has been exceeded.
            self.setMultilingualName(nameID=2, string=name_id_2)

        # nameID 3
        if 3 not in namerecords_to_ignore:
            name_id_3 = unique_id
            name_id_3 = name_id_3.replace(weight, wgt) if 3 in shorten_weight else name_id_3
            name_id_3 = name_id_3.replace(width, wdt) if 3 in shorten_width else name_id_3
            name_id_3 = name_id_3.replace(slope, slp) if 3 in shorten_slope else name_id_3

            self.setMultilingualName(nameID=3, string=name_id_3)

        # nameID 4
        if 4 not in namerecords_to_ignore:

            name_id_4 = full_font_name
            name_id_4 = name_id_4.replace(weight, wgt) if 4 in shorten_weight else name_id_4
            name_id_4 = name_id_4.replace(width, wdt) if 4 in shorten_width else name_id_4
            name_id_4 = name_id_4.replace(slope, slp) if 4 in shorten_slope else name_id_4

            if len(name_id_4) > 31:
                click.secho('WARNING: full name length is more than 31 characters', fg='yellow')

            self.setMultilingualName(nameID=4, string=name_id_4)

            if old_full_font_name:
                self.setMultilingualName(nameID=4, string=postscript_name, mac=False)

        # nameID 5
        if 5 not in namerecords_to_ignore:
            name_id_5 = version_string

            self.setMultilingualName(nameID=5, string=name_id_5)

        # nameID6
        if 6 not in namerecords_to_ignore:
            # PostScript Name has already been shortened
            name_id_6 = postscript_name

            if len(name_id_6) > 31:
                click.secho('WARNING: PostScript name length is more than 31 characters', fg='yellow')

            self.setMultilingualName(nameID=6, string=name_id_6)

        # nameID 16
        if 16 not in namerecords_to_ignore:
            name_id_16 = family_name_ot
            name_id_16 = name_id_16.replace(weight, wgt) if 16 in shorten_weight else name_id_16
            name_id_16 = name_id_16.replace(width, wdt) if 16 in shorten_width else name_id_16
            name_id_16 = name_id_16.replace(slope, slp) if 16 in shorten_slope else name_id_16
            if not name_id_16 == str(self['name'].getName(1, 3, 1, 0x409)):
                self.setMultilingualName(nameID=16, string=name_id_16)
            else:
                self.delNameRecord(nameID=16)

        # nameID 17
        if 17 not in namerecords_to_ignore:
            name_id_17 = subfamily_name_ot
            name_id_17 = name_id_17.replace(weight, wgt) if 17 in shorten_weight else name_id_17
            name_id_17 = name_id_17.replace(width, wdt) if 17 in shorten_width else name_id_17
            name_id_17 = name_id_17.replace(slope, slp) if 17 in shorten_slope else name_id_17
            if not name_id_17 == str(self['name'].getName(2, 3, 1, 0x409)):
                self.setMultilingualName(nameID=17, string=name_id_17)
            else:
                self.delNameRecord(nameID=17)

        # nameID 18
        if 18 not in namerecords_to_ignore:
            name_id_18 = full_font_name
            name_id_18 = name_id_18.replace(weight, wgt) if 18 in shorten_weight else name_id_18
            name_id_18 = name_id_18.replace(width, wdt) if 18 in shorten_width else name_id_18
            name_id_18 = name_id_18.replace(slope, slp) if 18 in shorten_slope else name_id_18

            # We write nameID 18 only if different from nameID 4. Could be useful when nameID 4 string is longer than
            # 31 characters. See: https://typedrawers.com/discussion/617/family-name
            if not name_id_18 == str(self['name'].getName(4, 1, 0, 0x0)):
                self.setMultilingualName(nameID=18, string=name_id_18, windows=False)
            else:
                self.delNameRecord(nameID=18)

        # CFF Names
        if 'CFF ' in self and fixCFF is True:
            self['CFF '].cff.fontNames = [postscript_name]
            self['CFF '].cff.topDictIndex[0].FullName = full_font_name
            self['CFF '].cff.topDictIndex[0].FamilyName = family_name_ot
            self['CFF '].cff.topDictIndex[0].Weight = weight

    def setCFFName(self, fontNames=None, FullName=None, FamilyName=None, Weight=None, Copyright=None, Notice=None):

        count = 0

        if fontNames:
            if not self['CFF '].cff.fontNames == [fontNames]:
                self['CFF '].cff.fontNames = [fontNames]
                count += 1

        if FullName:
            if not self['CFF '].cff.topDictIndex[0].FullName == FullName:
                self['CFF '].cff.topDictIndex[0].FullName = FullName
                count += 1

        if FamilyName:
            if not self['CFF '].cff.topDictIndex[0].FamilyName == FamilyName:
                self['CFF '].cff.topDictIndex[0].FamilyName = FamilyName
                count += 1

        if Weight:
            if not self['CFF '].cff.topDictIndex[0].Weight == Weight:
                self['CFF '].cff.topDictIndex[0].Weight = Weight
                count += 1

        if Copyright:
            if not self['CFF '].cff.topDictIndex[0].Copyright == Copyright:
                self['CFF '].cff.topDictIndex[0].Copyright = Copyright
                count += 1

        if Notice:
            if not self['CFF '].cff.topDictIndex[0].Notice == Notice:
                self['CFF '].cff.topDictIndex[0].Notice = Notice
                count += 1

        return count

    def setMultilingualName(self, nameID=None, language='en', string="", windows=True, mac=True):

        if windows is True:
            self.delNameRecord(nameID, language=language, windows=True, mac=False)

        if mac is True:
            self.delNameRecord(nameID, language=language, windows=False, mac=True)

        names = {language: string}
        self['name'].addMultilingualName(names, ttFont=self, windows=windows, mac=mac, nameID=nameID)

    def delNameRecord(self, nameID, language='en', windows=True, mac=True):

        if language == 'ALL':
            windows = False
            mac = False
            for name in self['name'].names:
                if name.nameID == nameID:
                    self['name'].removeNames(
                        name.nameID, name.platformID, name.platEncID, name.langID)

        if windows is True:
            langID = _WINDOWS_LANGUAGE_CODES.get(language.lower())
            self['name'].removeNames(nameID, 3, 1, langID)

        if mac is True:
            macLang = _MAC_LANGUAGE_CODES.get(language.lower())
            macScript = _MAC_LANGUAGE_TO_SCRIPT.get(macLang)
            self['name'].removeNames(nameID, 1, macScript, macLang)

    def findReplace(self, oldString: str, newString: str, fixCFF=False, nameID=None, platform=None,
                    namerecords_to_ignore=None):

        platforms_list = []

        if platform == 'mac':
            platforms_list.append(1)

        if platform == 'win':
            platforms_list.append(3)

        if platform is None:
            for name in self['name'].names:
                if name.platformID not in platforms_list:
                    platforms_list.append(name.platformID)

        names_list = []

        if nameID is not None:
            for p in platforms_list:
                names_list.append([p, nameID])

        else:
            for name in self['name'].names:
                if name.platformID in platforms_list:
                    names_list.append([name.platformID, name.nameID])

        # If a nameID is excluded, it won't be changed even if it has been explicitly included.
        if namerecords_to_ignore:
            for name in self['name'].names:
                if name.nameID in namerecords_to_ignore and [name.platformID, name.nameID] in names_list:
                    names_list.remove([name.platformID, name.nameID])

        fixCount = 0

        for name in self['name'].names:
            if [name.platformID, name.nameID] in names_list:
                if oldString in str(name):
                    string = str(name).replace(oldString, newString).replace("  ", " ").strip()

                    self['name'].setName(
                        string, name.nameID, name.platformID, name.platEncID, name.langID)
                    fixCount += 1

        if 'CFF ' in self and fixCFF is True:
            try:
                fontName = str(getattr(self['CFF '].cff, 'fontNames')[0])
                fontName_new = fontName.replace(
                    oldString, newString).replace("  ", " ").strip()

                if not fontName == fontName_new:
                    fixCount += 1
                    self['CFF '].cff.fontNames = [fontName_new]
            except Exception as e:
                print(f"ERROR: {e}")

            input_object = self['CFF '].cff.topDictIndex[0]
            attr_list = ['FullName', 'FamilyName', 'Weight', 'Copyright', 'Notice']

            for a in attr_list:
                try:
                    old_value = str(getattr(input_object, a))
                    new_value = old_value.replace(oldString, newString).replace("  ", " ").strip()
                    if not old_value == new_value:
                        fixCount += 1
                        setattr(input_object, a, new_value)
                except:
                    pass

        return fixCount

    def win2mac(self):
        self.removeEmptyNames()
        for name in self['name'].names:
            if name.platformID == 3:
                string = name.toUnicode()
                try:
                    self.setMultilingualName(nameID=name.nameID, language='en', string=string, windows=False, mac=True)
                except:
                    # IMPORTANT: FOR NON STANDARD LANGUAGES ENCODINGS
                    # MAYBE THERE'S A BETTER WAY?
                    self.setMultilingualName(nameID=name.nameID, language='en', string=string.encode(), windows=False,
                                             mac=True)

    def addPrefix(self, prefix: str, name_ids: list, platform: str = None):

        platforms_list = [1, 3]
        if platform == 'mac':
            platforms_list = [1]
        if platform == 'win':
            platforms_list = [3]
        if platform is None:
            platforms_list = [1, 3]

        for namerecord in self['name'].names:
            for p in platforms_list:
                for n in name_ids:
                    if (namerecord.nameID, namerecord.platformID) == (n, p):
                        platEncID = namerecord.platEncID
                        langID = namerecord.langID
                        original_string = self['name'].getName(nameID=n, platformID=p, platEncID=platEncID,
                                                               langID=langID).toUnicode()
                        prefixed_string = f'{prefix}{original_string}'
                        self.setMultilingualName(nameID=n, windows=True if p == 3 else False,
                                                 mac=True if p == 1 else False, string=prefixed_string)

    def addSuffix(self, suffix: str, name_ids: list, platform: str = None):

        platforms_list = []
        if platform == 'mac':
            platforms_list = [1]
        if platform == 'win':
            platforms_list = [3]
        if platform is None:
            platforms_list = [1, 3]

        for namerecord in self['name'].names:
            for p in platforms_list:
                for n in name_ids:
                    if (namerecord.nameID, namerecord.platformID) == (n, p):
                        platEncID = namerecord.platEncID
                        langID = namerecord.langID
                        original_string = self['name'].getName(nameID=n, platformID=p, platEncID=platEncID,
                                                               langID=langID).toUnicode()
                        suffixed_string = f'{original_string}{suffix}'
                        self.setMultilingualName(nameID=n, windows=True if p == 3 else False,
                                                 mac=True if p == 1 else False, string=suffixed_string)

    def removeEmptyNames(self):
        for name in self['name'].names:
            if len(str(name)) == 0:
                self['name'].removeNames(
                    name.nameID, name.platformID, name.platEncID, name.langID)

    def delMacNames(self, exclude_namerecord=None):
        if exclude_namerecord is None:
            exclude_namerecord = []
        exclude_namerecord = [int(i) for i in exclude_namerecord]
        for name in self['name'].names:
            if name.platformID != 1 or name.nameID in exclude_namerecord:
                continue
            self['name'].removeNames(name.nameID, name.platformID, name.platEncID, name.langID)

    def modifyLinegapPercent(self, percent):
        try:

            # get observed start values from the font
            os2_typo_ascender = self["OS/2"].sTypoAscender
            os2_typo_descender = self["OS/2"].sTypoDescender
            os2_typo_linegap = self["OS/2"].sTypoLineGap
            hhea_ascent = self["hhea"].ascent
            hhea_descent = self["hhea"].descent
            units_per_em = self["head"].unitsPerEm

            # calculate necessary delta values
            os2_typo_ascdesc_delta = os2_typo_ascender + -(os2_typo_descender)
            hhea_ascdesc_delta = hhea_ascent + -(hhea_descent)

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
            self["hhea"].lineGap = hhea_linegap
            self["OS/2"].sTypoAscender = os2_typo_ascender
            self["OS/2"].sTypoDescender = os2_typo_descender
            self["OS/2"].sTypoLineGap = os2_typo_linegap
            self["OS/2"].usWinAscent = os2_win_ascent
            self["OS/2"].usWinDescent = os2_win_descent
            self["hhea"].ascent = hhea_ascent
            self["hhea"].descent = hhea_descent

        except Exception as e:
            click.secho("ERROR: {}".format(e), fg='red')
            sys.exit(1)

    def recalcXHeight(self) -> int:
        metrics = self.getGlyphsMetrics()
        try:
            x_height = metrics['x']['yMax']
        except KeyError:
            x_height = 0
        return round(x_height)

    def recalcCapHeight(self) -> int:
        metrics = self.getGlyphsMetrics()
        try:
            cap_height = metrics['H']['yMax']
        except KeyError:
            cap_height = 0
        return round(cap_height)

    def recalcCodePageRanges(self) -> (int, int):
        cmap = self['cmap']
        unicodes = set()
        for table in cmap.tables:
            if table.isUnicode():
                unicodes.update(table.cmap.keys())

        codePageRanges = calcCodePageRanges(unicodes)
        ulCodePageRange1 = intListToNum(codePageRanges, 0, 32)
        ulCodePageRange2 = intListToNum(codePageRanges, 32, 32)

        return ulCodePageRange1, ulCodePageRange2

    def recalcUsMaxContext(self) -> int:
        return maxCtxFont(self)

    def setOS2Version(self, target_version: int):

        current_version = self['OS/2'].version

        # Let's ensure to clear bits 7, 8 and 9 in ['OS/2'].fsSelection when target version is lower than 4.
        if target_version < 4:
            self.unsetUseTypoMetrics()
            self.unsetWWS()
            self.unsetOblique()

        self['OS/2'].version = target_version

        # When upgrading from version is 0, at least ulCodePageRanges are to be recalculated.
        if current_version == 0:
            attrs = {
                'ulCodePageRange1': self.recalcCodePageRanges()[0],
                'ulCodePageRange2': self.recalcCodePageRanges()[1],
            }
            for k, v in attrs.items():
                setattr(self['OS/2'], k, v)
            if target_version == 1:
                return

        # Upgrading from version 1 requires creating sxHeight, sCapHeight, usDefaultChar, usBreakChar and usMaxContext
        # entries.
        if current_version < 2:
            attrs = {
                'sxHeight': self.recalcXHeight(),
                'sCapHeight': self.recalcCapHeight(),
                'usDefaultChar': 0,
                'usBreakChar': 32,
                'usMaxContext': maxCtxFont(self),
            }
            for k, v in attrs.items():
                setattr(self['OS/2'], k, v)

        # Write default values
        if target_version == 5:
            attrs = {
                'usLowerOpticalPointSize': 0,
                'usUpperOpticalPointSize': 65535 / 20
            }
            for k, v in attrs.items():
                setattr(self['OS/2'], k, v)

    def isBold(self):
        return is_nth_bit_set(self['head'].macStyle, 0) and is_nth_bit_set(self['OS/2'].fsSelection, 5)

    def isItalic(self):
        return is_nth_bit_set(self['head'].macStyle, 1) and is_nth_bit_set(self['OS/2'].fsSelection, 0)

    def isOblique(self):
        return is_nth_bit_set(self['OS/2'].fsSelection, 9)

    def isRegular(self):
        return is_nth_bit_set(self['OS/2'].fsSelection, 6) and not self.isBold() and not self.isItalic()

    def isWWS(self):
        return is_nth_bit_set(self['OS/2'].fsSelection, 8)

    def setBold(self):
        self.__setBoldBits()
        self.__clearRegularBit()

    def setItalic(self):
        self.__setItalicBits()
        self.__clearRegularBit()

    def setOblique(self):
        if self['OS/2'].version < 4:
            print('OS/2 table version was {} and has been updated to 4'.format(self['OS/2'].version))
            self['OS/2'].version = 4
        self['OS/2'].fsSelection = set_nth_bit(self['OS/2'].fsSelection, 9)

    def setWWS(self):
        self['OS/2'].fsSelection = set_nth_bit(self['OS/2'].fsSelection, 8)

    def unsetBold(self):
        self.__clearBoldBits()
        if not self.isItalic():
            self.__setRegularBit()

    def unsetItalic(self):
        self.__clearItalicBits()
        if not self.isBold():
            self.__setRegularBit()

    def unsetOblique(self):
        self['OS/2'].fsSelection = unset_nth_bit(self['OS/2'].fsSelection, 9)

    def unsetWWS(self):
        self['OS/2'].fsSelection = unset_nth_bit(self['OS/2'].fsSelection, 8)

    def setRegular(self):
        self.__setRegularBit()
        self.__clearBoldBits()
        self.__clearItalicBits()

    def getUseTypoMetricsValue(self):
        return is_nth_bit_set(self['OS/2'].fsSelection, 7)

    def setUseTypoMetrics(self):
        if self['OS/2'].version > 3:
            self['OS/2'].fsSelection = set_nth_bit(self['OS/2'].fsSelection, 7)

    def unsetUseTypoMetrics(self):
        self['OS/2'].fsSelection = unset_nth_bit(self['OS/2'].fsSelection, 7)

    def setEmbedLevel(self, value: int):
        if value == 0:
            for b in (0, 1, 2, 3):
                self['OS/2'].fsType = unset_nth_bit(self['OS/2'].fsType, b)
        if value == 2:
            for b in (0, 2, 3):
                self['OS/2'].fsType = unset_nth_bit(self['OS/2'].fsType, b)
            self['OS/2'].fsType = set_nth_bit(self['OS/2'].fsType, 1)
        if value == 4:
            for b in (0, 1, 3):
                self['OS/2'].fsType = unset_nth_bit(self['OS/2'].fsType, b)
            self['OS/2'].fsType = set_nth_bit(self['OS/2'].fsType, 2)
        if value == 8:
            for b in (0, 1, 2):
                self['OS/2'].fsType = unset_nth_bit(self['OS/2'].fsType, b)
            self['OS/2'].fsType = set_nth_bit(self['OS/2'].fsType, 3)

    def getEmbedLevel(self) -> int:
        return int(num2binary(self['OS/2'].fsType, 16)[9:17], 2)

    def setNoSubsettingBit(self):
        self['OS/2'].fsType = set_nth_bit(self['OS/2'].fsType, 8)

    def clearNoSubsettingBit(self):
        self['OS/2'].fsType = unset_nth_bit(self['OS/2'].fsType, 8)

    def getNoSubsettingValue(self) -> bool:
        return is_nth_bit_set(self['OS/2'].fsType, 8)

    def setBitmapEmbedOnlyBit(self):
        self['OS/2'].fsType = set_nth_bit(self['OS/2'].fsType, 9)

    def clearBitmapEmbedOnlyBit(self):
        self['OS/2'].fsType = unset_nth_bit(self['OS/2'].fsType, 9)

    def getBitmapEmbedOnlyValue(self):
        return is_nth_bit_set(self['OS/2'].fsType, 9)

    def setUsWidthClass(self, value):
        self["OS/2"].usWidthClass = value

    def setUsWeightClass(self, value):
        self["OS/2"].usWeightClass = value

    def setAchVendID(self, value):
        self['OS/2'].achVendID = value

    def addDummyDSIG(self):
        values = dict(
            ulVersion=1,
            usFlag=0,
            usNumSigs=0,
            signatureRecords=[],
        )
        dsig = self['DSIG'] = newTable('DSIG')
        for k, v in values.items():
            setattr(dsig, k, v)

    def getFontInfo(self) -> dict:

        font_info = {
            'sfnt_version': {'label': 'Flavor', 'value': 'PostScript' if self.sfntVersion == 'OTTO' else 'TrueType'},
            'glyphs_number': {'label': 'Glyphs number', 'value': self['maxp'].numGlyphs},
            'date_created': {'label': 'Date created', 'value': timestampToString(self['head'].created)},
            'date_modified': {'label': 'Date modified', 'value': timestampToString(self['head'].modified)},
            'version': {'label': 'Version', 'value': self['head'].fontRevision},
            'vend_id': {'label': 'Vendor code', 'value': self['OS/2'].achVendID},
            'unique_identifier': {'label': 'Unique identifier', 'value': self['name'].getName(3, 3, 1, 0x409)},
            'us_width_class': {'label': 'usWidthClass', 'value': self['OS/2'].usWidthClass},
            'us_weight_class': {'label': 'usWeightClass', 'value': self['OS/2'].usWeightClass},
            'is_bold': {'label': 'Font is bold', 'value': self.isBold()},
            'is_italic': {'label': 'Font is italic', 'value': self.isItalic()},
            'is_oblique': {'label': 'Font is oblique', 'value': self.isOblique()},
            'is_wws_consistent': {'label': 'WWS consistent', 'value': self.isWWS()},
            'italic_angle': {'label': 'Italic angle', 'value': self['post'].italicAngle},
            'embed_level': {'label': 'Embedding', 'value': self.getEmbedLevel(),}
        }

        return font_info

    def getVerticalMetrics(self) -> dict:
        vertical_metrics = {
            'head_units_per_em': self['head'].unitsPerEm,
            'hhea_ascent': self['hhea'].ascent,
            'hhea_descent': self['hhea'].descent,
            'hhea_linegap': self['hhea'].lineGap,
            'head_x_min': self['head'].xMin,
            'head_y_min': self['head'].yMin,
            'head_x_max': self['head'].xMax,
            'head_y_max': self['head'].yMax,
            'os2_typo_ascender': self['OS/2'].sTypoAscender,
            'os2_typo_descender': self['OS/2'].sTypoDescender,
            'os2_typo_linegap': self['OS/2'].sTypoLineGap,
            'os2_win_ascent': self['OS/2'].usWinAscent,
            'os2_win_descent': self['OS/2'].usWinDescent,
        }

        return vertical_metrics

    def getGlyphsMetrics(self):
        glyphs_metrics = {}
        glyphset = self.getGlyphSet()
        for glyphname in glyphset.keys():

            if 'glyf' in self:
                glyph = self["glyf"][glyphname]
                if glyph.numberOfContours == 0:
                    # no data
                    continue
                glyph_metrics = {
                    "xMin": glyph.xMin,
                    "yMin": glyph.yMin,
                    "xMax": glyph.xMax,
                    "yMax": glyph.yMax,
                }
                glyphs_metrics[glyphname] = glyph_metrics

            else:
                bounds = self.getGlyphSet()[glyphname]._glyph.calcBounds(self.getGlyphSet())
                if bounds is None:
                    continue
                glyph_metrics = {
                    "xMin": bounds[0],
                    "yMin": bounds[1],
                    "xMax": bounds[2],
                    "yMax": bounds[3],
                }
                glyphs_metrics[glyphname] = glyph_metrics

        return glyphs_metrics

    def getFontFeatures(self):

        feature_list = []

        if 'GSUB' in self.keys():
            gsub_table = self['GSUB']
            feature_list += gsub_table.table.FeatureList.FeatureRecord

        if 'GPOS' in self.keys():
            gpos_table = self['GPOS']
            feature_list += gpos_table.table.FeatureList.FeatureRecord

        feature_tags = []
        if len(feature_list) > 0:
            for feature_record in feature_list:
                if feature_record.FeatureTag not in feature_tags:
                    feature_tags.append(feature_record.FeatureTag)

        return feature_tags

    def __setBoldBits(self):
        self['OS/2'].fsSelection = set_nth_bit(self['OS/2'].fsSelection, 5)
        self['head'].macStyle = set_nth_bit(self['head'].macStyle, 0)

    def __setItalicBits(self):
        self['OS/2'].fsSelection = set_nth_bit(self['OS/2'].fsSelection, 0)
        self['head'].macStyle = set_nth_bit(self['head'].macStyle, 1)

    def __setRegularBit(self):
        self['OS/2'].fsSelection = set_nth_bit(self['OS/2'].fsSelection, 6)

    def __clearBoldBits(self):
        self['OS/2'].fsSelection = unset_nth_bit(self['OS/2'].fsSelection, 5)
        self['head'].macStyle = unset_nth_bit(self['head'].macStyle, 0)

    def __clearItalicBits(self):
        self['OS/2'].fsSelection = unset_nth_bit(self['OS/2'].fsSelection, 0)
        self['head'].macStyle = unset_nth_bit(self['head'].macStyle, 1)

    def __clearRegularBit(self):
        self['OS/2'].fsSelection = unset_nth_bit(self['OS/2'].fsSelection, 6)


def is_nth_bit_set(x: int, n: int):
    if x & (1 << n):
        return True
    return False


def set_nth_bit(x: int, n: int):
    return x | 1 << n


def unset_nth_bit(x: int, n: int):
    return x & ~(1 << n)


PLATFORMS = {
    0: 'Unicode',
    1: 'Macintosh',
    2: 'ISO (deprecated)',
    3: 'Windows',
    4: 'Custom',
}

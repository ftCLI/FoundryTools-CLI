from textwrap import TextWrapper

import click
from fontTools.misc.timeTools import timestampToString
from fontTools.ttLib import TTFont
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._n_a_m_e import (_MAC_LANGUAGE_CODES, _MAC_LANGUAGE_TO_SCRIPT, _WINDOWS_LANGUAGE_CODES)


class TTFontCLI(TTFont):

    def __init__(self, file, recalcTimestamp=False):
        super().__init__(file=file, recalcTimestamp=recalcTimestamp)

    def recalcNames(
            self, font_data, namerecords_to_ignore=None, shorten_weight=None, shorten_width=None, shorten_slope=None,
            fixCFF=False, linked_styles=None, isSuperFamily=False, alt_uid=False, regular_italic=False,
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

        isItalic = bool(int(font_data['is_italic']))
        isOblique = bool(int(font_data['is_oblique']))
        usWidthClass = int(font_data['uswidthclass'])
        wdt = str(font_data['wdt'])
        width = str(font_data['width'])
        usWeightClass = int(font_data['usweightclass'])
        wgt = str(font_data['wgt'])
        weight = str(font_data['weight'])
        slp = str(font_data['slp'])
        slope = str(font_data['slope'])
        familyName = str(font_data['family_name'])

        # We clear the bold and italic bits. Only the italic bit value is read from the CSV file. The bold bits will be
        # set only if the -ls / --linked-styles option is active.
        self.setRegular()

        if isItalic:
            self.setItalic()

        # If isOblique is True, the oblique bit is set, as well as the italic bits. In case we don't want want to set
        # also the italic bits, this can be achieved setting oblique_not_italic to True.
        if isOblique:
            self.setOblique()
            self.setItalic()
            if oblique_not_italic:
                isItalic = False
                self.unsetItalic()
        else:
            self.unsetOblique()

        # Set usWeightClass and usWidthClass values reading them from the CSV.
        self.setUsWeightClass(usWeightClass)
        self.setUsWidthClass(usWidthClass)

        # Macintosh family and subfamily names

        familyNameMac = familyName

        subFamilyNameMac = weight

        if width.lower() != "normal":
            if isSuperFamily is False:
                familyNameMac = "{} {}".format(familyName, width)
            else:
                subFamilyNameMac = "{} {}".format(width, weight)

        if len(slope) > 0:
            subFamilyNameMac = "{} {}".format(subFamilyNameMac, slope)
            if not keep_regular:
                subFamilyNameMac = subFamilyNameMac.replace('Regular', '').replace('  ', ' ').strip()

        # Microsoft family and subfamily names

        familyNameWin = "{} {} {}".format(
            familyName, width.replace("Normal", "").replace("Nor", ""), weight).replace("  ", " ").strip()

        # When there are both italic and oblique slopes in the family, the italic bits are cleared and the oblique bit
        # is set. Consequently, in case the font is oblique, the slope is added to family name.
        if len(slope) > 0 and isItalic is False:
            familyNameWin = '{} {}'.format(familyNameWin, slope)

        # In platformID 3, Subfamily name can be only Regular, Italic, Bold, Bold Italic.
        subFamilyNameWin = "Regular"
        if isItalic is True or (isOblique is True and oblique_not_italic is False):
            subFamilyNameWin = "Italic"

        if len(linked_styles) == 2:

            # Remove Weight from Family Name
            if usWeightClass in linked_styles:
                familyNameWin = familyNameWin.replace(weight, "").replace("  ", " ").strip()

            linked_styles.sort()
            if usWeightClass == linked_styles[1]:
                # The bold bits are set here and only here.
                self.setBold()
                subFamilyNameWin = "Bold"
                if isItalic is True:
                    subFamilyNameWin = "Bold Italic"

        # Build the PostScript name.
        postScriptName = str(self['name'].getName(6, 3, 1, 0x409))

        if 6 not in namerecords_to_ignore:
            postScriptName = "{}-{}".format(
                familyNameMac, subFamilyNameMac)
            if regular_italic:
                postScriptName = postScriptName.replace(
                    "-Italic", "-RegularItalic")

            # Let's replace long words (e.g. 'Italic') with short words (e.g. 'It') when --shorten-width,
            # --shorten-weight or --shorten-slope are active.
            postScriptName = postScriptName.replace(weight, wgt) if 6 in shorten_weight else postScriptName
            postScriptName = postScriptName.replace(width, wdt) if 6 in shorten_width else postScriptName
            postScriptName = postScriptName.replace(slope, slp) if 6 in shorten_slope else postScriptName

            # Do not remove spaces and dots before, if not the -swdt, -swgt and -sita switches won't work!
            postScriptName = postScriptName.replace(" ", "").replace(".", "")

        # Build the Unique Identifier
        achVendID = str(self['OS/2'].achVendID).replace(" ", "").replace(r'\x00', "")
        fontRevision = str(round(self['head'].fontRevision, 3)).ljust(5, "0")
        versionString = "Version {}".format(fontRevision)

        uniqueID = "{};{};{}".format(fontRevision, achVendID.ljust(4), postScriptName)

        if alt_uid:
            year_created = timestampToString(
                self['head'].created).split(" ")[-1]
            manufacturer = self['name'].getName(8, 3, 1, 0x409)
            uniqueID = "{}:{} {}:{}".format(manufacturer, familyNameMac, subFamilyNameMac, year_created)

        # Build the Full Font Name
        fullFontName = "{} {}".format(familyNameMac, subFamilyNameMac)

        # Finally, write the namerecords.

        # nameID 1
        if 1 not in namerecords_to_ignore:
            string = familyNameMac
            string = string.replace(weight, wgt) if 1 in shorten_weight else string
            string = string.replace(width, wdt) if 1 in shorten_width else string
            string = string.replace(slope, slp) if 1 in shorten_slope else string
            self['name'].setName(string, 1, 1, 0, 0x0)

            string = familyNameWin
            string = string.replace(weight, wgt) if 1 in shorten_weight else string
            string = string.replace(width, wdt) if 1 in shorten_width else string
            string = string.replace(slope, slp) if 1 in shorten_slope else string
            self['name'].setName(string, 1, 3, 1, 0x409)

        # nameID 2
        if 2 not in namerecords_to_ignore:
            string = subFamilyNameMac
            string = string.replace(weight, wgt) if 2 in shorten_weight else string
            string = string.replace(width, wdt) if 2 in shorten_width else string
            string = string.replace(slope, slp) if 2 in shorten_slope else string
            self['name'].setName(string, 2, 1, 0, 0x0)

            # Windows Subfamily Name can be only Regular, Italic, Bold or Bold Italic and can't be shortened!
            self['name'].setName(subFamilyNameWin, 2, 3, 1, 0x409)

        # nameID 3
        if 3 not in namerecords_to_ignore:
            string = uniqueID
            string = string.replace(weight, wgt) if 3 in shorten_weight else string
            string = string.replace(width, wdt) if 3 in shorten_width else string
            string = string.replace(slope, slp) if 3 in shorten_slope else string
            self['name'].setName(string, 3, 1, 0, 0x0)
            self['name'].setName(string, 3, 3, 1, 0x409)

        # nameID 4
        if 4 not in namerecords_to_ignore:
            string = fullFontName
            string = string.replace(weight, wgt) if 4 in shorten_weight else string
            string = string.replace(width, wdt) if 4 in shorten_width else string
            string = string.replace(slope, slp) if 4 in shorten_slope else string
            self['name'].setName(string, 4, 1, 0, 0x0)
            self['name'].setName(string, 4, 3, 1, 0x409)

            # No need to shorten this!
            if old_full_font_name:
                self['name'].setName(postScriptName, 4, 3, 1, 0x409)

        # nameID 5
        if 5 not in namerecords_to_ignore:
            self['name'].setName(versionString, 5, 1, 0, 0x0)
            self['name'].setName(versionString, 5, 3, 1, 0x409)

        # nameID6
        if 6 not in namerecords_to_ignore:
            # Already shortened!
            self['name'].setName(postScriptName, 6, 1, 0, 0x0)
            self['name'].setName(postScriptName, 6, 3, 1, 0x409)

        # nameID 16
        if 16 not in namerecords_to_ignore:
            string = familyNameMac
            string = string.replace(weight, wgt) if 16 in shorten_weight else string
            string = string.replace(width, wdt) if 16 in shorten_width else string
            string = string.replace(slope, slp) if 16 in shorten_slope else string
            self['name'].setName(string, 16, 1, 0, 0x0)
            self['name'].setName(string, 16, 3, 1, 0x409)

        # nameID 17
        if 17 not in namerecords_to_ignore:
            string = subFamilyNameMac
            string = string.replace(weight, wgt) if 17 in shorten_weight else string
            string = string.replace(width, wdt) if 17 in shorten_width else string
            string = string.replace(slope, slp) if 17 in shorten_slope else string
            self['name'].setName(string, 17, 1, 0, 0x0)
            self['name'].setName(string, 17, 3, 1, 0x409)

        # nameID 18
        if 18 not in namerecords_to_ignore:
            string = fullFontName
            string = string.replace(weight, wgt) if 18 in shorten_weight else string
            string = string.replace(width, wdt) if 18 in shorten_width else string
            string = string.replace(slope, slp) if 18 in shorten_slope else string
            self['name'].setName(string, 18, 1, 0, 0x0)

        # CFF Names
        if 'CFF ' in self and fixCFF is True:
            self['CFF '].cff.fontNames = [postScriptName]
            self['CFF '].cff.topDictIndex[0].FullName = fullFontName
            self['CFF '].cff.topDictIndex[0].FamilyName = familyNameMac
            self['CFF '].cff.topDictIndex[0].Weight = weight

    def setMultilingualName(self, nameID=None, language='en', string="", windows=True, mac=True):

        if windows is True:
            self.delMultilingualName(nameID, language=language, windows=True, mac=False)

        if mac is True:
            self.delMultilingualName(
                nameID, language=language, windows=False, mac=True)

        names = {language: string}
        self['name'].addMultilingualName(names, ttFont=self, windows=windows, mac=mac, nameID=nameID)

    def delMultilingualName(self, nameID, language='en', windows=True, mac=True):

        if nameID is not None:
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

    def findReplace(self, oldString, newString, fixCFF=False, nameID=None, platform=None):

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
                except Exception as e:
                    click.secho('ERROR: {}'.format(e))
                    pass

        return fixCount

    def removeEmptyNames(self):
        for name in self['name'].names:
            if len(str(name)) == 0:
                self['name'].removeNames(
                    name.nameID, name.platformID, name.platEncID, name.langID)

    def delMacNames(self, exclude_namerecords=None):
        if exclude_namerecords is None:
            exclude_namerecords = []
        exclude_namerecords = [int(i) for i in exclude_namerecords]
        for name in self['name'].names:
            if name.platformID != 1 or name.nameID in exclude_namerecords:
                continue
            self['name'].removeNames(name.nameID, name.platformID, name.platEncID, name.langID)

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
                    self.setMultilingualName(
                        nameID=name.nameID, language='en', string=string.encode(), windows=False, mac=True)

    def isBold(self):
        return (
                is_nth_bit_set(self['head'].macStyle, 0)
                and is_nth_bit_set(self['OS/2'].fsSelection, 5)
        )

    def isItalic(self):
        return (
                is_nth_bit_set(self['head'].macStyle, 1)
                and is_nth_bit_set(self['OS/2'].fsSelection, 0)
        )

    def isOblique(self):
        return is_nth_bit_set(self['OS/2'].fsSelection, 9)

    def isRegular(self):
        return is_nth_bit_set(self['OS/2'].fsSelection, 6)

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

    def unsetBold(self):
        self.__clearBoldBits()
        if not self.isItalic():
            self.__setRegularBit()

    def unsetItalic(self):
        self.__clearItalicBits()
        if not self.isBold():
            self.__setRegularBit()

    def unsetOblique(self):
        self['OS/2'].fsSelection = unset_nth_bit(
            self['OS/2'].fsSelection, 9)

    def setRegular(self):
        self.__setRegularBit()
        self.__clearBoldBits()
        self.__clearItalicBits()

    def usesTypoMetrics(self):
        return is_nth_bit_set(self['OS/2'].fsSelection, 7)

    def setUseTypoMetrics(self):
        if self['OS/2'].version > 3:
            self['OS/2'].fsSelection = set_nth_bit(
                self['OS/2'].fsSelection, 7)

    def unsetUseTypoMetrics(self):
        self['OS/2'].fsSelection = unset_nth_bit(
            self['OS/2'].fsSelection, 7)

    def setEmbedLevel(self, value):
        if self['OS/2'].fsType != value:
            self['OS/2'].fsType = value

    def setUsWidthClass(self, value):
        if self["OS/2"].usWidthClass != value:
            self["OS/2"].usWidthClass = value

    def setUsWeightClass(self, value):
        if self["OS/2"].usWeightClass != value:
            self["OS/2"].usWeightClass = value

    def setAchVendID(self, value):
        if self['OS/2'].achVendID != value:
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

    def __setBoldBits(self):
        self['OS/2'].fsSelection = set_nth_bit(
            self['OS/2'].fsSelection, 5)
        self['head'].macStyle = set_nth_bit(self['head'].macStyle, 0)

    def __setItalicBits(self):
        self['OS/2'].fsSelection = set_nth_bit(
            self['OS/2'].fsSelection, 0)
        self['head'].macStyle = set_nth_bit(self['head'].macStyle, 1)

    def __setRegularBit(self):
        self['OS/2'].fsSelection = set_nth_bit(
            self['OS/2'].fsSelection, 6)

    def __clearBoldBits(self):
        self['OS/2'].fsSelection = unset_nth_bit(
            self['OS/2'].fsSelection, 5)
        self['head'].macStyle = unset_nth_bit(
            self['head'].macStyle, 0)

    def __clearItalicBits(self):
        self['OS/2'].fsSelection = unset_nth_bit(
            self['OS/2'].fsSelection, 0)
        self['head'].macStyle = unset_nth_bit(
            self['head'].macStyle, 1)

    def __clearRegularBit(self):
        self['OS/2'].fsSelection = unset_nth_bit(
            self['OS/2'].fsSelection, 6)


def is_nth_bit_set(x: int, n: int):
    if x & (1 << n):
        return True
    return False


def set_nth_bit(x: int, n: int):
    return x | 1 << n


def unset_nth_bit(x: int, n: int):
    return x & ~(1 << n)


def wrapString(string, indent, max_lines, width):
    wrapped_string = TextWrapper(
        initial_indent="",
        subsequent_indent=" " * indent,
        max_lines=max_lines,
        break_on_hyphens=True,
        break_long_words=True,
        width=width
    ).fill(str(string))

    return wrapped_string


NAMEIDS = {
    0: 'Copyright Notice',
    1: 'Family name',
    2: 'Subfamily name',
    3: 'Unique identifier',
    4: 'Full font name',
    5: 'Version string',
    6: 'PostScript name',
    7: 'Trademark',
    8: 'Manufacturer Name',
    9: 'Designer',
    10: 'Description',
    11: 'URL Vendor',
    12: 'URL Designer',
    13: 'License Description',
    14: 'License Info URL',
    15: 'Reserved',
    16: 'Typographic Family',
    17: 'Typographic Subfamily',
    18: 'Compatible Full (Mac)',
    19: 'Sample text',
    20: 'PS CID findfont name',
    21: 'WWS Family Name',
    22: 'WWS Subfamily Name',
    23: 'Light Backgr Palette',
    24: 'Dark Backgr Palette',
    25: 'Variations PSName Pref'
}

PLATFORMS = {
    0: 'Unicode',
    1: 'Macintosh',
    2: 'ISO (deprecated)',
    3: 'Windows',
    4: 'Custom',
}

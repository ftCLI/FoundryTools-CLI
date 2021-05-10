from textwrap import TextWrapper

from fontTools.misc.timeTools import timestampToString
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._n_a_m_e import (_MAC_LANGUAGE_CODES,
                                             _MAC_LANGUAGE_TO_SCRIPT,
                                             _WINDOWS_LANGUAGE_CODES)


class pyFont(object):

    def __init__(self, font):

        self.font = font

        self.isCFF = self.font.has_key('CFF ')

        if self.isCFF == True:
            self.otFont = self.font['CFF '].cff

        self.is_bold = is_nth_bit_set(self.font['head'].macStyle, 0) and is_nth_bit_set(
            self.font['OS/2'].fsSelection, 5) and not(is_nth_bit_set(self.font['OS/2'].fsSelection, 6))

        self.is_italic = is_nth_bit_set(self.font['head'].macStyle, 1) and is_nth_bit_set(
            self.font['OS/2'].fsSelection, 0) and not is_nth_bit_set(self.font['OS/2'].fsSelection, 6)

        self.usWeightClass = self.font['OS/2'].usWeightClass

        self.usWidthClass = self.font['OS/2'].usWidthClass

        try:
            self.nameTable = self.font['name']
            self.names = self.nameTable.names
        except KeyError:
            self.nameTable = self.font['name'] = newTable('name')
            # self.nameTable.names = []

    def recalcNames(
        self, font_data, italics, namerecords_to_ignore=[],
        shorten_weight=[], shorten_width=[], shorten_italic=[],
        fixCFF=False, linked_styles=[], isSuperFamily=False,
        alt_uid=False, regular_italic=False, keep_regular=False,
        old_full_font_name=False
    ):

        ita, italic = italics
        isBold = bool(int(font_data['is_bold']))
        isItalic = bool(int(font_data['is_italic']))
        usWidthClass = int(font_data['uswidthclass'])
        wdt = str(font_data['wdt'])
        width = str(font_data['width'])
        usWeightClass = int(font_data['usweightclass'])
        wgt = str(font_data['wgt'])
        weight = str(font_data['weight'])
        familyName = str(font_data['family_name'])

        self.setRegular()

        if isBold:
            self.setBold()

        if isItalic:
            self.setItalic()

        self.setUsWeightClass(usWeightClass)
        self.setUsWidthClass(usWidthClass)

        # Macintosh

        familyNameMac = familyName

        subFamilyNameMac = weight

        if width.lower() != "normal":
            if isSuperFamily is False:
                familyNameMac = "{} {}".format(familyName, width)
            else:
                subFamilyNameMac = "{} {}".format(width, weight)

        if isItalic:
            subFamilyNameMac = "{} {}".format(
                subFamilyNameMac, italic)
            if not keep_regular:
                subFamilyNameMac = subFamilyNameMac.replace(
                    'Regular Italic', 'Italic')

        # Microsoft

        familyNameWin = familyName

        familyNameWin = "{} {} {}".format(familyName, width.replace(
            "Normal", "").replace("Nor", ""), weight).replace("  ", " ").strip()

        subFamilyNameWin = "Regular"

        if len(linked_styles) == 2:
            regularWeight = linked_styles[0]
            boldWeight = linked_styles[1]

            if usWeightClass in linked_styles:
                familyNameWin = familyNameWin.replace(
                    weight, "").replace("  ", " ").strip()

            if usWeightClass == regularWeight:
                self.setRegular()
                if isItalic is True:

                    self.setItalic()

            if usWeightClass == boldWeight:

                self.setBold()

                subFamilyNameWin = "Bold"

        else:

            if self.isBold():

                self.unsetBold()

        if isItalic is True:

            subFamilyNameWin = "{} Italic".format(subFamilyNameWin).replace(

                "Regular Italic", "Italic").replace("  ", " ").strip()

        postScriptName = str(self.nameTable.getName(6, 3, 1, 0x409))

        if 6 not in namerecords_to_ignore:

            postScriptName = "{}-{}".format(

                familyNameMac, subFamilyNameMac)

            if regular_italic:

                postScriptName = postScriptName.replace(

                    "-Italic", "-RegularItalic")

            postScriptName = postScriptName.replace(

                weight, wgt) if 6 in shorten_weight else postScriptName

            postScriptName = postScriptName.replace(

                width, wdt) if 6 in shorten_width else postScriptName

            postScriptName = postScriptName.replace(

                italic, ita) if 6 in shorten_italic else postScriptName

            # Do not remove spaces and dots before, if not the -swdt, -swgt and -sita
            # switches won't work!

            postScriptName = postScriptName.replace(" ", "").replace(".", "")

        achVendID = str(
            self.font['OS/2'].achVendID).replace(" ", "").replace(r'\x00', "")

        fontRevision = str(
            round(self.font['head'].fontRevision, 3)).ljust(5, "0")

        versionString = "Version {}".format(fontRevision)

        fullFontName = "{} {}".format(familyNameMac, subFamilyNameMac)

        uniqueID = "{};{};{}".format(
            fontRevision, achVendID.ljust(4), postScriptName)

        if alt_uid:

            year_created = timestampToString(
                self.font['head'].created).split(" ")[-1]

            manufacturer = self.nameTable.getName(8, 3, 1, 0x409)

            uniqueID = "{}:{} {}:{}".format(

                manufacturer, familyNameMac, subFamilyNameMac, year_created)

        # nameID 1

        if not 1 in namerecords_to_ignore:

            string = familyNameMac

            string = string.replace(
                weight, wgt) if 1 in shorten_weight else string

            string = string.replace(
                width, wdt) if 1 in shorten_width else string

            string = string.replace(
                italic, ita) if 1 in shorten_italic else string

            self.nameTable.setName(string, 1, 1, 0, 0x0)

            string = familyNameWin

            string = string.replace(
                weight, wgt) if 1 in shorten_weight else string

            string = string.replace(
                width, wdt) if 1 in shorten_width else string

            # No need to shorten the italics here.
            # string = string.replace(
            # italic, ita) if 1 in shorten_italic else string

            self.nameTable.setName(string, 1, 3, 1, 0x409)

        # nameID 2

        if 2 not in namerecords_to_ignore:

            string = subFamilyNameMac

            string = string.replace(

                weight, wgt) if 2 in shorten_weight else string

            string = string.replace(

                width, wdt) if 2 in shorten_width else string

            string = string.replace(

                italic, ita) if 2 in shorten_italic else string

            self.nameTable.setName(string, 2, 1, 0, 0x0)

            # This can be only Regular, Italic, Bold or Bold Italic and can't be shortened!

            self.nameTable.setName(subFamilyNameWin, 2, 3, 1, 0x409)

        # nameID 3

        if 3 not in namerecords_to_ignore:

            string = uniqueID

            string = string.replace(

                weight, wgt) if 3 in shorten_weight else string

            string = string.replace(

                width, wdt) if 3 in shorten_width else string

            string = string.replace(

                italic, ita) if 3 in shorten_italic else string

            self.nameTable.setName(string, 3, 1, 0, 0x0)

            self.nameTable.setName(string, 3, 3, 1, 0x409)

        # nameID 4

        if 4 not in namerecords_to_ignore:

            string = fullFontName

            string = string.replace(

                weight, wgt) if 4 in shorten_weight else string

            string = string.replace(

                width, wdt) if 4 in shorten_width else string

            string = string.replace(

                italic, ita) if 4 in shorten_italic else string

            self.nameTable.setName(string, 4, 1, 0, 0x0)

            self.nameTable.setName(string, 4, 3, 1, 0x409)

            # No need to shorten this!

            if old_full_font_name:

                self.nameTable.setName(postScriptName, 4, 3, 1, 0x409)

        # nameID 5

        if 5 not in namerecords_to_ignore:

            self.nameTable.setName(versionString, 5, 1, 0, 0x0)

            self.nameTable.setName(versionString, 5, 3, 1, 0x409)

        # nameID6

        if 6 not in namerecords_to_ignore:

            # Alreay shortened!

            self.nameTable.setName(postScriptName, 6, 1, 0, 0x0)

            self.nameTable.setName(postScriptName, 6, 3, 1, 0x409)

        # nameID 16, 17, 18

        if 16 not in namerecords_to_ignore:

            string = familyNameMac

            string = string.replace(

                weight, wgt) if 16 in shorten_weight else string

            string = string.replace(

                width, wdt) if 16 in shorten_width else string

            string = string.replace(

                italic, ita) if 16 in shorten_italic else string

            self.nameTable.setName(string, 16, 1, 0, 0x0)

            self.nameTable.setName(string, 16, 3, 1, 0x409)

        if 17 not in namerecords_to_ignore:

            string = subFamilyNameMac

            string = string.replace(

                weight, wgt) if 17 in shorten_weight else string

            string = string.replace(

                width, wdt) if 17 in shorten_width else string

            string = string.replace(

                italic, ita) if 17 in shorten_italic else string

            self.nameTable.setName(string, 17, 1, 0, 0x0)

            self.nameTable.setName(string, 17, 3, 1, 0x409)

        if 18 not in namerecords_to_ignore:

            string = fullFontName

            string = string.replace(

                weight, wgt) if 18 in shorten_weight else string

            string = string.replace(

                width, wdt) if 18 in shorten_width else string

            string = string.replace(

                italic, ita) if 18 in shorten_italic else string

            self.nameTable.setName(string, 18, 1, 0, 0x0)

        if self.isCFF and fixCFF == True:

            self.otFont.fontNames = [postScriptName]

            self.otFont.topDictIndex[0].FullName = fullFontName

            self.otFont.topDictIndex[0].FamilyName = familyNameMac

            self.otFont.topDictIndex[0].Weight = weight

            # self.otFont.topDictIndex[0].Copyright = None

            # self.otFont.topDictIndex[0].Notice = None

    def fixCFF(self):

        postScriptName = str(self.font['name'].getName(6, 1, 0, 0x0))

        fullFontName = str(self.font['name'].getName(4, 1, 0, 0x0))

        familyName = str(self.font['name'].getName(1, 1, 0, 0x0))

        weight = str(self.font['name'].getName(

            2, 1, 0, 0x0)).replace("Italic", "").strip()

        try:

            self.otFont.fontNames = [postScriptName]

            self.otFont.topDictIndex[0].FullName = fullFontName

            self.otFont.topDictIndex[0].FamilyName = familyName

            self.otFont.topDictIndex[0].Weight = weight

        except:

            pass

    def setMultilingualName(self, nameID=None, language='en', string="", windows=True, mac=True):

        if windows is True:

            self.delMultilingualName(

                nameID, language=language, windows=True, mac=False)

        if mac is True:

            self.delMultilingualName(

                nameID, language=language, windows=False, mac=True)

        names = {language: string}

        self.nameTable.addMultilingualName(

            names, ttFont=self.font, windows=windows, mac=mac, nameID=nameID)

    def delMultilingualName(self, nameID, language='en', windows=True, mac=True):

        if nameID is not None:

            if language == 'ALL':

                windows = False

                mac = False

                for name in self.nameTable.names:

                    if name.nameID == nameID:

                        self.nameTable.removeNames(

                            name.nameID, name.platformID, name.platEncID, name.langID)

            if windows is True:

                langID = _WINDOWS_LANGUAGE_CODES.get(language.lower())

                self.nameTable.removeNames(nameID, 3, 1, langID)

            if mac is True:

                macLang = _MAC_LANGUAGE_CODES.get(language.lower())

                macScript = _MAC_LANGUAGE_TO_SCRIPT.get(macLang)

                self.nameTable.removeNames(nameID, 1, macScript, macLang)

    def findReplace(self, oldString, newString, fixCFF=False, nameID=None, platform=None):

        platforms_list = []

        if platform == 'mac':

            platforms_list.append(1)

        if platform == 'win':

            platforms_list.append(3)

        if platform is None:

            for name in self.names:

                if name.platformID not in platforms_list:

                    platforms_list.append(name.platformID)

        names_list = []

        if nameID is not None:

            for p in platforms_list:

                names_list.append([p, nameID])

        else:

            for name in self.names:

                if name.platformID in platforms_list:

                    names_list.append([name.platformID, name.nameID])

        fixCount = 0

        for name in self.names:

            if [name.platformID, name.nameID] in names_list:

                if oldString in str(name):

                    string = str(name).replace(

                        oldString, newString).replace("  ", " ").strip()

                    self.font['name'].setName(

                        string, name.nameID, name.platformID, name.platEncID, name.langID)

                    fixCount += 1

        if self.isCFF and fixCFF is True:

            try:

                fontName = str(getattr(self.otFont, 'fontNames')[0])

                fontName_new = fontName.replace(

                    oldString, newString).replace("  ", " ").strip()

                if not fontName == fontName_new:

                    fixCount += 1

                    self.otFont.fontNames = [fontName_new]

            except:

                pass

            input_object = self.otFont.topDictIndex[0]

            attr_list = ['FullName', 'FamilyName',

                         'Weight', 'Copyright', 'Notice']

            for a in attr_list:

                try:

                    old_value = str(getattr(input_object, a))

                    new_value = old_value.replace(

                        oldString, newString).replace("  ", " ").strip()

                    if not old_value == new_value:

                        fixCount += 1

                        setattr(input_object, a, new_value)

                except:

                    pass

        return fixCount

    def removeEmptyNames(self):

        for name in self.names:

            if len(str(name)) == 0:

                self.nameTable.removeNames(

                    name.nameID, name.platformID, name.platEncID, name.langID)

    def win2mac(self):

        self.removeEmptyNames()

        for name in self.names:

            if name.platformID == 3:

                string = name.toUnicode()

                try:

                    self.setMultilingualName(

                        nameID=name.nameID, language='en', string=string, windows=False, mac=True)

                except:

                    # IMPORTANT: FOR NON STANDARD LANGUAGES ENCODINGS

                    # MAYBE THERE'S A BETTER WAY?

                    self.setMultilingualName(

                        nameID=name.nameID, language='en', string=string.encode(), windows=False, mac=True)

    def isBold(self):

        return (

            is_nth_bit_set(self.font['head'].macStyle, 0)

            and is_nth_bit_set(self.font['OS/2'].fsSelection, 5)
        )

    def isItalic(self):

        return (

            is_nth_bit_set(self.font['head'].macStyle, 1)

            and is_nth_bit_set(self.font['OS/2'].fsSelection, 0)
        )

    def isOblique(self):

        return is_nth_bit_set(self.font['OS/2'].fsSelection, 9)

    def isRegular(self):

        return is_nth_bit_set(self.font['OS/2'].fsSelection, 6)

    def setBold(self):

        self.__setBoldBits()

        self.__clearRegularBit()

    def setItalic(self):

        self.__setItalicBits()

        self.__clearRegularBit()

    def setOblique(self):
        self.font['OS/2'].fsSelection = set_nth_bit(
            self.font['OS/2'].fsSelection, 9)

    def unsetBold(self):
        self.__clearBoldBits()
        if not self.isItalic():
            self.__setRegularBit()

    def unsetItalic(self):
        self.__clearItalicBits()
        if not self.isBold():
            self.__setRegularBit()

    def unsetOblique(self):
        self.font['OS/2'].fsSelection = unset_nth_bit(
            self.font['OS/2'].fsSelection, 9)

    def setRegular(self):
        self.__setRegularBit()
        self.__clearBoldBits()
        self.__clearItalicBits()

    def usesTypoMetrics(self):
        return is_nth_bit_set(self.font['OS/2'].fsSelection, 7)

    def setUseTypoMetrics(self):
        if self.font['OS/2'].version > 3:
            self.font['OS/2'].fsSelection = set_nth_bit(
                self.font['OS/2'].fsSelection, 7)

    def unsetUseTypoMetrics(self):
        self.font['OS/2'].fsSelection = unset_nth_bit(
            self.font['OS/2'].fsSelection, 7)

    def setEmbedLevel(self, value):
        if self.font['OS/2'].fsType != value:
            self.font['OS/2'].fsType = value

    def setUsWidthClass(self, value):
        if self.font["OS/2"].usWidthClass != value:
            self.font["OS/2"].usWidthClass = value

    def setUsWeightClass(self, value):
        if self.font["OS/2"].usWeightClass != value:
            self.font["OS/2"].usWeightClass = value

    def setAchVendID(self, value):
        if self.font['OS/2'].achVendID != value:
            self.font['OS/2'].achVendID = value

    def addDummyDSIG(self):
        values = dict(
            ulVersion=1,
            usFlag=0,
            usNumSigs=0,
            signatureRecords=[],
        )
        dsig = self.font['DSIG'] = newTable('DSIG')
        for k, v in values.items():
            setattr(dsig, k, v)

    def __setBoldBits(self):
        self.font['OS/2'].fsSelection = set_nth_bit(
            self.font['OS/2'].fsSelection, 5)
        self.font['head'].macStyle = set_nth_bit(self.font['head'].macStyle, 0)

    def __setItalicBits(self):
        self.font['OS/2'].fsSelection = set_nth_bit(
            self.font['OS/2'].fsSelection, 0)
        self.font['head'].macStyle = set_nth_bit(self.font['head'].macStyle, 1)

    def __setRegularBit(self):
        self.font['OS/2'].fsSelection = set_nth_bit(
            self.font['OS/2'].fsSelection, 6)

    def __clearBoldBits(self):
        self.font['OS/2'].fsSelection = unset_nth_bit(
            self.font['OS/2'].fsSelection, 5)
        self.font['head'].macStyle = unset_nth_bit(
            self.font['head'].macStyle, 0)

    def __clearItalicBits(self):
        self.font['OS/2'].fsSelection = unset_nth_bit(
            self.font['OS/2'].fsSelection, 0)
        self.font['head'].macStyle = unset_nth_bit(
            self.font['head'].macStyle, 1)

    def __clearRegularBit(self):
        self.font['OS/2'].fsSelection = unset_nth_bit(
            self.font['OS/2'].fsSelection, 6)


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

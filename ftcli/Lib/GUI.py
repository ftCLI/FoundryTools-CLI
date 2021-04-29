import os
import sys

import click
from click.termui import confirm
from fontTools.misc.fixedTools import floatToFixedToStr
from fontTools.misc.textTools import num2binary
from fontTools.misc.timeTools import timestampToString
from fontTools.ttLib import TTFont
from ftcli.Lib.configHandler import (DEFAULT_WEIGHTS, DEFAULT_WIDTHS,
                                            configHandler)
from ftcli.Lib.csvHandler import csvHandler
from ftcli.Lib.pyFont import pyFont
from ftcli.Lib.utils import (getConfigPath, getCsvPath, getFontsList,
                                    wrapString)


class GUI(object):

    def csvEditor(self, config_file, csv_file):

        data = csvHandler(csv_file).getData()
        terminal_width = click.get_terminal_size()[0] - 1

        click.clear()
        print("\nCURRENT FILE:", csv_file)
        print("-" * terminal_width)

        commands = {
            'c': 'Edit configuration file',
            'f': 'Set family name',
            'l': 'Edit single line',
            'r': 'Recalc CSV data',
            'p': 'Print names',
            'i': 'Init CSV data',
            'x': 'Exit'
        }

        if len(data) == 0:
            del commands['l']
            del commands['p']
            click.secho("{} contains no data".format(
                csv_file), fg='yellow')
        else:
            self.printCsv(csv_file)

        print('-' * terminal_width)
        print('AVAILABLE COMMANDS:')
        print('-' * terminal_width)

        choices = []
        for key, value in commands.items():
            print('{} : {}'.format(key, value))
            choices.append(key)

        message = "\nYour selection"
        choice = click.prompt(
            message, type=click.Choice(choices), show_choices=True)

        if choice == 'c':
            self.cfgEditor(config_file)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'f':
            family_name = click.prompt("\nFamily name")
            for row in data:
                row['family_name'] = family_name
            csvHandler(csv_file).writeCSV(data)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'r':
            source_string = click.prompt("\nSource string", type=click.Choice(
                choices=('fname', '1_1_2', '1_4', '1_6', '1_16_17', '1_18', '3_1_2', '3_4', '3_6', '3_16_17', 'cff_1', 'cff_2', 'cff_3')),
                default='fname', show_choices=True, show_default=True)

            confirm = click.confirm(
                '\nDo you want to continue', default=True)
            if confirm:
                csvHandler(csv_file).recalcCSV(
                    config_file=config_file, family_name=None, source_string=source_string)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'l':

            line_to_edit = click.prompt(
                "\nEnter line number", type=click.IntRange(1, len(data))) - 1
            line_data = data[line_to_edit]

            print('\nSelected file:', data[line_to_edit]['file_name'])

            is_bold = int(click.prompt(
                "\nIs bold", type=click.BOOL, default=line_data['is_bold']))
            is_italic = int(click.prompt(
                "\nIs italic", type=click.BOOL, default=line_data['is_italic']))
            uswidthclass = click.prompt("\nusWidthClass", type=click.IntRange(
                1, 9), default=line_data['uswidthclass'])
            wdt = click.prompt("\nWidth (short word)",
                               default=line_data['wdt'])
            width = click.prompt("\nWidth (long word)",
                                 default=line_data['width'])
            usweightclass = click.prompt("\nusWeightClass", type=click.IntRange(
                1, 1000), default=line_data['usweightclass'])
            wgt = click.prompt("\nWeight (short word)",
                               default=line_data['wgt'])
            weight = click.prompt("\nWeight (long word)",
                                  default=line_data['weight'])
            family_name = click.prompt(
                "\nFamily name", default=line_data['family_name'])

            data[line_to_edit]['is_bold'] = is_bold
            data[line_to_edit]['is_italic'] = is_italic
            data[line_to_edit]['uswidthclass'] = uswidthclass
            data[line_to_edit]['wdt'] = wdt
            data[line_to_edit]['width'] = width
            data[line_to_edit]['usweightclass'] = usweightclass
            data[line_to_edit]['wgt'] = wgt
            data[line_to_edit]['weight'] = weight
            data[line_to_edit]['family_name'] = family_name

            csvHandler(csv_file).writeCSV(data)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'p':
            selected_line = click.prompt(
                "\nEnter line number", type=click.IntRange(1, len(data))) - 1
            selected_filename = data[selected_line]['file_name']
            selected_file = os.path.join(os.path.split(
                csv_file)[0], selected_filename)

            click.clear()
            self.printFtNames(selected_file, minimal=True)
            print()
            click.pause()
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'i':
            confirm = click.confirm(
                '\nAll changes will be lost. Do you want to continue', default=True)
            if confirm:
                csvHandler(csv_file).resetCSV(config_file=config_file)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'x':
            sys.exit()

    def cfgEditor(self, config_file):
        terminal_width = click.get_terminal_size()[0] - 1
        config = configHandler(config_file).getConfig()

        click.clear()
        print("\nCURRENT FILE:", config_file)
        print('-' * terminal_width)
        self.printCfg(config_file)

        commands = {
            '1': 'Edit Weights',
            '2': 'Edit Widths',
            '3': 'Edit Italics',
            'r': 'Reset default values',
            'x': 'Exit'}

        print('AVAILABLE COMMANDS:')
        print('-' * terminal_width)
        choices = []
        message = "\nYour selection"
        for key, value in commands.items():
            print('{} : {}'.format(key, value))
            choices.append(key)

        commands = {}
        choice = click.prompt(
            message, type=click.Choice(choices), show_choices=True)

        # Weights editor
        if choice == '1':
            self.__dictEditor(config_file, 'weights', 'usWeightClass',
                              1, 1000, DEFAULT_WEIGHTS)

        # Widths editor
        if choice == '2':
            self.__dictEditor(config_file, 'widths',
                              'usWidthClass', 1, 9, DEFAULT_WIDTHS)

        # Italics editor
        if choice == '3':
            print('\n[ITALICS]')
            v1 = click.prompt("\nShort word", default=config['italics'][0])
            v2 = click.prompt("\nLong word", default=config['italics'][1])
            lst = [v1, v2]
            lst.sort(key=len)
            config['italics'] = lst
            configHandler(config_file).saveConfig(config)
            self.cfgEditor(config_file)

        if choice == 'r':
            confirmation_message = "\nWARNING: values will be replaced with default ones. All changes will be lost.\n\nDo you want continue?"
            confirm = click.confirm(confirmation_message, default=True)
            if confirm == True:
                configHandler(config_file).resetConfig()
            self.cfgEditor(config_file)

        # Exit GUI
        if choice == 'x':
            return

    def printCfg(self, config_file):

        terminal_width = click.get_terminal_size()[0] - 1
        config = configHandler(config_file).getConfig()

        print()
        print("[WEIGHTS]")
        print()
        for k, v in config['weights'].items():
            print(k, ':', v[0] + ',', v[1])
        print()
        print('-' * terminal_width)

        print()
        print("[WIDTHS]")
        print()
        for k, v in config['widths'].items():
            print(k, ':', v[0] + ',', v[1])
        print()
        print('-' * terminal_width)

        print()
        print('[ITALICS]')
        print()
        print("Short word :", config['italics'][0])
        print("Long word  :", config['italics'][1])
        print()
        print('-' * terminal_width)

    def printCsv(self, csv_file):

        terminal_width = click.get_terminal_size()[0] - 1
        data = csvHandler(csv_file).getData()

        count = 0

        print(
            "{:>3}".format('#'), " ",
            "{0:<37}".format('File name'), 'B ', 'I ',
            "{0:<25}".format('usWidthClass '),
            "{0:<25}".format('usWeightClass '),
            'Family name')
        print("-" * terminal_width)

        for row in data:
            count += 1
            print(
                "{:3d}".format(count), ":", "{0:<37}".format(
                    row['file_name'][0:36]),
                row['is_bold'] + ' ',
                row['is_italic'] + ' ',
                "{0:<25}".format(row['uswidthclass'] + ": " +
                                 row['wdt'] + ", " + row['width'])[0:25],
                "{0:<25}".format(row['usweightclass'] + ": " +
                                 row['wgt'] + ", " + row['weight'])[0:25],
                row['family_name']
            )

    def printFtInfo(self, input_path):

        terminal_width = click.get_terminal_size()[0] - 1
        length = 17

        files = getFontsList(input_path)

        for f in files:

            try:
                font = TTFont(f)
                print("-" * terminal_width)
                print("BASIC INFORMATIONS:")
                print("-" * terminal_width)

                print(("Flavor").ljust(length), end=" : ")
                if font.has_key('CFF '):
                    print("PostScript")
                else:
                    print("TrueType")

                print(("Glyphs number").ljust(length),
                      ":", font['maxp'].numGlyphs)
                print(("Date created").ljust(length), ":",
                      timestampToString(font['head'].created))
                print(("Date modified").ljust(length), ":",
                      timestampToString(font['head'].modified))
                print(("usWeightClass").ljust(length),
                      ":", str(font['OS/2'].usWeightClass))
                print(("usWidthClass").ljust(length),
                      ":", str(font['OS/2'].usWidthClass))
                print(("pyFont is bold").ljust(length),
                      ":", str(pyFont(font).is_bold))
                print(("pyFont is italic").ljust(length),
                      ":", str(pyFont(font).is_italic))

                embedLevel = font['OS/2'].fsType
                if embedLevel == 0:
                    string = "Everything is allowed"
                elif embedLevel == 2:
                    string = "Embedding of this font is not allowed"
                elif embedLevel == 4:
                    string = "Only printing and previewing of the document is allowed"
                elif embedLevel == 8:
                    string = "Editing of the document is allowed"
                else:
                    string = "Unknown"

                print(("Embedding").ljust(length), ":", str(
                    font['OS/2'].fsType), "(" + string + ")")

                print("-" * terminal_width)
                print("VERSION AND IDENTIFICATION")
                print("-" * terminal_width)
                print(("Version").ljust(length), ":", floatToFixedToStr(
                    font['head'].fontRevision, precisionBits=12))
                print(("Unique identifier").ljust(length), ":",
                      font['name'].getName(3, 3, 1, 0x409))
                print(("Vendor code").ljust(length),
                      ":", font['OS/2'].achVendID)

                print("-" * terminal_width)
                print("METRICS AND DIMENSIONS")
                print("-" * terminal_width)
                print(("unitsPerEm").ljust(length),
                      ":", font['head'].unitsPerEm)
                print(("pyFont BBox").ljust(length), ":", "(" + str(font['head'].xMin) + ", " + str(
                    font['head'].yMin) + ")", "(" + str(font['head'].xMax) + ", " + str(font['head'].yMax) + ")")

                print("\n[OS/2] table")
                print((" " * 4 + "TypoAscender").ljust(length),
                      ":", font['OS/2'].sTypoAscender)
                print((" " * 4 + "TypoDescender").ljust(length),
                      ":", font['OS/2'].sTypoDescender)
                print((" " * 4 + "TypoLineGap").ljust(length),
                      ":", font['OS/2'].sTypoLineGap)
                print((" " * 4 + "WinAscent").ljust(length),
                      ":", font['OS/2'].usWinAscent)
                print((" " * 4 + "WinDescent").ljust(length),
                      ":", font['OS/2'].usWinDescent)

                try:
                    print((" " * 4 + "x height").ljust(length),
                          ":", font['OS/2'].sxHeight)
                except:
                    pass

                try:
                    print((" " * 4 + "Caps height").ljust(length),
                          ":", font['OS/2'].sCapHeight)
                except:
                    pass

                try:
                    print((" " * 4 + "Subscript").ljust(length), ":",
                          "X pos = " +
                          str(font['OS/2'].ySubscriptXOffset) + ",",
                          "Y pos = " +
                          str(font['OS/2'].ySubscriptYOffset) + ",",
                          "X size = " +
                          str(font['OS/2'].ySubscriptXSize) + ",",
                          "Y size = " + str(font['OS/2'].ySubscriptYSize)
                          )
                except:
                    pass

                try:
                    print((" " * 4 + "Superscript").ljust(length), ":",
                          "X pos = " +
                          str(font['OS/2'].ySuperscriptXOffset) + ",",
                          "Y pos = " +
                          str(font['OS/2'].ySuperscriptYOffset) + ",",
                          "X size = " +
                          str(font['OS/2'].ySuperscriptXSize) + ",",
                          "Y size = " + str(font['OS/2'].ySuperscriptYSize)
                          )
                except:
                    pass

                print("\n[hhea] table")
                print((" " * 4 + "Ascent").ljust(length),
                      ":", font['hhea'].ascent)
                print((" " * 4 + "Descent").ljust(length),
                      ":", font['hhea'].descent)
                print((" " * 4 + "LineGap").ljust(length),
                      ":", font['hhea'].lineGap)

                print("\n[head] table")

                print((" " * 4 + "xMin").ljust(length), ":", font['head'].xMin)
                print((" " * 4 + "yMin").ljust(length), ":", font['head'].yMin)
                print((" " * 4 + "xMax").ljust(length), ":", font['head'].xMax)
                print((" " * 4 + "yMax").ljust(length), ":", font['head'].yMax)

                print("-" * terminal_width)
                print('FONT TABLES')
                print("-" * terminal_width)
                print(", ".join([k.strip() for k in font.keys()]))
                print("-" * terminal_width)

            except:
                click.secho('%s is not a valid font.' % f, fg='red')

    def printFtList(self, input_path):

        terminal_width = click.get_terminal_size()[0] - 1

        print("-" * terminal_width)
        print("{0:<38}".format("File Name"), "usWeightClass",
              "usWidthClass", "isBold", "isItalic")
        print("-" * terminal_width)

        usWidthClassList = []
        usWeightClassList = []

        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                filename = os.path.basename(f)
                usWeightClass = font['OS/2'].usWeightClass
                usWidthClass = font['OS/2'].usWidthClass
                isBold = pyFont(font).is_bold
                isItalic = pyFont(font).is_italic
                print("{0:<37}".format(filename)[0:36], "{:13d}".format(usWeightClass), "{:12d}".format(
                    usWidthClass), "{:6d}".format(isBold), "{0:8d}".format(isItalic))

                if not usWeightClass in usWeightClassList:
                    usWeightClassList.append(usWeightClass)
                if not usWidthClass in usWidthClassList:
                    usWidthClassList.append(usWidthClass)
            except:
                pass

        usWidthClassList.sort()
        usWeightClassList.sort()

        print("-" * terminal_width)
        print("Weights:", usWeightClassList)
        print("\nWidths:", usWidthClassList)
        print("-" * terminal_width)

    def printFtName(self, input_path, name_id, indent=32, max_lines=None):
        terminal_width = click.get_terminal_size()[0] - 1

        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                names = font['name'].names
                platform_specs = []
                for name in names:
                    platform_spec = [name.platformID,
                                     name.platEncID, name.langID]
                    if platform_spec not in platform_specs:
                        platform_specs.append(platform_spec)

                print('-' * terminal_width)
                print('FILE NAME: %s' % os.path.basename(f))
                print('-' * terminal_width)

                for platform_spec in platform_specs:
                    platformID = platform_spec[0]
                    platEncID = platform_spec[1]
                    langID = platform_spec[2]

                    for name in names:
                        if name.nameID == name_id and name.platformID == platformID and name.platEncID == platEncID and name.langID == langID:

                            string = "platform: ({}, {}, {}),  nameID{} : {}".format(
                                platformID, platEncID, langID, name.nameID, name.toUnicode())

                            string = wrapString(
                                string, indent, max_lines, terminal_width)
                            print(string)
                print()
            except:
                click.secho('%s is not a valid font.' % f, fg='red')

    def printFtNames(self, input_path, minimal=False, indent=32, max_lines=None):

        terminal_width = click.get_terminal_size()[0] - 1

        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                names = font['name'].names
                platform_specs = []
                for name in names:
                    platform_spec = [name.platformID,
                                        name.platEncID, name.langID]
                    if platform_spec not in platform_specs:
                        platform_specs.append(platform_spec)

                print('\nCURRENT FILE: %s' % f)
                print('-' * terminal_width)

                # NAME TABLE
                print('NAME TABLE')
                print('-' * terminal_width)

                for platform_spec in platform_specs:

                    platformID = platform_spec[0]
                    platEncID = platform_spec[1]
                    langID = platform_spec[2]

                    print(
                        'platformID: %s (%s) | platEncID: %s | langID: %s'
                        % (platformID, PLATFORMS.get(platformID), platEncID, langID)
                    )
                    print('-' * terminal_width)

                    for name in names:
                        if name.platformID == platformID and name.platEncID == platEncID and name.langID == langID:
                            if name.nameID in NAMEIDS:
                                string = "{:5d}".format(
                                    name.nameID) + " : " + "{0:<21}".format(NAMEIDS[name.nameID]) + " : " + name.toUnicode()
                            else:
                                string = "{:5d}".format(
                                    name.nameID) + " : " + "{0:<21}".format(name.nameID) + " : " + name.toUnicode()

                            string = wrapString(
                                string, indent, max_lines, terminal_width)
                            
                            if minimal is False:
                                print(string)
                            else:
                                if name.nameID in [1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22]:
                                    print(string)

                    print('-' * terminal_width)

                # CFF NAMES
                if font.has_key('CFF '):
                    print('CFF NAMES')
                    print('-' * terminal_width)

                    otFont = font['CFF '].cff

                    try:
                        string = "{0:<29}".format(
                            ' CFFFont name') + ' : ' + str(font['CFF '].cff.fontNames[0])
                        string = wrapString(
                            string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(
                            ' version') + ' : ' + str(otFont.topDictIndex[0].version)
                        string = wrapString(
                            string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(
                            ' Notice') + ' : ' + str(otFont.topDictIndex[0].Notice)
                        string = wrapString(
                            string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(
                            ' Copyright') + ' : ' + str(otFont.topDictIndex[0].Copyright)
                        string = wrapString(
                            string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(
                            ' FullName') + ' : ' + str(otFont.topDictIndex[0].FullName)
                        string = wrapString(
                            string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(
                            ' FamilyName') + ' : ' + str(otFont.topDictIndex[0].FamilyName)
                        string = wrapString(
                            string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(
                            ' Weight') + ' : ' + str(otFont.topDictIndex[0].Weight)
                        string = wrapString(
                            string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    print("-" * terminal_width)
            except FileNotFoundError:
                click.secho(
                    '\nFILE NOT FOUND: {}\n\nMaybe you have to update the data.csv file?'.format(f), fg='red')
            except:
                click.secho('\n{} is not a valid font.'.format(f), fg='red')

    def printTableHead(self, input_path):

        terminal_width = click.get_terminal_size()[0] - 1

        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                print('\nCURRENT FILE: %s' % f)
                print('-' * terminal_width)

                for name, value in font['head'].__dict__.items():
                    if name == 'tableTag':
                        print(name, value)
                        print("-" * terminal_width)
                        print()
                    elif name in ("created", "modified"):
                        print('    <%s value="%s"/>' %
                              (name, timestampToString(value)))
                    elif name in ("magicNumber", "checkSumAdjustment"):
                        if value < 0:
                            value = value + 0x100000000
                        value = hex(value)
                        if value[-1:] == "L":
                            value = value[:-1]
                        print('    <%s value="%s"/>' % (name, str(value)))
                    elif value in ("macStyle", "flags"):
                        print('    <%s value="%s"/>' %
                              (name, num2binary(value)))
                    else:
                        print('    <%s value="%s"/>' % (name, value))
                print()
                print("-" * terminal_width)
            except:
                click.secho('%s is not a valid font.' % f, fg='red')

    def printTableOS2(self, input_path):

        terminal_width = click.get_terminal_size()[0] - 1

        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                print('\nCURRENT FILE: %s' % f)
                print('-' * terminal_width)
                for name, value in font['OS/2'].__dict__.items():
                    if name == 'tableTag':
                        print(name, value)
                        print("-" * terminal_width)
                        print()
                    elif name == 'panose':
                        print('    <' + name + '>')
                        for panosename, value in font['OS/2'].panose.__dict__.items():
                            print('        <' + panosename +
                                  ' value="' + str(value) + '"/>')
                        print('    </' + name + '>')
                    elif name in ("ulUnicodeRange1", "ulUnicodeRange2", "ulUnicodeRange3", "ulUnicodeRange4", "ulCodePageRange1", "ulCodePageRange2"):
                        print('    <' + name + ' value="' +
                              num2binary(value) + '"/>')
                    elif name in ("fsType", "fsSelection"):
                        print('    <' + name + ' value="' +
                              num2binary(value, 16) + '"/>')
                    elif name == "achVendID":
                        print('    <' + name + ' value="' +
                              repr(value)[1:-1] + '"/>')
                    else:
                        print('    <' + name + ' value="' + str(value) + '"/>')
                print()
                print("-" * terminal_width)
            except:
                click.secho('%s is not a valid font.' % f, fg='red')

    def listTables(self, input_path):

        terminal_width = click.get_terminal_size()[0] - 1

        files = getFontsList(input_path)
        for f in files:
            try:
                font = TTFont(f)
                print('-' * terminal_width)
                print('CURRENT FILE: %s' % os.path.basename(f))
                print('-' * terminal_width)
                print(", ".join([k.strip() for k in font.keys()]))
                print()
            except:
                pass

    def __dictEditor(self, config_file, input_dict, key_name, min_key, max_key, default_dict):

        terminal_width = click.get_terminal_size()[0] - 1
        config = configHandler(config_file).getConfig()

        keys_list = []
        keys_list = [k for k in config[input_dict] if k not in keys_list]

        click.clear()
        print("CURRENT FILE:", config_file)
        print('-' * terminal_width)

        print()
        print("[%s]" % input_dict.upper())
        for k, v in config[input_dict].items():
            print('%s : %s, %s' % (k, v[0], v[1]))
        print()

        print('-' * terminal_width, '\nAVAILABLE COMMANDS:\n' + '-' * terminal_width)

        commands = {
            'a': 'Add/Edit item',
            'd': 'Delete item',
            'r': 'Reset default values',
            'x': 'Main menu'}
        message = "\nYour selection"
        choices = []
        for key, value in commands.items():
            print('[%s] : %s' % (key, value))
            choices.append(key)

        choice = click.prompt(
            message, type=click.Choice(choices), show_choices=True)

        if choice == 'a':

            print()
            k = click.prompt(key_name, type=click.IntRange(min_key, max_key))

            if str(k) in keys_list:
                old_key = k
                old_v1 = config[input_dict][str(k)][0]
                old_v2 = config[input_dict][str(k)][1]
                new_key = click.prompt("\nnew %s value" % key_name, type=click.IntRange(
                    min_key, max_key), default=old_key)
                v1 = str(click.prompt("\nShort word", type=str, default=old_v1))
                v2 = str(click.prompt("\nLong word", type=str, default=old_v2))
                del config[input_dict][str(k)]
            else:
                new_key = k
                v1 = str(click.prompt("\nShort word", type=str))
                v2 = str(click.prompt("\nLong word", type=str))

            lst = [v1, v2]
            lst.sort(key=len)
            config[input_dict][str(new_key)] = lst
            configHandler(config_file).saveConfig(config)
            self.__dictEditor(config_file, input_dict, key_name, min_key,
                              max_key, default_dict)

        if choice == 'd':

            print()
            k = click.prompt("%s value" %
                             key_name, type=click.IntRange(min_key, max_key))

            if str(k) in keys_list:
                confirmation_message = "\nDo you want continue?"
                confirm = click.confirm(confirmation_message, default=True)
                if confirm == True:
                    del config[input_dict][str(k)]
                    configHandler(config_file).saveConfig(config)
            else:
                print()
                click.pause(key_name + str(k) +
                            ' value not found. Press any key to continue')

            self.__dictEditor(config_file, input_dict, key_name, min_key,
                              max_key, default_dict)

        if choice == 'r':
            confirmation_message = "\nWARNING: values will be replaced with default ones. All changes will be lost.\n\nDo you want continue?"
            confirm = click.confirm(confirmation_message, default=True)

            if confirm == True:
                config[input_dict] = default_dict
                configHandler(config_file).saveConfig(config)

            self.__dictEditor(config_file, input_dict, key_name, min_key,
                              max_key, default_dict)

        if choice == 'x':
            self.cfgEditor(config_file)


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
    25: 'Variations PSName Pref'}

PLATFORMS = {
    0: 'Unicode',
    1: 'Macintosh',
    2: 'ISO (deprecated)',
    3: 'Windows',
    4: 'Custom'}

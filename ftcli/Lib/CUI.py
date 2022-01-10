import os
import sys
from shutil import get_terminal_size

import click
from fontTools.misc.fixedTools import floatToFixedToStr
from fontTools.misc.textTools import num2binary
from fontTools.misc.timeTools import timestampToString
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import (_MAC_LANGUAGES, _WINDOWS_LANGUAGES)

from ftcli.Lib.Font import Font
from ftcli.Lib.configHandler import (DEFAULT_WEIGHTS, DEFAULT_WIDTHS, configHandler)
from ftcli.Lib.csvHandler import csvHandler
from ftcli.Lib.utils import (getFontsList, wrapString)


# Character User Interface
class CUI(object):

    def csvEditor(self, config_file, csv_file):

        data = csvHandler(csv_file).getData()

        click.clear()

        print("\nCURRENT FILE:", csv_file, '\n')

        commands = {
            'e': 'Edit CSV lines',
            'i': 'Init CSV data',
            'r': 'Recalc CSV data',
            'c': 'Edit Config file',
            'p': 'Print font names',
            'x': 'Exit'
        }

        if len(data) == 0:
            # No data, nothing to edit or print. So we remove the commands.
            del commands['e']
            del commands['p']
            click.secho(f"{csv_file} contains no data.", fg='yellow')
        else:
            self.printCsv(csv_file)

        print('\nAVAILABLE COMMANDS:\n')

        choices = []
        for key, value in commands.items():
            print('{} : {}'.format(key, value))
            choices.append(key)

        choice = click.prompt("\nYour selection", type=click.Choice(choices), show_choices=True)

        if choice == 'c':
            self.cfgEditor(config_file)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'r':
            source_string = click.prompt("\nSource string", type=click.Choice(
                choices=('fname', '1_1_2', '1_4', '1_6', '1_16_17', '1_18', '3_1_2', '3_4', '3_6', '3_16_17', 'cff_1',
                         'cff_2')), default='fname', show_choices=True, show_default=True)

            confirm = click.confirm(
                '\nDo you want to continue', default=True)
            if confirm:
                csvHandler(csv_file).recalcCSV(
                    config_file=config_file, family_name=None, source_string=source_string)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'e':
            self.multilineEditor(csv_file=csv_file)
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
        config = configHandler(config_file).getConfig()

        click.clear()
        print("\nCURRENT FILE:", config_file, '\n')
        self.printCfg(config_file)

        commands = {
            '1': 'Edit Weights',
            '2': 'Edit Widths',
            '3': 'Edit Italics',
            '4': 'Edit Obliques',
            'r': 'Reset default values',
            'x': 'Exit'}

        print('\nAVAILABLE COMMANDS:\n')

        choices = []
        for key, value in commands.items():
            print('{} : {}'.format(key, value))
            choices.append(key)

        choice = click.prompt("\nYour selection", type=click.Choice(choices), show_choices=True)

        # Weights editor
        if choice == '1':
            self.__dictEditor(config_file, 'weights', 'usWeightClass', 1, 1000, DEFAULT_WEIGHTS)

        # Widths editor
        if choice == '2':
            self.__dictEditor(config_file, 'widths', 'usWidthClass', 1, 9, DEFAULT_WIDTHS)

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

        # Obliques editor
        if choice == '4':
            print('\n[OBLIQUES]')
            v1 = click.prompt("\nShort word", default=config['obliques'][0])
            v2 = click.prompt("\nLong word", default=config['obliques'][1])
            lst = [v1, v2]
            lst.sort(key=len)
            config['obliques'] = lst
            configHandler(config_file).saveConfig(config)
            self.cfgEditor(config_file)

        if choice == 'r':
            confirmation_message = "\nWARNING: values will be replaced with default ones. All changes will be lost." \
                                   "\n\nDo you want continue?"
            confirm = click.confirm(confirmation_message, default=True)
            if confirm is True:
                configHandler(config_file).resetConfig()
            self.cfgEditor(config_file)

        # Exit GUI
        if choice == 'x':
            return

    def multilineEditor(self, csv_file):

        data = csvHandler(csv_file).getData()

        click.clear()
        print("\nCURRENT FILE:", csv_file, '\n')
        self.printCsv(csv_file)
        print('\nAVAILABLE COMMANDS:\n')

        multiline_commands = {
            '1': 'Set Italic bits',
            '2': 'Clear Italic bits',
            '3': 'Set Oblique bits',
            '4': 'Clear Oblique bits',
            '5': 'Set usWidthClass value',
            '6': 'Set usWeightClass value',
            '7': 'Set family name',
            '8': 'Set width style names',
            '9': 'Set weight style names',
            '10': 'Set slope style names',
            '11': 'Delete lines',
            'x': 'Exit'
        }

        multiline_choices = []
        for k, v in multiline_commands.items():
            print(f'{k.rjust(2)} : {v}')
            multiline_choices.append(k)

        multiline_choice = click.prompt('\nYour selection', type=click.Choice(choices=multiline_choices))

        if not multiline_choice == 'x':
            print(f'\n{multiline_commands[multiline_choice]}')
        else:
            return

        start_line = click.prompt("\nFrom line", type=click.IntRange(1, len(data)), default=1)
        end_line = click.prompt("To line  ", type=click.IntRange(start_line, len(data)), default=len(data))

        if multiline_choice == '1':
            for line in range(start_line, end_line + 1):
                data[line - 1]['is_italic'] = 1

        if multiline_choice == '2':
            for line in range(start_line, end_line + 1):
                data[line - 1]['is_italic'] = 0

        if multiline_choice == '3':
            for line in range(start_line, end_line + 1):
                data[line - 1]['is_oblique'] = 1

        if multiline_choice == '4':
            for line in range(start_line, end_line + 1):
                data[line - 1]['is_oblique'] = 0

        if multiline_choice == '5':
            uswidthclass = click.prompt("\nusWidthClass", type=click.IntRange(1, 9))
            for line in range(start_line, end_line + 1):
                data[line - 1]['uswidthclass'] = uswidthclass

        if multiline_choice == '6':
            usweightclass = click.prompt("\nusWidthClass", type=click.IntRange(1, 1000))
            for line in range(start_line, end_line + 1):
                data[line - 1]['usweightclass'] = usweightclass

        if multiline_choice == '7':
            family_name = click.prompt("\nFamily name")
            for line in range(start_line, end_line + 1):
                data[line - 1]['family_name'] = family_name

        if multiline_choice == '8':
            wdt = click.prompt("\nWidth (short word)")
            width = click.prompt("Width (long word)")
            for line in range(start_line, end_line + 1):
                data[line - 1]['wdt'] = wdt
                data[line - 1]['width'] = width

        if multiline_choice == '9':
            wgt = click.prompt("\nWeight (short word)")
            weight = click.prompt("Weight (long word)")
            for line in range(start_line, end_line + 1):
                data[line - 1]['wgt'] = wgt
                data[line - 1]['weight'] = weight

        if multiline_choice == '10':
            slp = click.prompt("\nSlope (short word)")
            slope = click.prompt("\nSlope (long word)")
            for line in range(start_line, end_line + 1):
                data[line - 1]['slp'] = slp
                data[line - 1]['slope'] = slope

        if multiline_choice == '11':
            for line in reversed(range(start_line, end_line + 1)):
                del data[line - 1]

        confirm = click.confirm('\nSave changes', default=True)
        if confirm:
            csvHandler(csv_file).writeCSV(data)
        self.multilineEditor(csv_file=csv_file)

    def printCfg(self, config_file):

        config = configHandler(config_file).getConfig()

        max_line_len = 40  # minimum len

        for k, v in config['widths'].items():
            current_line_len = len(f'{k} : {v[0]}, {v[1]}')
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        for k, v in config['weights'].items():
            current_line_len = len(f'{k} : {v[0]}, {v[1]}')
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        for v in config['italics']:
            current_line_len = max(
                len(f'Short word : {v}'), len(f'Long word : {v}')
            )
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        for v in config['obliques']:
            current_line_len = max(len(f'Short word : {v}'), len(f'Long word : {v}'))
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        # Add the 2 spaces needed to place "|" at the beginning of the strings
        max_line_len += 2
        sep_line = '+' + '-' * max_line_len + '+'

        print(sep_line)
        print("| WEIGHTS".ljust(max_line_len, ' '), '|')
        print(sep_line)
        for k, v in config['weights'].items():
            print(f'| {k} : {v[0]}, {v[1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

        print("| WIDTHS".ljust(max_line_len, ' '), '|')
        print(sep_line)
        for k, v in config['widths'].items():
            print(f'| {k} : {v[0]}, {v[1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

        print('| ITALICS'.ljust(max_line_len, ' '), '|')
        print(sep_line)
        print(f'| Short word : {config["italics"][0]}'.ljust(max_line_len, ' '), '|')
        print(f'| Long word  : {config["italics"][1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

        print('| OBLIQUES'.ljust(max_line_len, ' '), '|')
        print(sep_line)
        print(f'| Short word : {config["obliques"][0]}'.ljust(max_line_len, ' '), '|')
        print(f'| Long word  : {config["obliques"][1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

    def printCsv(self, csv_file):

        data = csvHandler(csv_file).getData()

        # Get the maximum field len
        count = 0
        max_filename_len = 9  # length of the "File Name" string
        max_family_len = 11  # length of the "Family Name" string
        max_width_len = 5  # length of the "Width" string
        max_weight_len = 6  # length of the "Weight" string
        max_slope_len = 5  # length of the "Slope" string

        for row in data:

            count += 1

            current_filename_len = len(row['file_name'])
            if current_filename_len > max_filename_len:
                max_filename_len = current_filename_len

            current_family_len = len(f'{row["family_name"]}')
            if current_family_len > max_family_len:
                max_family_len = current_family_len

            current_width_len = len(f'{row["uswidthclass"]}: {row["wdt"]}, {row["width"]}')
            if current_width_len > max_width_len:
                max_width_len = current_width_len

            current_weight_len = len(f'{row["usweightclass"]}: {row["wgt"]}, {row["weight"]}')
            if current_weight_len > max_weight_len:
                max_weight_len = current_weight_len

            current_slope_len = len(f'{row["slp"]}, {row["slope"]}')
            if current_slope_len > max_slope_len:
                max_slope_len = current_slope_len

        count_len = len(str(count))
        max_filename_len = min(max_filename_len, 40)
        max_family_len = min(max_family_len, 30)
        max_width_len = min(max_width_len, 30)
        max_weight_len = min(max_weight_len, 30)
        max_slope_len = min(max_slope_len, 20)

        # Set the sep line
        sep_line = ('+' + '-' * (count_len + 2) + '+' +
                    '-' * (max_filename_len + 2) + '+' +
                    3 * ('-' * 3 + '+') +
                    '-' * (max_family_len + 2) + '+' +
                    '-' * (max_width_len + 2) + '+' +
                    '-' * (max_weight_len + 2) + '+' +
                    '-' * (max_slope_len + 2) + '+'
                    )

        print(sep_line)

        count = 0

        # Print the header
        print(
            '|', "#".rjust(count_len, ' '), '|',
            "File Name".ljust(max_filename_len, ' '), '|',
            'B | I | O |',
            "Family Name".ljust(max_family_len, ' '), '|',
            "Width".ljust(max_width_len, ' '), '|',
            "Weight".ljust(max_weight_len, ' '), '|',
            "Slope".ljust(max_slope_len, ' '), '|',
        )

        print(sep_line)

        # Print formatted data
        for row in data:
            count += 1
            print(
                '|', str(count).rjust(count_len, ' '), '|',
                row['file_name'].ljust(max_filename_len, ' ')[0:max_filename_len], '|',
                row['is_bold'], '|', row['is_italic'], '|', row['is_oblique'], '|',
                row['family_name'].ljust(max_family_len, ' ')[0:max_family_len], '|',
                f'{row["uswidthclass"]}: {row["wdt"]}, {row["width"]}'.ljust(max_width_len, ' ')[0:max_width_len], '|',
                f'{row["usweightclass"]}: {row["wgt"]}, {row["weight"]}'.ljust(
                    max_weight_len, ' ')[0:max_weight_len], '|',
                f'{row["slp"]}, {row["slope"]}'.ljust(
                    max_slope_len, ' ') if len(row['slope']) > 0 else ' '.ljust(max_slope_len), '|',
            )

        print(sep_line)

    def printFtInfo(self, input_path, max_lines=999):

        terminal_width = min(120, get_terminal_size()[0] - 1)
        files = getFontsList(input_path)
        length = 17

        for f in files:

            try:
                font = Font(f)

                font_info = font.getFontInfo()
                v_metrics = font.getVerticalMetrics()
                feature_tags = font.getFontFeatures()
                embed_level = font_info['embed_level']['value']
                try:
                    embed_string = EMBED_LEVELS.get(embed_level)
                except KeyError():
                    embed_string = "Unknown"

                print()
                print(f'CURRENT FILE: {f}')

                print()
                print("-" * terminal_width)
                print("  BASIC INFORMATION")
                print("-" * terminal_width)

                for v in font_info.values():
                    if v['label'] == 'Version':
                        print(f"  {v['label'].ljust(length)} : {floatToFixedToStr(v['value'], precisionBits=12)}")
                    elif v['label'] == 'Embedding':
                        print(f'  {v["label"].ljust(length)} : {v["value"]} ({embed_string})')
                    else:
                        print(f'  {v["label"].ljust(length)} : {v["value"]}')

                print()
                print("-" * terminal_width)
                print("  FONT METRICS")
                print("-" * terminal_width)

                print()
                print("  [OS/2]")
                print(f"  {'  sTypoAscender'.ljust(length)} : {v_metrics['os2_typo_ascender']}")
                print(f"  {'  sTypoDescender'.ljust(length)} : {v_metrics['os2_typo_descender']}")
                print(f"  {'  sTypoLineGap'.ljust(length)} : {v_metrics['os2_typo_linegap']}")
                print(f"  {'  usWinAscent'.ljust(length)} : {v_metrics['os2_win_ascent']}")
                print(f"  {'  usWinDescent'.ljust(length)} : {v_metrics['os2_win_descent']}")

                print()
                print("  [hhea]")
                print(f"  {'  ascent'.ljust(length)} : {v_metrics['hhea_ascent']}")
                print(f"  {'  descent'.ljust(length)} : {v_metrics['hhea_descent']}")
                print(f"  {'  lineGap'.ljust(length)} : {v_metrics['hhea_linegap']}")

                print()
                print("  [head]")
                print(f"  {'  unitsPerEm'.ljust(length)} : {v_metrics['head_units_per_em']}")
                print(f"  {'  xMin'.ljust(length)} : {v_metrics['head_x_min']}")
                print(f"  {'  yMin'.ljust(length)} : {v_metrics['head_y_min']}")
                print(f"  {'  xMax'.ljust(length)} : {v_metrics['head_x_max']}")
                print(f"  {'  yMax'.ljust(length)} : {v_metrics['head_y_max']}")
                print(f"  {'  Font BBox'.ljust(length)} : "
                      f"({v_metrics['head_x_min']}, {v_metrics['head_y_min']}) "
                      f"({v_metrics['head_x_max']}, {v_metrics['head_y_max']})"
                      )

                print()
                print("-" * terminal_width)
                print(f'  FONT TABLES: {len(font.keys())}')
                print("-" * terminal_width)
                print(wrapString(", ".join([k.strip() for k in font.keys()]),
                                 initial_indent=2, indent=2, max_lines=max_lines, width=terminal_width))

                if len(feature_tags) > 0:
                    print()
                    print("-" * terminal_width)
                    print(f'  FONT FEATURES: {len(feature_tags)}')
                    print("-" * terminal_width)
                    print(wrapString(', '.join(feature_tags), initial_indent=2, indent=2, max_lines=max_lines,
                                     width=terminal_width))

                print("-" * terminal_width)

            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def printFtList(self, input_path):

        files = getFontsList(input_path)

        max_filename_len = 9  # length of the string "File Name"

        for f in files:
            current_filename_len = len(os.path.basename(f))
            if current_filename_len > max_filename_len:
                max_filename_len = current_filename_len

        max_filename_len = min(max_filename_len, 60)  # Limit the printed file name string to 60 characters

        sep_line = '+' + '-' * (max_filename_len + 2) + '+' + '-' * 14 + '+' + '-' * 15 + '+' + '-' * 8 + '+' + \
                   '-' * 10 + '+' + '-' * 11 + '+'

        print(sep_line)
        print('|', 'File Name'.ljust(max_filename_len, ' '),
              '|', 'usWidthClass', '|', 'usWeightClass', '|', 'isBold', '|', 'isItalic', '|', 'isOblique', '|')
        print(sep_line)

        usWidthClassList = []
        usWeightClassList = []

        for f in files:
            try:
                font = Font(f, recalcTimestamp=False)
                filename = os.path.basename(f)
                usWeightClass = font['OS/2'].usWeightClass
                usWidthClass = font['OS/2'].usWidthClass
                isBold = font.isBold()
                isItalic = font.isItalic()
                isOblique = font.isOblique()
                print('|', filename.ljust(max_filename_len, ' ')[0:max_filename_len], '|',
                      str(usWidthClass).rjust(12), '|',
                      str(usWeightClass).rjust(13), '|',
                      str(int(isBold)).rjust(6), '|',
                      str(int(isItalic)).rjust(8), '|',
                      str(int(isOblique)).rjust(9), '|',
                      )

                if usWeightClass not in usWeightClassList:
                    usWeightClassList.append(usWeightClass)
                if usWidthClass not in usWidthClassList:
                    usWidthClassList.append(usWidthClass)
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

        usWidthClassList.sort()
        usWeightClassList.sort()
        print(sep_line)

        print()
        print(" Widths  :", str(usWidthClassList)[1:-1])
        print(" Weights :", str(usWeightClassList)[1:-1])

    def printFtName(self, input_path, name_id, indent=32, max_lines=None):

        terminal_width = min(90, get_terminal_size()[0] - 1)

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
                print('FILE NAME: {}'.format(os.path.basename(f)))
                print('-' * terminal_width)

                for platform_spec in platform_specs:
                    platformID = platform_spec[0]
                    platEncID = platform_spec[1]
                    langID = platform_spec[2]

                    for name in names:
                        if name.nameID == name_id and name.platformID == platformID and name.platEncID == platEncID \
                                and name.langID == langID:
                            string = "platform: ({}, {}, {}),  nameID{} : {}".format(
                                platformID, platEncID, langID, name.nameID, name.toUnicode())

                            string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                                width=terminal_width)
                            print(string)
                print()
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def printFtNames(self, input_path, minimal=False, indent=32, max_lines=None):

        terminal_width = min(120, get_terminal_size()[0] - 1)

        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                names = font['name'].names
                platform_specs = []
                for name in names:
                    platform_spec = [name.platformID, name.platEncID, name.langID]
                    if platform_spec not in platform_specs:
                        platform_specs.append(platform_spec)

                print(f'\nCURRENT FILE: {f}\n')
                print('-' * terminal_width)

                # NAME TABLE
                print(' NAME TABLE')
                print('-' * terminal_width)

                for platform_spec in platform_specs:

                    platformID = platform_spec[0]
                    platEncID = platform_spec[1]
                    langID = platform_spec[2]
                    langName = ""
                    platformEncoding = ""
                    if platformID == 3:
                        langName = _WINDOWS_LANGUAGES.get(langID)
                        platformEncoding = WINDOWS_ENCODING_IDS.get(platEncID)
                    if platformID == 1:
                        langName = _MAC_LANGUAGES.get(langID)
                        platformEncoding = MAC_ENCODING_IDS.get(platEncID)

                    print(
                        f' platformID: {platformID} ({PLATFORMS.get(platformID)}) | '
                        f'platEncID: {platEncID} ({platformEncoding}) | '
                        f'langID: {langID} ({langName})')
                    print('-' * terminal_width)

                    for name in names:
                        try:
                            if name.platformID == platformID and name.platEncID == platEncID and name.langID == langID:
                                if name.nameID in NAMEIDS:
                                    string = "{:5d}".format(
                                        name.nameID) + " : " + "{0:<21}".format(
                                        NAMEIDS[name.nameID]) + " : " + name.toUnicode()
                                else:
                                    string = "{:5d}".format(
                                        name.nameID) + " : " + "{0:<21}".format(name.nameID) + " : " + name.toUnicode()

                                string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                                    width=terminal_width)

                                if minimal is False:
                                    print(string)
                                else:
                                    if name.nameID in [1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22]:
                                        print(string)
                        except Exception as e:
                            click.secho('nameID {} ERROR: {}'.format(name.nameID, e), fg='red')

                    print('-' * terminal_width)

                # CFF NAMES
                if 'CFF ' in font:
                    print(' CFF NAMES')
                    print('-' * terminal_width)

                    otFont = font['CFF '].cff

                    try:
                        string = "{0:<29}".format(' CFFFont name') + ' : ' + str(font['CFF '].cff.fontNames[0])
                        string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                            width=terminal_width)
                        print(string)
                    except:
                        pass

                    if minimal is False:
                        try:
                            string = "{0:<29}".format(' version') + ' : ' + str(otFont.topDictIndex[0].version)
                            string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                                width=terminal_width)
                            print(string)
                        except:
                            pass

                        try:
                            string = "{0:<29}".format(' Notice') + ' : ' + str(otFont.topDictIndex[0].Notice)
                            string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                                width=terminal_width)
                            print(string)
                        except:
                            pass

                        try:
                            string = "{0:<29}".format(' Copyright') + ' : ' + str(otFont.topDictIndex[0].Copyright)
                            string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                                width=terminal_width)
                            print(string)
                        except:
                            pass

                    try:
                        string = "{0:<29}".format(' FullName') + ' : ' + str(otFont.topDictIndex[0].FullName)
                        string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                            width=terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(' FamilyName') + ' : ' + str(otFont.topDictIndex[0].FamilyName)
                        string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                            width=terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(' Weight') + ' : ' + str(otFont.topDictIndex[0].Weight)
                        string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                            width=terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(' UniqueID') + ' : ' + str(otFont.topDictIndex[0].UniqueID)
                        string = wrapString(string=string, initial_indent=0, indent=indent, max_lines=max_lines,
                                            width=terminal_width)
                        print(string)
                    except:
                        pass

                    print("-" * terminal_width)
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def printTableHead(self, input_path):

        terminal_width = get_terminal_size()[0] - 1
        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                print('\nCURRENT FILE: {}'.format(f))
                print('-' * terminal_width)

                for name, value in font['head'].__dict__.items():
                    if name == 'tableTag':
                        print(name, value)
                        print("-" * terminal_width)
                        print()
                    elif name in ("created", "modified"):
                        print('    <{} value="{}"/>'.format(name, timestampToString(value)))
                    elif name in ("magicNumber", "checkSumAdjustment"):
                        if value < 0:
                            value = value + 0x100000000
                        value = hex(value)
                        if value[-1:] == "L":
                            value = value[:-1]
                        print('    <{} value="{}"/>'.format(name, str(value)))
                    elif value in ("macStyle", "flags"):
                        print('    <{} value="{}"/>'.format(name, num2binary(value)))
                    else:
                        print('    <{} value="{}"/>'.format(name, value))
                print()
                print("-" * terminal_width)
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def printTableOS2(self, input_path):

        terminal_width = get_terminal_size()[0] - 1
        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                print('\nCURRENT FILE: {}'.format(f))
                print('-' * terminal_width)
                for name, value in font['OS/2'].__dict__.items():
                    if name == 'tableTag':
                        print(name, value)
                        print("-" * terminal_width)
                        print()
                    elif name == 'panose':
                        print('    <' + name + '>')
                        for panosename, v in font['OS/2'].panose.__dict__.items():
                            print('        <' + panosename + ' value="' + str(v) + '"/>')
                        print('    </' + name + '>')
                    elif name in ("ulUnicodeRange1", "ulUnicodeRange2", "ulUnicodeRange3", "ulUnicodeRange4",
                                  "ulCodePageRange1", "ulCodePageRange2"):
                        print('    <' + name + ' value="' + num2binary(value) + '"/>')
                    elif name in ("fsType", "fsSelection"):
                        print('    <' + name + ' value="' + num2binary(value, 16) + '"/>')
                    elif name == "achVendID":
                        print('    <' + name + ' value="' + repr(value)[1:-1] + '"/>')
                    else:
                        print('    <' + name + ' value="' + str(value) + '"/>')
                print()
                print("-" * terminal_width)
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def listTables(self, input_path):

        terminal_width = get_terminal_size()[0] - 1
        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                print('-' * terminal_width)
                print('CURRENT FILE: {}'.format(os.path.basename(f)))
                print('-' * terminal_width)
                print(", ".join([k.strip() for k in font.keys()]))
                print()
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def __dictEditor(self, config_file, input_dict, key_name, min_key, max_key, default_dict):

        config = configHandler(config_file).getConfig()

        max_line_len = 40
        for k, v in config[input_dict].items():
            current_line_len = len(f'{k} : {v[0]}, {v[1]}')
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        max_line_len += 2

        sep_line = ('+' + '-' * max_line_len + '+')

        keys_list = []
        keys_list = [k for k in config[input_dict] if k not in keys_list]

        click.clear()
        print("\nCURRENT FILE:", config_file, "\n")
        print(sep_line)
        print(f'| {input_dict.upper()}'.ljust(max_line_len, ' '), '|')
        print(sep_line)
        for k, v in config[input_dict].items():
            print(f'| {k} : {v[0]}, {v[1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

        print('\nAVAILABLE COMMANDS:\n')

        commands = {
            'a': 'Add/Edit item',
            'd': 'Delete item',
            'r': 'Reset default values',
            'x': 'Main menu'
        }

        choices = []
        for key, value in commands.items():
            print('[{}] : {}'.format(key, value))
            choices.append(key)

        choice = click.prompt("\nYour selection", type=click.Choice(choices), show_choices=True)

        if choice == 'a':

            print()
            k = click.prompt(key_name, type=click.IntRange(min_key, max_key))

            if str(k) in keys_list:
                old_key = k
                old_v1 = config[input_dict][str(k)][0]
                old_v2 = config[input_dict][str(k)][1]
                new_key = click.prompt("\nnew {} value".format(key_name), type=click.IntRange(min_key, max_key),
                                       default=old_key)
                v1 = str(click.prompt("\nShort word", default=old_v1))
                v2 = str(click.prompt("\nLong word", default=old_v2))
                del config[input_dict][str(k)]
            else:
                new_key = k
                v1 = str(click.prompt("\nShort word"))
                v2 = str(click.prompt("\nLong word"))

            lst = [v1, v2]
            lst.sort(key=len)
            config[input_dict][str(new_key)] = lst
            configHandler(config_file).saveConfig(config)
            self.__dictEditor(config_file, input_dict, key_name, min_key,
                              max_key, default_dict)

        if choice == 'd':

            print()
            k = click.prompt("{} value".format(key_name), type=click.IntRange(min_key, max_key))

            if str(k) in keys_list:
                confirmation_message = "\nDo you want continue?"
                confirm = click.confirm(confirmation_message, default=True)
                if confirm is True:
                    del config[input_dict][str(k)]
                    configHandler(config_file).saveConfig(config)
            else:
                print()
                click.pause(key_name + str(k) +
                            ' value not found. Press any key to continue')

            self.__dictEditor(config_file, input_dict, key_name, min_key,
                              max_key, default_dict)

        if choice == 'r':
            confirmation_message = "\nWARNING: values will be replaced with default ones. All changes will be lost." \
                                   "\n\nDo you want continue?"
            confirm = click.confirm(confirmation_message, default=True)

            if confirm is True:
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

MAC_ENCODING_IDS = {
    0: 'Roman',
    1: 'Japanese',
    2: 'Chinese (Traditional)',
    3: 'Korean',
    4: 'Arabic',
    5: 'Hebrew',
    6: 'Greek',
    7: 'Russian',
    8: 'RSymbol',
    9: 'Devanagari',
    10: 'Gurmukhi',
    11: 'Gujarati',
    12: 'Oriya',
    13: 'Bengali',
    14: 'Tamil',
    15: 'Telugu',
    16: 'Kannada',
    17: 'Malayalam',
    18: 'Sinhalese',
    19: 'Burmese',
    20: 'Khmer',
    21: 'Thai',
    22: 'Laotian',
    23: 'Georgian',
    24: 'Armenian',
    25: 'Chinese (Simplified)',
    26: 'Tibetan',
    27: 'Mongolian',
    28: 'Geez',
    29: 'Slavic',
    30: 'Vietnamese',
    31: 'Sindhi',
    32: 'Uninterpreted',
}

WINDOWS_ENCODING_IDS = {
    0: 'Symbol',
    1: 'Unicode',
    2: 'ShiftJIS',
    3: 'PRC',
    4: 'Big5',
    5: 'Wansung',
    6: 'Johab',
    7: 'Reserved',
    8: 'Reserved',
    9: 'Reserved',
    10: 'UCS4',
}

EMBED_LEVELS = {
    0: 'Installable embedding',
    2: 'Restricted License embedding',
    4: 'Preview & Print embedding',
    8: 'Editable embedding'
}

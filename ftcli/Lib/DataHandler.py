import json
import os
import sys

from ftcli.Lib.Font import Font
from ftcli.Lib.configHandler import configHandler
from ftcli.Lib.utils import (getFontsList, getSourceString, guessFamilyName)


class DataHandler(object):

    def __init__(self, fonts_json):
        self.fonts_json = fonts_json
        if not os.path.exists(self.fonts_json):
            with open(self.fonts_json, 'w') as f:
                json.dump({}, f)

    def parseJSON(self):
        try:
            with open(self.fonts_json) as f:
                json_data = json.load(f)
            return json_data
        except Exception as e:
            print(f'\n{__name__}: an error occurred while parsing: {e}')
            sys.exit()

    def resetFontsDatabase(self, config_file):

        files = getFontsList(os.path.dirname(self.fonts_json))
        config = configHandler(config_file).getConfig()
        json_data = {}

        for f in files:
            file_name = os.path.basename(f)
            json_data[file_name] = {'current-data': {}}
            font = Font(f)
            family_name = guessFamilyName(font)

            try:
                wdt, width = config['widths'][str(font['OS/2'].usWidthClass)]
            except KeyError:
                wdt, width = [str(font['OS/2'].usWidthClass), str(font['OS/2'].usWidthClass)]

            try:
                wgt, weight = config['weights'][str(font['OS/2'].usWeightClass)]
            except KeyError:
                wgt, weight = [str(font['OS/2'].usWeightClass), str(font['OS/2'].usWeightClass)]

            slp = slope = None

            # If the font is italic and oblique at the same time, the oblique slopes will be used.
            if font.isItalic():
                slp, slope = config['italics'][0], config['italics'][1]
            if font.isOblique():
                slp, slope = config['obliques'][0], config['obliques'][1]

            current_names = {'family_name': family_name, 'wdt': wdt, 'width': width, 'wgt': wgt, 'weight': weight,
                             'slp': slp, 'slope': slope}

            current_attributes = {'is_bold': font.isBold(), 'is_italic': font.isItalic(),
                                  'is_oblique': font.isOblique(), 'uswidthclass': font['OS/2'].usWidthClass,
                                  'usweightclass': font['OS/2'].usWeightClass}

            json_data[file_name] = {'attributes': current_attributes, 'names': current_names}

        with open(self.fonts_json, 'w') as f:
            json.dump(json_data, f, indent=4)

    def recalcFontsDatabase(self, config_file, family_name=None, source_string='fname'):

        files = getFontsList(os.path.dirname(self.fonts_json))
        config = configHandler(config_file).getConfig()
        json_data = self.parseJSON()
        if json_data == {}:
            self.resetFontsDatabase(config_file=config_file)

        # Read the configuration file
        weights = config['weights']
        widths = config['widths']
        italics = config['italics']
        obliques = config['obliques']

        # Build a list of the literals of all widths in the configuration file.
        widthsList = []
        for values in widths.values():
            for value in values:
                widthsList.append(value)

        # Build a list of the literals of all weights in the configuration file.
        weightsList = []
        for values in weights.values():
            for value in values:
                weightsList.append(value)

        # Build a list with all style names.
        all_style_names = []
        all_style_names.extend(widthsList)
        all_style_names.extend(weightsList)
        all_style_names.extend(italics)
        all_style_names.extend(obliques)
        all_style_names.sort(key=len, reverse=True)

        for f in files:
            file_name = os.path.basename(f)
            font = Font(f)

            # Get the source string
            string = getSourceString(f, source_string)

            # Remove dashes, underscores and spaces from the string
            string = string.lower().replace("-", "").replace("_", "").replace(" ", "")

            # Build the dictionary with the current values

            # In case the family name isn't passed as parameter, we use the one stored in the JSON
            if family_name is None:
                new_family_name = json_data[file_name]['names']['family_name']
            else:
                new_family_name = family_name

            # Remove the family name from the string
            style_name = string.replace(new_family_name.lower().replace(
                ' ', '').replace('-', '').replace('_', '').replace(' ', ''), '')

            # Once removed the family name, the remaining string should be == style name (width/weight/slope)
            weight_string = width_string = italic_string = oblique_string = style_name

            # We remove all the widths and italics literals from the string, and what remains should be == the weight
            # literal (long or short has no importance).
            # If the obtained string is == to one of the weight literals, the corresponding key will be the new
            # usWeightClass. Otherwise usWeightClass is read from current font values.

            remove_list = []
            remove_list.extend(all_style_names)
            for v in weightsList:
                remove_list.remove(v)

            weight_string = self.__replaceListItems(
                input_string=weight_string, remove_list=remove_list, keep_list=weightsList)

            try:
                new_usWeightClass = int(self.__getKeyFromValue(weights, weight_string))
            except:
                new_usWeightClass = font['OS/2'].usWeightClass

            # At this point we retrieve the long and short weight literals.
            try:
                new_wgt = weights[str(new_usWeightClass)][0]
            except KeyError:
                new_wgt = str(new_usWeightClass)

            try:
                new_weight = weights[str(new_usWeightClass)][1]
            except KeyError:
                new_weight = str(new_usWeightClass)

            # Same for widths

            remove_list = []
            remove_list.extend(all_style_names)
            for v in widthsList:
                remove_list.remove(v)

            width_string = width_string.replace(weight_string, '')

            width_string = self.__replaceListItems(
                input_string=width_string, remove_list=remove_list, keep_list=widthsList)

            try:
                new_usWidthClass = int(self.__getKeyFromValue(widths, width_string))
            except:
                new_usWidthClass = font['OS/2'].usWidthClass

            try:
                new_wdt = widths[str(new_usWidthClass)][0]
            except KeyError:
                new_wdt = str(new_usWidthClass)

            try:
                new_width = widths[str(new_usWidthClass)][1]
            except KeyError:
                new_width = str(new_usWidthClass)

            # We do not recalculate this because the bold bit will be set only if linked_styles is active while fixing
            # fonts.

            new_isBold = font.isBold()

            # Recalculate italic bits

            remove_list = []
            remove_list.extend(all_style_names)
            for v in italics:
                remove_list.remove(v)

            italic_string = self.__replaceListItems(
                input_string=italic_string, remove_list=remove_list, keep_list=italics)

            if italic_string.lower() == italics[0].lower() or italic_string == italics[1].lower():
                new_isItalic = True
            else:
                new_isItalic = font.isItalic()

            # Recalculate oblique bit

            remove_list = []
            remove_list.extend(weightsList)
            remove_list.extend(widthsList)
            remove_list.extend(italics)
            remove_list.sort(key=len, reverse=True)

            oblique_string = self.__replaceListItems(
                input_string=oblique_string, remove_list=remove_list, keep_list=obliques)

            # By default, if a font is oblique, we also set it as italic. To change this behaviour, use the
            # -obni / --oblique-not-italic switch in recalc-names
            if oblique_string.lower() == obliques[0].lower() or oblique_string == obliques[1].lower():
                new_isOblique = True
                new_isItalic = True
            else:
                new_isOblique = font.isOblique()

            # Recalculate slope style names

            italics.sort(key=len)
            obliques.sort(key=len)

            new_slp = new_slope = None
            if new_isItalic == 1:
                new_slp, new_slope = italics[0], italics[1]
            if new_isOblique == 1:
                new_slp, new_slope = obliques[0], obliques[1]

            # Initialize the recalculated dictionary.
            recalculated_data = {
                'attributes': {
                    'is_bold': new_isBold,
                    'is_italic': new_isItalic,
                    'is_oblique': new_isOblique,
                    'uswidthclass': new_usWidthClass,
                    'usweightclass': new_usWeightClass,
                },
                'names': {
                    'family_name': new_family_name,
                    'wdt': new_wdt,
                    'width': new_width,
                    'wgt': new_wgt,
                    'weight': new_weight,
                    'slp': new_slp,
                    'slope': new_slope
                }
            }

            json_data[file_name] = recalculated_data

        with open(self.fonts_json, 'w') as f:
            json.dump(json_data, f, indent=4)

    @staticmethod
    def __replaceListItems(input_string, remove_list, keep_list):
        for word in remove_list:
            if word not in keep_list:
                input_string = input_string.lower().replace(word.lower().replace(' ', ''), '')
                for k in keep_list:
                    if word.lower() in k.lower():
                        if len(input_string) > 0:
                            input_string = input_string.lower().replace(k.lower().replace(word.lower(), ''), k)
        return input_string

    @staticmethod
    def __getKeyFromValue(d, s):
        for key, values in d.items():
            for v in values:
                if s.lower().replace(" ", "") == v.lower().replace(" ", ""):
                    return key

import csv
import os

from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.configHandler import configHandler
from ftcli.Lib.utils import (getFontsList, getSourceString, guessFamilyName)


class csvHandler(object):

    def __init__(self, csv_file):
        self.csv_file = csv_file

    def getData(self):
        with open(self.csv_file, 'r') as f:
            data = [row for row in csv.DictReader(f, delimiter=";")]
        return data

    def recalcCSV(self, config_file, family_name=None, source_string='fname'):
        # Recalculates each line in the CSV file comparing a string with the
        # values in the JSON config file.

        files = getFontsList(os.path.dirname(self.csv_file))
        config = configHandler(config_file).getConfig()
        current_csv_data = csvHandler(self.csv_file).getData()
        new_csv_data = []

        for f in files:
            font = TTFontCLI(f, recalcTimestamp=False)
            file_name = os.path.basename(f)

            # Get the source string
            string = getSourceString(f, source_string)

            # Remove dashes, underscores and spaces from the string
            string = string.lower().replace("-", "").replace("_", "").replace(" ", "")

            weights = config['weights']
            widths = config['widths']
            italics = config['italics']
            obliques = config['obliques']

            try:
                wgt, weight = weights[str(font['OS/2'].usWeightClass)]
            except KeyError:
                wgt, weight = [font['OS/2'].usWeightClass, font['OS/2'].usWeightClass]

            try:
                wdt, width = widths[str(font['OS/2'].usWidthClass)]
            except KeyError:
                wdt, width = [font['OS/2'].usWidthClass, font['OS/2'].usWidthClass]

            italics.sort(key=len)
            obliques.sort(key=len)

            slp = slope = None
            if font.isItalic() is True:
                slp, slope = italics[0], italics[1]
            if font.isOblique() is True:
                slp, slope = obliques[0], obliques[1]

            # Build the dictionary with the current values

            new_family_name = ""
            if family_name is None:
                for row in current_csv_data:
                    if row['file_name'] == file_name:
                        new_family_name = row['family_name']
            else:
                new_family_name = family_name

            this_font_data = {
                'file_name': file_name,
                'family_name': new_family_name,
                'is_bold': int(font.isBold()),
                'is_italic': int(font.isItalic()),
                'is_oblique': int(font.isOblique()),
                'uswidthclass': int(font['OS/2'].usWidthClass),
                'wdt': str(wdt),
                'width': str(width),
                'usweightclass': int(font['OS/2'].usWeightClass),
                'wgt': str(wgt),
                'weight': str(weight),
                'slp': str(slp),
                'slope': str(slope)
            }

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

            # Sort by reverse length the lists to ensure that long literals are processed
            # before the short ones.
            widthsList.sort(key=len, reverse=True)
            weightsList.sort(key=len, reverse=True)
            italics.sort(key=len, reverse=True)
            obliques.sort(key=len, reverse=True)

            # Remove the family name from the string
            style_name = string.replace(new_family_name.lower().replace(
                ' ', ''), '').replace('-', '').replace('_', '').replace(' ', '')

            # Once removed the family name, the remaining string should be == style name (width/weight/slope)
            weight_string = width_string = italic_string = oblique_string = style_name

            # We remove all the widths and italics literals from the string, and what remains should be == the weight
            # literal (long or short has no importance).
            # If the obtained string is == to one of the weight literals, the corresponding key will be the new
            # usWeightClass. Otherwise usWeightClass is read from current font values.

            remove_list = []
            remove_list.extend(widthsList)
            remove_list.extend(italics)
            remove_list.extend(obliques)
            remove_list.sort(key=len, reverse=True)

            weight_string = self.__replaceListItems(
                input_string=weight_string, remove_list=remove_list, keep_list=weightsList)

            if self.__getKeyFromValue(weights, weight_string) is not None:
                new_usWeightClass = self.__getKeyFromValue(weights, weight_string)
            else:
                new_usWeightClass = this_font_data['usweightclass']

            # At this point we retrieve the long and short weight literals.
            try:
                new_wgt = weights[new_usWeightClass][0]
            except KeyError:
                new_wgt = this_font_data['wgt']

            try:
                new_weight = weights[new_usWeightClass][1]
            except KeyError:
                new_weight = this_font_data['weight']

            # Same for widths

            remove_list = []
            remove_list.extend(weightsList)
            remove_list.extend(italics)
            remove_list.extend(obliques)
            remove_list.sort(key=len, reverse=True)

            width_string = width_string.replace(weight_string, '')

            width_string = self.__replaceListItems(
                input_string=width_string, remove_list=remove_list, keep_list=widthsList)

            if self.__getKeyFromValue(widths, width_string) is not None:
                new_usWidthClass = self.__getKeyFromValue(widths, width_string)
            else:
                new_usWidthClass = this_font_data['uswidthclass']

            try:
                new_wdt = widths[new_usWidthClass][0]
            except KeyError:
                new_wdt = this_font_data['wdt']

            try:
                new_width = widths[new_usWidthClass][1]
            except KeyError:
                new_width = this_font_data['width']

            # We ignore this because the bold bit will be set only if linked_styles is active while fixing fonts.
            new_isBold = this_font_data['is_bold']

            # Recalculate italic bits

            remove_list = []
            remove_list.extend(weightsList)
            remove_list.extend(widthsList)
            remove_list.extend(obliques)
            remove_list.sort(key=len, reverse=True)

            italic_string = self.__replaceListItems(
                input_string=italic_string, remove_list=remove_list, keep_list=italics)

            if italic_string == italics[0].lower() or italic_string == italics[1].lower():
                new_isItalic = 1
            else:
                new_isItalic = 0

            # Recalculate oblique bit

            remove_list = []
            remove_list.extend(weightsList)
            remove_list.extend(widthsList)
            remove_list.extend(italics)
            remove_list.sort(key=len, reverse=True)

            oblique_string = self.__replaceListItems(
                input_string=oblique_string, remove_list=remove_list, keep_list=obliques)

            # By default, if a font is oblique, we also set it as italic. To change this behaviour, use the
            # -ob / --oblique-not-italic switch in recalc-names
            if oblique_string == obliques[0].lower() or oblique_string == obliques[1].lower():
                new_isOblique = 1
                new_isItalic = 1
            else:
                new_isOblique = 0

            # Recalculate slope style names

            italics.sort(key=len)
            obliques.sort(key=len)

            new_slp = new_slope = None
            if new_isItalic == 1:
                new_slp, new_slope = italics[0], italics[1]
            if new_isOblique == 1:
                new_slp, new_slope = obliques[0], obliques[1]

            # Initialize the recalculated dictionary.
            new_font_data = {'file_name': file_name, 'family_name': new_family_name, 'is_bold': new_isBold,
                             'is_italic': new_isItalic, 'is_oblique': new_isOblique, 'uswidthclass': new_usWidthClass,
                             'wdt': new_wdt, 'width': new_width, 'usweightclass': new_usWeightClass, 'wgt': new_wgt,
                             'weight': new_weight, 'slp': new_slp, 'slope': new_slope}

            new_csv_data.append(new_font_data)

        self.writeCSV(new_csv_data)

    def resetCSV(self, config_file):

        files = getFontsList(os.path.dirname(self.csv_file))
        config = configHandler(config_file).getConfig()
        csv_data = []

        for f in files:

            this_font_filename = os.path.basename(f)
            font = TTFontCLI(f, recalcTimestamp=False)
            is_bold = int(font.isBold())
            is_italic = int(font.isItalic())
            is_oblique = int(font.isOblique())
            usWidthClass = int(font['OS/2'].usWidthClass)
            usWeightClass = int(font['OS/2'].usWeightClass)

            try:
                wgt, weight = config['weights'][str(font['OS/2'].usWeightClass)]
            except KeyError:
                wgt, weight = [font['OS/2'].usWeightClass, font['OS/2'].usWeightClass]

            try:
                wdt, width = config['widths'][str(font['OS/2'].usWidthClass)]
            except KeyError:
                wdt, width = [font['OS/2'].usWidthClass, font['OS/2'].usWidthClass]

            slp = slope = None

            # If the font is italic and also oblique, the oblique slope will be used.
            if is_italic == 1:
                slp, slope = config['italics'][0], config['italics'][1]
            if is_oblique == 1:
                slp, slope = config['obliques'][0], config['obliques'][1]

            family_name = guessFamilyName(font)

            this_font_data = {
                'file_name': this_font_filename,
                'family_name': family_name,
                'is_bold': is_bold,
                'is_italic': is_italic,
                'is_oblique': is_oblique,
                'uswidthclass': usWidthClass,
                'wdt': wdt,
                'width': width,
                'usweightclass': usWeightClass,
                'wgt': wgt,
                'weight': weight,
                'slp': slp,
                'slope': slope
            }

            csv_data.append(this_font_data)

        self.writeCSV(csv_data)

    def writeCSV(self, data):

        header = ('file_name', 'family_name', 'is_bold', 'is_italic', 'is_oblique', 'uswidthclass', 'wdt', 'width',
                  'usweightclass', 'wgt', 'weight', 'slp', 'slope')
        with open(self.csv_file, 'w', newline="") as csv_file:
            writer = csv.DictWriter(csv_file, delimiter=";", fieldnames=header)
            writer.writeheader()
            writer.writerows(data)

    def __replaceListItems(self, input_string, remove_list, keep_list):
        for word in remove_list:
            if word not in keep_list:
                input_string = input_string.lower().replace(word.lower().replace(' ', ''), '')
        return input_string

    def __getKeyFromValue(self, d, s):
        for key, values in d.items():
            for v in values:
                if s.lower().replace(" ", "") == v.lower().replace(" ", ""):
                    return key

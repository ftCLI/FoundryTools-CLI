import csv
import os

from fontTools.ttLib import TTFont
from ftcli.Lib.configHandler import configHandler
from ftcli.Lib.pyFont import pyFont
from ftcli.Lib.utils import (getConfigPath, getFontsList,
                                    getSourceString, guessFamilyName)


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
            font = TTFont(f)
            file_name = os.path.basename(f)

            # Get the source string
            string = getSourceString(f, source_string)

            # Remove dashes, underscores and spaces from the string
            string = string.lower().replace("-", "").replace("_", "").replace(" ", "")

            weights = config['weights']
            widths = config['widths']
            italics = config['italics']

            try:
                wgt, weight = weights[str(pyFont(font).usWeightClass)]
            except:
                wgt, weight = [pyFont(font).usWeightClass,
                               pyFont(font).usWeightClass]

            try:
                wdt, width = widths[str(pyFont(font).usWidthClass)]
            except:
                wdt, width = [pyFont(font).usWidthClass, pyFont(font).usWidthClass]

            # Build the dictionary with the current values

            new_family_name = ""
            if family_name is None:
                for row in current_csv_data:
                    if row['file_name'] == file_name:
                        new_family_name = row['family_name']
            else:
                new_family_name = family_name

            this_font_data = {
                'is_bold': int(pyFont(font).is_bold),
                'is_italic': int(pyFont(font).is_italic),
                'uswidthclass': int(pyFont(font).usWidthClass),
                'wdt': str(wdt),
                'width': str(width),
                'usweightclass': int(pyFont(font).usWeightClass),
                'wgt': str(wgt),
                'weight': str(weight),
                'family_name': new_family_name,
                'file_name': file_name
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

            # Remove the family name from the string
            style_name = string.replace(new_family_name.lower().replace(
                ' ', ''), '').replace('-', '').replace('_', '').replace(' ', '')

            # Once removed the family name, the remaining string should be == style name (width/weight/slope)
            weight_string = width_string = italic_string = style_name

            # We remove all the widths and italics literals from the string, and what remains should be == the weight literal
            # (long or short has no importance).
            # If the obtained string is == to one of the weight literals, the corresponding key will be the new usWeightClass.
            # Otherwise usWeightClass is read from current font values.
            weight_string = self.__replaceListItems(
                input_string=weight_string, remove_list=widthsList, keep_list=weightsList)
            weight_string = self.__replaceListItems(
                input_string=weight_string, remove_list=italics, keep_list=weightsList)
            if self.__getKeyFromValue(weights, weight_string) is not None:
                new_usWeightClass = self.__getKeyFromValue(
                    weights, weight_string)
            else:
                new_usWeightClass = this_font_data['usweightclass']

            # At this point we retrieve the long and short weight literals.
            try:
                new_wgt = weights[new_usWeightClass][0]
            except:
                new_wgt = this_font_data['wgt']

            try:
                new_weight = weights[new_usWeightClass][1]
            except:
                new_weight = this_font_data['weight']

            # Same for widths
            width_string = self.__replaceListItems(
                input_string=width_string, remove_list=weightsList, keep_list=widthsList)
            width_string = self.__replaceListItems(
                input_string=width_string, remove_list=italics, keep_list=widthsList)
            if self.__getKeyFromValue(widths, width_string) is not None:
                new_usWidthClass = self.__getKeyFromValue(widths, width_string)
            else:
                new_usWidthClass = this_font_data['uswidthclass']
            try:
                new_wdt = widths[new_usWidthClass][0]
            except:
                new_wdt = this_font_data['wdt']

            try:
                new_width = widths[new_usWidthClass][1]
            except:
                new_width = this_font_data['width']

            # We ignore this because the bold bit will be set only if linked_styles is active when fixing fonts.
            new_isBold = this_font_data['is_bold']

            italic_string = self.__replaceListItems(
                input_string=italic_string, remove_list=widthsList, keep_list=italics)
            italic_string = self.__replaceListItems(
                input_string=italic_string, remove_list=weightsList, keep_list=italics)
            if italic_string == italics[0].lower() or italic_string == italics[1].lower():
                new_isItalic = '1'
            else:
                new_isItalic = this_font_data['is_italic']

            # Initialize the recalculated dictionary.
            new_font_data = {}
            new_font_data['is_bold'] = new_isBold
            new_font_data['is_italic'] = new_isItalic
            new_font_data['uswidthclass'] = new_usWidthClass
            new_font_data['wdt'] = new_wdt
            new_font_data['width'] = new_width
            new_font_data['usweightclass'] = new_usWeightClass
            new_font_data['wgt'] = new_wgt
            new_font_data['weight'] = new_weight
            new_font_data['family_name'] = new_family_name
            new_font_data['file_name'] = file_name

            new_csv_data.append(new_font_data)

        self.writeCSV(new_csv_data)

    def resetCSV(self, config_file):

        files = getFontsList(os.path.dirname(self.csv_file))
        config = configHandler(config_file).getConfig()
        csv_data = []

        for f in files:

            this_font_filename = os.path.basename(f)
            this_font_data = {}

            font = TTFont(f)
            is_bold = int(pyFont(font).is_bold)
            is_italic = int(pyFont(font).is_italic)
            usWidthClass = int(pyFont(font).usWidthClass)
            usWeightClass = int(pyFont(font).usWeightClass)

            try:
                wgt, weight = config['weights'][str(pyFont(font).usWeightClass)]
            except:
                wgt, weight = [pyFont(font).usWeightClass,
                               pyFont(font).usWeightClass]

            try:
                wdt, width = config['widths'][str(pyFont(font).usWidthClass)]
            except:
                wdt, width = [pyFont(font).usWidthClass, pyFont(font).usWidthClass]

            family_name = guessFamilyName(font)

            this_font_data = {
                'file_name': this_font_filename,
                'is_bold': is_bold,
                'is_italic': is_italic,
                'uswidthclass': usWidthClass,
                'wdt': wdt,
                'width': width,
                'usweightclass': usWeightClass,
                'wgt': wgt,
                'weight': weight,
                'family_name': family_name
            }

            csv_data.append(this_font_data)

        self.writeCSV(csv_data)

    def writeCSV(self, data):

        header = ('file_name', 'is_bold', 'is_italic', 'uswidthclass', 'wdt', 'width',
                  'usweightclass', 'wgt', 'weight', 'family_name')
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
                if (s.lower().replace(" ", "") == v.lower().replace(" ", "")):
                    return key

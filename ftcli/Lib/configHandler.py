import json
import os
import sys

import click


class configHandler(object):

    def __init__(self, config_file):

        self.config_file = config_file

    def getConfig(self):
        try:
            with open(self.config_file) as cf:
                config = json.load(cf)
            return config
        except json.decoder.JSONDecodeError:
            click.secho('\nERROR: JSON decoder error.', fg='red')
            sys.exit()
        except:
            click.secho('\nUNKNOWN ERROR.', fg='red')
            sys.exit()

    def saveConfig(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4)

    def resetConfig(self):
        with open(self.config_file, 'w') as f:
            json.dump({
                'weights': DEFAULT_WEIGHTS,
                'widths': DEFAULT_WIDTHS,
                'italics': DEFAULT_ITALICS,
            }, f, sort_keys=True, indent=4)


DEFAULT_WEIGHTS = {
    250: ['Th', 'Thin'],
    275: ['ExLt', 'ExtraLight'],
    300: ['Lt', 'Light'],
    350: ['Bk', 'Book'],
    400: ['Rg', 'Regular'],
    500: ['Md', 'Medium'],
    600: ['SmBd', 'SemiBold'],
    700: ['Bd', 'Bold'],
    800: ['ExBd', 'ExtraBold'],
    850: ['Hvy', 'Heavy'],
    900: ['Blk', 'Black']}

DEFAULT_WIDTHS = {
    1: ['Cm', 'Compressed'],
    2: ['ExCn', 'ExtraCondensed'],
    3: ['Cn', 'Condensed'],
    4: ['Nr', 'Narrow'],
    5: ['Nor', 'Normal'],
    6: ['Wd', 'Wide'],
    7: ['Extd', 'Extended'],
    8: ['ExExtd', 'ExtraExtended'],
    9: ['Exp', 'Expanded']}

DEFAULT_ITALICS = ['It', 'Italic']

import os

import click
from fontTools.ttLib import TTFont
from ftcli.Lib.utils import (getFontsList, getSourceString, makeOutputFileName)


@click.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-s', '--source-string', type=click.Choice(
    choices=['1_1_2', '1_4', '1_6', '1_16_17', '1_18', '3_1_2', '3_4', '3_6', '3_16_17', 'cff_1', 'cff_2', 'cff_3']),
              default='3_6',
              help="""
The source string is read from a namerecord or from a combination of two namerecords, and the font file is renamed
according to it.

The first number in the sequence is the platformID, while the following numbers represent the nameID(s) numbers.

For example:

-s 1_1_2: reads the strings contained in PlatformID 1 (Macintosh) nameID 1 and nameID 2 values and concatenates them.

-s 3_6: reads the platformID 3 (Windows) nameID 6 (PostScript name).

If the font is CFF flavored, the cff_1, cff_2, and cff_3 options can be used.
""")
def cli(input_path, source_string):
    """
Renames font files according to the provided source string.
    """

    files = getFontsList(input_path)

    for f in files:
        d = os.path.dirname(f)
        n = os.path.basename(f)

        font = TTFont(f)
        isCFF = 'CFF ' in font

        string = getSourceString(f, source_string)

        new_ext = None
        if font.flavor == 'woff':
            new_ext = '.woff'
        if font.flavor == 'woff2':
            new_ext = '.woff2'
        if font.flavor is None:
            if isCFF:
                new_ext = '.otf'
            else:
                new_ext = '.ttf'

        new_file_name = string + new_ext
        new_file = makeOutputFileName(os.path.join(d, new_file_name), overWrite=True)

        if new_file != f:
            try:
                os.rename(f, new_file)
                click.secho("{} --> {}".format(n, new_file_name), fg='green')

            except FileExistsError:
                new_file = makeOutputFileName(new_file, overWrite=False)
                os.rename(f, new_file)
                click.secho("%s --> %s" % (n, os.path.basename(new_file)), fg='green')

            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')
        else:
            click.secho("%s --> skipped" % n, fg='yellow')

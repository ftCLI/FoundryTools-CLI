import os
import sys

import click
from dehinter.font import dehint
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.ttLib import TTCollection
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps

from ftcli.Lib.Font import Font
from ftcli.Lib.utils import (getFontsList, makeOutputFileName, getSourceString, add_file_or_path_argument,
                             add_common_options)


def replaceIllegalCharacters(string: str, replacement_text: str = "") -> str:
    """
    Removes illegal characters from file names and directory names before saving the output files.
    :param string: File or directory name
    :param replacement_text: Replacement text for invalid characters. Defaults to ``""``.
    :return: Cleaned string
    """
    for illegal_char in ['/', '\\', '<', '>', ':', '"', '|', '?', '*']:
        string = string.replace(illegal_char, replacement_text)
    return string


@click.group()
def recalcItalicBits():
    pass


@recalcItalicBits.command()
@add_file_or_path_argument()
@add_common_options()
def recalc_italic_bits(input_path, outputDir, overWrite, recalcTimestamp):
    """Sets or clears the italic bits according to the `italicAngle` value in `post` table.

    If the `italicAngle` value is 0.0, the italic bits are cleared. If the value is not 0.0, the italic bits are set.
    """
    files = getFontsList(input_path)
    if len(files) == 0:
        click.pause('\nNo font files found.')
        sys.exit()

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            font.italicBitsFromItalicAngle()
            # Checking if the font has changed. If not, file isn't saved.
            if font.has_changed:
                output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
                font.save(output_file)
                click.secho(f'{os.path.basename(f)} --> saved', fg='green')
            else:
                click.secho(f'{os.path.basename(f)} --> no changes', fg='yellow')
        except Exception as e:
            click.secho(f'{os.path.basename(f)}: {e}', fg='red')


@click.group()
def fontOrganizer():
    pass


@fontOrganizer.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
def font_organizer(input_path):
    """Renames font files according to PostScript name and sorts them by foundry and family names.

    Usage: ftcli utils font-organizer INPUT_PATH

    INPUT_PATH can be a single font file or a directory containing fonts (subdirectories are not processed by choice).

    Fonts are renamed according to PostScript name (`name` table nameID 6) and sorted by Manufacturer Name (nameID 8).
    If nameID 8 is not present, the script will try to read nameID 9 (Designer) and if also name ID 9 is not present,
    the 4 characters achVendID stored in 'OS/2' table is used.

    Family name is read from nameID 16, or nameID 1 where nameID 16 is not present.

    If two files have identical foundry name, family name and PostScript name, a suffix with a number (#1, #2, etc.)
    is added at the end of filename to avoid overwriting an existing file.
    """

    print(f'\nParsing {input_path}')

    files = getFontsList(input_path)
    if len(files) == 0:
        click.pause('\nNo font files found.')
        sys.exit()

    print()
    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=False)

            try:
                foundry_name = font['name'].getName(8, 3, 1, 0x409).toUnicode()
            except AttributeError:
                try:
                    foundry_name = font['name'].getName(9, 3, 1, 0x409).toUnicode()
                except AttributeError:
                    try:
                        foundry_name = font['OS/2'].achVendID
                    except AttributeError:
                        foundry_name = 'Unknown foundry'

            foundry_name = replaceIllegalCharacters(foundry_name, replacement_text="_")

            try:
                family_name = font['name'].getName(16, 3, 1, 0x409).toUnicode()
            except AttributeError:
                try:
                    family_name = font['name'].getName(1, 3, 1, 0x409).toUnicode()
                except AttributeError:
                    family_name = 'Unknown family'

            family_name = replaceIllegalCharacters(family_name, replacement_text="_")

            new_ext = os.path.splitext(f)[1]
            if font.flavor == 'woff':
                new_ext = '.woff'
            if font.flavor == 'woff2':
                new_ext = '.woff2'
            if font.flavor is None:
                new_ext = '.otf' if font.sfntVersion == 'OTTO' else '.ttf'

            try:
                new_file_name = f"{font['name'].getName(6, 3, 1, 0x409).toUnicode()}{new_ext}"
            except AttributeError:
                try:
                    new_file_name = f"{font['name'].getName(6, 1, 0, 0x0).toUnicode()}{new_ext}"
                except AttributeError:
                    new_file_name = f"{os.path.splitext(os.path.basename(f))[0]}{new_ext}"

            new_file_name = replaceIllegalCharacters(new_file_name, replacement_text="_")

            new_dir = os.path.join(os.path.dirname(f), foundry_name, family_name)
            new_file = makeOutputFileName(os.path.join(new_dir, new_file_name))

            os.makedirs(new_dir, exist_ok=True)
            os.rename(f, new_file)

            click.secho(f'\nOLD PATH: {f}', fg="green")
            click.secho(f'NEW PATH: {new_file}', fg="green")

        except Exception as e:
            click.secho(f'{os.path.basename(f)}: {e}', fg='red')


# add-features
@click.group()
def addFeatures():
    pass


@addFeatures.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-fea', '--feature-file', type=click.Path(exists=True, resolve_path=True, dir_okay=False), required=True,
              help="Path to the feature file.")
@click.option('-t', '--tables',
              type=click.Choice(choices=["BASE", "GDEF", "GPOS", "GSUB", "OS/2", "head", "hhea", "name", "vhea",
                                         "STAT"]),
              multiple=True, help="Specify the table(s) to be built.")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help="""
The output directory where the output files are to be created. If it doesn't exist, will be created. If not specified,
files are saved to the same folder.""")
@click.option('--recalc-timestamp', is_flag=True, default=False,
              help="""
By default, original head.modified value is kept when a font is saved. Use this switch to set head.modified timestamp
to current time.
""")
@click.option('--no-overwrite', 'overwrite', is_flag=True, default=True,
              help="""
By default, modified files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name).
""")
def add_features(input_path, feature_file, tables, recalc_timestamp, output_dir, overwrite):
    """Import features form a fea file.
    """
    if tables == ():
        tables = None
    files = getFontsList(input_path)
    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalc_timestamp)
            addOpenTypeFeatures(font, featurefile=feature_file, tables=tables)

            output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')

        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


# add-dsig
@click.group()
def addDsig():
    pass


@addDsig.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help="""
The output directory where the output files are to be created. If it doesn't exist, will be created. If not specified,
files are saved to the same folder.""")
@click.option('--recalc-timestamp', is_flag=True, default=False,
              help="""
By default, original head.modified value is kept when a font is saved. Use this switch to set head.modified timestamp
to current time.
""")
@click.option('--no-overwrite', 'overwrite', is_flag=True, default=True,
              help="""
By default, modified files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name).
""")
def add_dsig(input_path, recalc_timestamp, output_dir, overwrite):
    """Adds a dummy DSIG to the font, if it's not present.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalc_timestamp)
            if 'DSIG' not in font:
                font.addDummyDSIG()
                if output_dir is None:
                    output_dir = os.path.dirname(f)
                else:
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir)

                output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
                click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
            else:
                click.secho(f'No changes made, DSIG table is already present in {os.path.basename(f)}', fg='yellow')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


# dehinter
@click.group()
def removeHinting():
    pass


@removeHinting.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('--keep-cvar', is_flag=True, default=False, help="keep cvar table")
@click.option('--keep-cvt', is_flag=True, default=False, help="keep cvt table")
@click.option('--keep-fpgm', is_flag=True, default=False, help="keep fpgm table")
@click.option('--keep-hdmx', is_flag=True, default=False, help="keep hdmx table")
@click.option('--keep-ltsh', is_flag=True, default=False, help="keep LTSH table")
@click.option('--keep-prep', is_flag=True, default=False, help="keep prep table")
@click.option('--keep-ttfa', is_flag=True, default=False, help="keep ttfa table")
@click.option('--keep-vdmx', is_flag=True, default=False, help="keep vdmx table")
@click.option('--keep-glyf', is_flag=True, default=False, help="do not modify glyf table")
@click.option('--keep-gasp', is_flag=True, default=False, help="do not modify gasp table")
@click.option('--keep-maxp', is_flag=True, default=False, help="do not modify maxp table")
@click.option('--keep-head', is_flag=True, default=False, help="do not modify head table")
@click.option('--verbose', is_flag=True, default=False, help="display standard output")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help="""
The output directory where the output files are to be created. If it doesn't exist, will be created. If not specified,
files are saved to the same folder.""")
@click.option('--recalc-timestamp', is_flag=True, default=False,
              help="""
By default, original head.modified value is kept when a font is saved. Use this switch to set head.modified timestamp
to current time.
""")
@click.option('--no-overwrite', 'overwrite', is_flag=True, default=True,
              help="""
By default, modified files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name).
""")
def dehinter(input_path, keep_cvar, keep_cvt, keep_fpgm, keep_hdmx, keep_ltsh, keep_prep, keep_ttfa, keep_vdmx,
             keep_glyf, keep_gasp, keep_maxp, keep_head, verbose, output_dir=None, recalc_timestamp=False,
             overwrite=True):
    """Drops hinting from all glyphs.

    Currently, this only works with TrueType fonts with 'glyf' table.

    This is a CLI for dehinter by Source Foundry: https://github.com/source-foundry/dehinter
    """

    files = getFontsList(input_path)
    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)
            if not font.sfntVersion == 'OTTO':
                dehint(font, keep_cvar=keep_cvar, keep_cvt=keep_cvt, keep_fpgm=keep_fpgm, keep_gasp=keep_gasp,
                       keep_glyf=keep_glyf, keep_head=keep_head, keep_hdmx=keep_hdmx, keep_ltsh=keep_ltsh,
                       keep_maxp=keep_maxp, keep_prep=keep_prep, keep_ttfa=keep_ttfa, keep_vdmx=keep_vdmx,
                       verbose=verbose)
                output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
                click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
            else:
                click.secho(f'ERROR: {os.path.basename(f)} is not a TrueType file', fg='red')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


@click.group()
def rmvOverlaps():
    pass


@rmvOverlaps.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help="""
The output directory where the output files are to be created. If it doesn't exist, will be created. If not specified,
files are saved to the same folder.""")
@click.option('--recalc-timestamp', is_flag=True, default=False,
              help="""
By default, original head.modified value is kept when a font is saved. Use this switch to set head.modified timestamp
to current time.
""")
@click.option('--no-overwrite', 'overwrite', is_flag=True, default=True,
              help="""
By default, modified files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name).
""")
def remove_overlaps(input_path, output_dir=None, recalc_timestamp=False, overwrite=True):
    """Simplify glyphs in TTFont by merging overlapping contours.

    Overlapping components are first decomposed to simple contours, then merged.

    Currently, this only works with TrueType fonts with 'glyf' table.

    Note that removing overlaps invalidates the hinting. Hinting is dropped from all glyphs whether or not overlaps are
    removed from a given one, as it would look weird if only some glyphs are left (un)hinted.
    """

    files = getFontsList(input_path)
    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)
            if not font.sfntVersion == 'OTTO':
                removeOverlaps(font)
                output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
                click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
            else:
                click.secho(f'{os.path.basename(f)} is not a TrueType file', fg='red')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


@click.group()
def fontRenamer():
    pass


@fontRenamer.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-s', '--source-string', type=click.Choice(
    choices=['1_1_2', '1_4', '1_6', '1_16_17', '1_18', '3_1_2', '3_4', '3_6', '3_16_17', 'cff_1', 'cff_2']),
              default='3_6',
              help="""
The source string is read from a namerecord or from a combination of two namerecords, and the font file is renamed
according to it.

The first number in the sequence is the platformID, while the following numbers represent the nameID(s) numbers.

For example:

-s 1_1_2: reads the strings contained in PlatformID 1 (Macintosh) nameID 1 and nameID 2 values and concatenates them.

-s 3_6: reads the platformID 3 (Windows) nameID 6 (PostScript name).

If the font is CFF flavored, the cff_1 or cff_2 options can be used.
""")
def font_renamer(input_path, source_string):
    """
Renames font files according to the provided source string.
    """

    files = getFontsList(input_path)

    for f in files:
        d = os.path.dirname(f)
        n = os.path.basename(f)

        font = TTFont(f)
        isCFF = 'CFF ' in font
        if not isCFF and source_string in ('cff_1', 'cff_2'):
            click.secho(f'Invalid option: {source_string}. {n} does not seem to be a CFF font', fg='yellow')
            continue

        string = getSourceString(f, source_string)
        if not string:
            string = os.path.splitext(n)[0]

        # Remove illegal characters from the string.
        string = replaceIllegalCharacters(string, replacement_text="_")

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
                click.secho(f'{n} --> {os.path.basename(new_file)}', fg='green')

            except Exception as e:
                click.secho(f'ERROR: {e}', fg='red')
        else:
            click.secho(f'{f} --> skipped', fg='yellow')


@click.group()
def ttcExtractor():
    pass


@ttcExtractor.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True, dir_okay=False))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help="""
The output directory where the output files are to be created. If it doesn't exist, will be created. If not specified,
files are saved to the same folder.""")
@click.option('--recalc-timestamp', is_flag=True, default=False,
              help="""
By default, original head.modified value is kept when a font is saved. Use this switch to set head.modified timestamp
to current time.
""")
@click.option('--no-overwrite', 'overwrite', is_flag=True, default=True,
              help="""
By default, modified files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name).
""")
def ttc_extractor(input_path, output_dir=None, recalc_timestamp=False, overwrite=True):
    """Extracts .ttc fonts to otf/ttf fonts.
    """
    try:
        TTCfont = TTCollection(input_path)
        fonts = TTCfont.fonts
        for font in fonts:
            font.recalcTimestamp = recalc_timestamp
            filename = str(font['name'].getName(6, 3, 1, 0x409))
            ext = '.otf' if font.sfntVersion == 'OTTO' else '.ttf'
            if not output_dir:
                output_dir = os.path.dirname(input_path)
            output_file = makeOutputFileName(filename + ext, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
    except Exception as e:
        click.secho('ERROR: {}'.format(e), fg='red')


@click.group()
def delTable():
    pass


@delTable.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-t', '--table', required=True)
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help='The output directory where the output files are to be created. If it doesn\'t exist, will be '
                   'created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False,
              help='Keeps the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True,
              help='Overwrites existing output files or save them to a new file (numbers are appended at the end of '
                   'file name). By default, files are overwritten.')
def del_table(input_path, table, output_dir, recalc_timestamp, overwrite):
    """Deletes the specified table from the font.
    """
    files = getFontsList(input_path)
    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalc_timestamp)
            if table in font:
                del font[table]
                output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
                click.secho(f'{os.path.basename(output_file)} --> {table} table deleted.', fg='green')
            else:
                click.secho(f'{os.path.basename(f)} --> {table} table not found.', fg='yellow')
        except Exception as e:
            click.secho(f'{os.path.basename(f)} --> ERROR: {e}', fg='red')


cli = click.CommandCollection(sources=[addDsig, addFeatures, delTable, fontOrganizer, removeHinting, fontRenamer,
                                       recalcItalicBits, rmvOverlaps, ttcExtractor],
                              help="Miscellaneous utilities.")

import os

import click
from fontTools.ttLib import TTCollection
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps

from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.utils import getFontsList, makeOutputFileName, getSourceString


@click.group()
def rmHinting():
    pass


@rmHinting.command()
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
@click.option('--keep-head', is_flag=True, default=False, help="do not head glyf table")
@click.option('--verbose', is_flag=True, default=False, help="display standard output")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t '
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of '
                   'file name). By default, files are overwritten.')
def remove_hinting(input_path, keep_cvar, keep_cvt, keep_fpgm, keep_hdmx, keep_ltsh, keep_prep, keep_ttfa, keep_vdmx,
                   keep_glyf, keep_gasp, keep_maxp, keep_head, verbose, output_dir=None, recalc_timestamp=False,
                   overwrite=True):
    """Drops hinting from all glyphs.

    Currently this only works with TrueType fonts with 'glyf' table.

    This is a CLI for dehinter by Source Foundry: https://github.com/source-foundry/dehinter
    """

    from dehinter.font import dehint

    files = getFontsList(input_path)
    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)
            if not font.sfntVersion == 'OTTO':
                dehint(font, keep_cvar=keep_cvar, keep_cvt=keep_cvt, keep_fpgm=keep_fpgm, keep_gasp=keep_gasp,
                       keep_glyf=keep_glyf, keep_head=keep_head, keep_ltsh=keep_ltsh, keep_maxp=keep_maxp,
                       keep_prep=keep_prep, keep_ttfa=keep_ttfa, keep_vdmx=keep_vdmx, verbose=verbose)
                output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
                click.secho('%s saved' % output_file, fg='green')
            else:
                click.secho(f'{f} is not a TrueType file', fg='red')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


@click.group()
def rmOverlaps():
    pass


@rmOverlaps.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t '
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def remove_overlaps(input_path, output_dir=None, recalc_timestamp=False, overwrite=True):
    """Simplify glyphs in TTFont by merging overlapping contours.

    Overlapping components are first decomposed to simple contours, then merged.

    Currently this only works with TrueType fonts with 'glyf' table.

    Note that removing overlaps invalidates the hinting. Hinting is dropped from
    all glyphs whether or not overlaps are removed from a given one, as it would
    look weird if only some glyphs are left (un)hinted.
    """

    files = getFontsList(input_path)
    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)
            if not font.sfntVersion == 'OTTO':
                removeOverlaps(font)
                output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
                click.secho('%s saved' % output_file, fg='green')
            else:
                click.secho('%s is not a TrueType file' % f, fg='red')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


@click.group()
def extractTTC():
    pass


@extractTTC.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True, dir_okay=False))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t '
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def ttc_extractor(input_path, output_dir=None, recalc_timestamp=False, overwrite=True):
    """
Extracts .ttc fonts.
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
            click.secho('%s saved' % output_file, fg='green')
    except Exception as e:
        click.secho('ERROR: {}'.format(e), fg='red')


@click.group()
def addDSIG():
    pass


@addDSIG.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-o', '--output-dir', type=click.Path(resolve_path=True),
              help='The output directory where the output files are to be created. If it doesn\'t exist, will be'
                   'created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False,
              help='Keeps the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True,
              help='Overwrites existing output files or save them to a new file (numbers are appended at the end of'
                   'filename). By default, files are overwritten.')
def add_dsig(input_path, recalc_timestamp, output_dir, overwrite):
    """
    Adds a dummy DSIG to the font if it's not present.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            if 'DSIG' not in font:
                font.addDummyDSIG()
                if output_dir is None:
                    output_dir = os.path.dirname(f)
                else:
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir)

                output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
                click.secho('%s --> saved' % f, fg='green')
            else:
                click.secho('DSIG table is already present in {}'.format(f), fg='yellow')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


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


cli = click.CommandCollection(sources=[rmOverlaps, rmHinting, extractTTC, addDSIG, fontRenamer], help="Miscellaneous utilities.")

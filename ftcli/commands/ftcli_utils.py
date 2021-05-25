import os

import click
from fontTools.ttLib import TTCollection
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps

from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.utils import getFontsList, makeOutputFileName


@click.group()
def rmOverlaps():
    pass


@rmOverlaps.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t'
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def remove_overlaps(input_path, output_dir=None, recalc_timestamp=False, overwrite=True):
    """
    Simplify glyphs in TTFont by merging overlapping contours.

    Overlapping components are first decomposed to simple contours, then merged.

    Currently this only works with TrueType fonts with 'glyf' table.
    Raises NotImplementedError if 'glyf' table is absent.

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
                click.secho('%s in not a TrueType file' % f, fg='red')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


@click.group()
def extractTTC():
    pass


@extractTTC.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True, dir_okay=False))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t'
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


cli = click.CommandCollection(sources=[rmOverlaps, extractTTC, addDSIG], help="Miscellaneous utilities.")

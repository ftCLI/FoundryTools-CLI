import click
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
from ftcli.Lib.utils import getFontsList, makeOutputFileName


@click.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file name). By default, files are overwritten.')
def cli(input_path, output_dir=None, recalc_timestamp=False, overwrite=True):
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
                output_file = makeOutputFileName(
                    f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
            click.secho('%s saved' % output_file, fg='green')
        except:
            click.secho('ERROR: %s is not a valid font' % f, fg='red')
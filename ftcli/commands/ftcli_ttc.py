import os.path

import click
from fontTools.ttLib import TTCollection

from ftcli.Lib.utils import makeOutputFileName


@click.command()
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
def cli(input_path, output_dir=None, recalc_timestamp=False, overwrite=True):
    """
Extracts .ttc fonts.
    """
    try:
        TTCfont = TTCollection(input_path)
        fonts = TTCfont.fonts
        for font in fonts:
            font.recalcTimestamp = recalc_timestamp
            filename = str(font['name'].getName(6, 3, 1, 0x409))
            print(filename)
            ext = '.otf' if font.sfntVersion == 'OTTO' else '.ttf'
            if not output_dir:
                output_dir = os.path.dirname(input_path)
            output_file = makeOutputFileName(filename + ext, outputDir=output_dir, overWrite=overwrite)
            print(output_file)
            font.save(output_file)
            click.secho('%s saved' % output_file, fg='green')
    except:
        click.secho('ERROR: %s is not a valid font' % input_path, fg='red')

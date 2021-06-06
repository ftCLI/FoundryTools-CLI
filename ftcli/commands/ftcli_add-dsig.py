import os

import click

from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.utils import getFontsList, makeOutputFileName


@click.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-o', '--output-dir', type=click.Path(resolve_path=True),
              help='The output directory where the output files are to be created. If it doesn\'t exist, will be'
                   'created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False,
              help='Keeps the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True,
              help='Overwrites existing output files or save them to a new file (numbers are appended at the end of'
                   'filename). By default, files are overwritten.')
def cli(input_path, recalc_timestamp, output_dir, overwrite):
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

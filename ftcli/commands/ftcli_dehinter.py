import click
from fontTools.ttLib import TTFont

from ftcli.Lib.utils import getFontsList, makeOutputFileName


@click.command()
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
def cli(input_path, keep_cvar, keep_cvt, keep_fpgm, keep_hdmx, keep_ltsh, keep_prep, keep_ttfa, keep_vdmx,
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

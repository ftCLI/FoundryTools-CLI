import os

import click
from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.utils import getFontsList, makeOutputFileName


@click.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-b/-nb', '--bold/--no-bold', default=None,
              help='Sets or clears the bold bits (OS/2.fsSelection bit 5 and head.macStyle bit 0).')
@click.option('-i/-ni', '--italic/--no-italic', default=None,
              help='Sets or clears the italic bits (OS/2.fsSelection bit 0 and head.macStyle bit 1).')
@click.option('-ob/-nob', '--oblique/--no-oblique', default=None,
              help='Sets or clears the oblique bit (OS/2.fsSelection bit 9).')
@click.option('-wd', '--width', type=click.IntRange(1, 9),
              help='Sets the OS/2.usWidthClass value (1-9)')
@click.option('-wg', '--weight', type=click.IntRange(1, 1000),
              help='Sets the OS/2.usWeightClass value (1-1000).')
@click.option('-el', '--embed-level', type=click.Choice(['0', '2', '4', '8']), default=None,
              help="""
Sets embedding level (OS/2.fsType).

\b
0: Installable embedding
2: Restricted License embedding
4: Preview & Print embedding
8: Editable embedding
""")
@click.option('-utm/-noutm', '--use-typo-metrics/--no-typo-metrics', default=None,
              help="""
Sets or clears the USE_TYPO_METRICS bit (OS/2.fsSelection bit 7).

If set, it is strongly recommended that applications use OS/2.sTypoAscender - OS/2.sTypoDescender + OS/2.sTypoLineGap as
the default line spacing for this font.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection
""")
@click.option('-ach', '--ach-vend-id', type=str,
              help='Sets the the OS/2.achVendID tag (vendor\'s four-character identifier).')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help='The output directory where the output files are to be created. If it doesn\'t exist, will be'
                   'created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False,
              help='Keeps the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True,
              help='Overwrites existing output files or save them to a new file (numbers are appended at the end of '
                   'file name). By default, files are overwritten.')
def cli(input_path, bold, italic, oblique, width, weight, embed_level, use_typo_metrics, ach_vend_id, recalc_timestamp,
        output_dir, overwrite):
    """
    A command line tool to edit some OS/2 table attributes.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            is_bold = font.isBold()
            is_italic = font.isItalic()
            is_oblique = font.isOblique()
            uses_typo_metrics = font.usesTypoMetrics()
            usWeightClass = font['OS/2'].usWeightClass
            usWidthClass = font['OS/2'].usWidthClass
            fsType = font['OS/2'].fsType

            modified = False

            if bold is not None:
                if is_bold != bold:
                    if bold is True:
                        font.setBold()
                    else:
                        font.unsetBold()
                    modified = True

            if italic is not None:
                if is_italic != italic:
                    if italic is True:
                        font.setItalic()
                    else:
                        font.unsetItalic()
                    modified = True

            if oblique is not None:
                if is_oblique != oblique:
                    if oblique is True:
                        font.setOblique()
                    else:
                        font.unsetOblique()

                    modified = True

            if weight is not None:
                if usWeightClass != weight:
                    font['OS/2'].usWeightClass = weight
                    modified = True

            if width is not None:
                if usWidthClass != width:
                    font['OS/2'].usWidthClass = width
                    modified = True

            if embed_level is not None:
                embed_level = click.INT(embed_level)
                if fsType != embed_level:
                    font['OS/2'].fsType = embed_level
                    modified = True

            if ach_vend_id:
                if len(ach_vend_id) > 4:
                    ach_vend_id = ach_vend_id[0:4]
                    click.secho(
                        '\nach_vend_id was longer than 4 characters, it has been truncated.', fg='yellow')
                if len(ach_vend_id) < 4:
                    ach_vend_id = str(ach_vend_id).ljust(4)
                if not ach_vend_id == font['OS/2'].achVendID:
                    font.setAchVendID(ach_vend_id)
                    modified = True

            if use_typo_metrics is not None:
                if uses_typo_metrics != use_typo_metrics:
                    font['OS/2'].version = 4
                    if use_typo_metrics is True:
                        if font['OS/2'].version > 3:
                            font.setUseTypoMetrics()
                            modified = True
                        else:
                            click.secho("\nfsSelection bits 7 is only defined in OS/2 table version 4 and up."
                                        "Current version: {}".format(font['OS/2'].version), fg='red')
                    if use_typo_metrics is False:
                        font.unsetUseTypoMetrics()
                        modified = True

            if output_dir is None:
                output_dir = os.path.dirname(f)
            else:
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)

            output_file = makeOutputFileName(
                f, outputDir=output_dir, overWrite=overwrite)

            if modified is True:
                font.save(output_file)
                click.secho('%s --> saved' % f, fg='green')
            else:
                click.secho('% s --> no changes made' % f, fg='yellow')

        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')

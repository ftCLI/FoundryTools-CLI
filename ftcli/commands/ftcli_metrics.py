import os
import sys

import click
from fontTools.ttLib import TTFont
from ftcli.Lib.utils import getFontsList, makeOutputFileName


@click.group()
def alignVMetrics():
    pass


@alignVMetrics.command()
@click.argument('input_path', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('-sil', '--sil-method', is_flag=True, help='Use SIL method: http://silnrsi.github.io/FDBP/en-US/Line_Metrics.html')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help='The output directory where the output files are to be created. If it doesn\'t exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False,
              help='Keeps the original font \'modified\' timestamp (head.modified) or set it to current time. By default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True,
              help='Overwrites existing output files or save them to a new file (numbers are appended at the end of file name). By default, files are overwritten.')
def align(input_path, sil_method, output_dir, recalc_timestamp, overwrite):
    """
    Aligns all fonts in INPUT_PATH to the same baseline.

    To achieve this, the script finds the maximum ascender and the minimum descender values of the fonts stored in the INPUT_PATH folder and applies those values to all fonts.

    This can produce undesired effects (an exaggerated line height) when one or more fonts contain swashes, for example. In such cases, it's better to copy the vertical metrics from a template font to one or more destination fonts using the 'ftcli metrics copy' command.

    See https://www.kltf.de/downloads/FontMetrics-kltf.pdf for more informations.
    """
    files = getFontsList(input_path)

    idealAscenders = []
    idealDescenders = []
    realAscenders = []
    realDescenders = []

    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)

            yMax = font['head'].yMax
            yMin = font['head'].yMin

            ascender = font['hhea'].ascender
            descender = font['hhea'].descender

            sTypoAscender = font['OS/2'].sTypoAscender
            sTypoDescender = font['OS/2'].sTypoDescender
            usWinAscent = font['OS/2'].usWinAscent
            usWinDescent = font['OS/2'].usWinDescent

            idealAscenders.extend([sTypoAscender])
            idealDescenders.extend([abs(sTypoDescender)])

            realAscenders.extend([yMax, usWinAscent, ascender])
            realDescenders.extend(
                [abs(yMin), abs(usWinDescent), abs(descender)])

        except:
            click.secho('ERROR: %s is not a valid font' % f, fg='red')
            files.remove(f)

    maxRealAscender = max(realAscenders)
    maxRealDescender = max(realDescenders)
    maxIdealAscender = max(idealAscenders)
    maxIdealDescender = max(idealDescenders)
    sTypoLineGap = (maxRealAscender + maxRealDescender) - \
        (maxIdealAscender + maxIdealDescender)

    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)

            font['hhea'].ascender = maxRealAscender
            font['hhea'].descender = -maxRealDescender
            font['hhea'].lineGap = 0

            font['OS/2'].usWinAscent = maxRealAscender
            font['OS/2'].usWinDescent = maxRealDescender
            font['OS/2'].sTypoAscender = maxIdealAscender
            font['OS/2'].sTypoDescender = -maxIdealDescender
            font['OS/2'].sTypoLineGap = sTypoLineGap

            if sil_method:
                font['OS/2'].sTypoAscender = maxRealAscender
                font['OS/2'].sTypoDescender = -maxRealDescender
                font['OS/2'].sTypoLineGap = 0

            output_file = makeOutputFileName(
                f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('%s saved' % output_file, fg='green')
        except:
            click.secho('ERROR: %s is not a valid font' % f, fg='red')


@click.group()
def copyVMetrics():
    pass


@copyVMetrics.command()
@click.option('-s', '--source-file', type=click.Path(exists=True, dir_okay=False, resolve_path=True), required=True, help='Source file. Vertical metrics from this font will be applied to all destination fonts.')
@click.option('-d', '--destination', type=click.Path(exists=True, resolve_path=True), required=True, help='Destination file or directory')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help='The output directory where the output files are to be created. If it doesn\'t exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False,
              help='Keeps the original font \'modified\' timestamp (head.modified) or set it to current time. By default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True,
              help='Overwrites existing output files or save them to a new file (numbers are appended at the end of file name). By default, files are overwritten.')
def copy(source_file, destination, output_dir, recalc_timestamp, overwrite):
    """
    Copies vertical metrics from a source font to one or more destination fonts.
    """

    try:
        source_font = TTFont(source_file)

        ascender = source_font['hhea'].ascender
        descender = source_font['hhea'].descender
        lineGap = source_font['hhea'].lineGap

        usWinAscent = source_font['OS/2'].usWinAscent
        usWinDescent = source_font['OS/2'].usWinDescent
        sTypoAscender = source_font['OS/2'].sTypoAscender
        sTypoDescender = source_font['OS/2'].sTypoDescender
        sTypoLineGap = source_font['OS/2'].sTypoLineGap

    except:
        click.secho('%s is not a valid font', fg='red')
        sys.exit()

    files = getFontsList(destination)

    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)

            font['hhea'].ascender = ascender
            font['hhea'].descender = descender
            font['hhea'].lineGap = 0

            font['OS/2'].usWinAscent = usWinAscent
            font['OS/2'].usWinDescent = usWinDescent
            font['OS/2'].sTypoAscender = sTypoAscender
            font['OS/2'].sTypoDescender = sTypoDescender
            font['OS/2'].sTypoLineGap = sTypoLineGap

            output_file = makeOutputFileName(
                f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('%s saved' % output_file, fg='green')
        except:
            click.secho('ERROR: %s is not a valid font' % f, fg='red')


cli = click.CommandCollection(sources=[alignVMetrics, copyVMetrics], help="""
Aligns all the fonts to the same baseline.

The 'ftcli metrics align' command calculates the maximum ascenders and descenders of a set of fonts and applies them to all fonts in that set.

The 'ftcli metrics copy' command copies vertical metrics from a source font to one or more destination fonts.
    """
                              )

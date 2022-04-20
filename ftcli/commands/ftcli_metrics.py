import os
import sys

import click

from ftcli.Lib.Font import Font
from ftcli.Lib.utils import getFontsList, makeOutputFileName, guessFamilyName


@click.group()
def setLineGap():
    pass


@setLineGap.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-p', '--percent', type=click.IntRange(1, 100), required=True,
              help="Adjust font line spacing to % of UPM value.")
@click.option('-mfn', '--modify-family-name', is_flag=True,
              help="Adds LG% to the font family to reflect the modified line gap.")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help='The output directory where the output files are to be created. If it doesn\'t exist, will be '
                   'created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False,
              help='Keeps the original font \'modified\' timestamp (head.modified) or set it to current time. '
                   'By default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True,
              help='Overwrites existing output files or save them to a new file (numbers are appended at the end of '
                   'file name). By default, files are overwritten.')
def set_linegap(input_path, percent, modify_family_name, output_dir, recalc_timestamp, overwrite):
    """Modifies the line spacing metrics in one or more fonts.

    This is a fork of font-line by Source Foundry: https://github.com/source-foundry/font-line
    """

    files = getFontsList(input_path)

    for f in files:

        file_name, ext = os.path.splitext(os.path.basename(f))
        file_dir = os.path.dirname(f)

        try:
            font = Font(f, recalcTimestamp=recalc_timestamp)
            font.modifyLinegapPercent(percent)

            # Modify the family name according to the linegap percent
            if modify_family_name:
                old_family_name = guessFamilyName(font)
                if old_family_name:
                    old_family_name_without_spaces = old_family_name.replace(" ", "")
                    new_family_name = old_family_name + ' LG{}'.format(str(percent))
                    new_family_name_without_spaces = new_family_name.replace(" ", "")
                    font.findReplace(oldString=old_family_name, newString=new_family_name, fixCFF=True)
                    font.findReplace(oldString=old_family_name_without_spaces, newString=new_family_name_without_spaces,
                                     fixCFF=True)
                else:
                    click.secho('Warning: could not retrieve Family Name, it has not been modified.', fg='yellow')

            # Before we add the "-linegap%" string to the new file name, let's remove it to avoid strange names like
            # Font-Bold-linegap20-linegap20.otf
            # new_file_path = os.path.join(file_dir, file_name.replace('-linegap' + str(percent), '') + '-linegap'
            #                              + str(percent) + ext)
            output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')

        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


@click.group()
def alignVMetrics():
    pass


@alignVMetrics.command()
@click.argument('input_path', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('-sil', '--sil-method', is_flag=True,
              help='Use SIL method: https://silnrsi.github.io/FDBP/en-US/Line_Metrics.html')
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
def align(input_path, sil_method, output_dir, recalc_timestamp, overwrite):
    """
    Aligns all fonts stored in INPUT_PATH folder to the same baseline.

    To achieve this, the script finds the maximum ascender and the minimum descender values of the fonts stored in the
    INPUT_PATH folder and applies those values to all fonts.

    This can produce undesired effects (an exaggerated line height) when one or more fonts contain swashes, for example.
    In such cases, it's better to copy the vertical metrics from a template font to one or more destination fonts using
    the 'ftcli metrics copy' command.

    See https://kltf.de/download/FontMetrics-kltf.pdf for more information.
    """
    files = getFontsList(input_path)

    idealAscenders = []
    idealDescenders = []
    realAscenders = []
    realDescenders = []

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalc_timestamp)

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

        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')
            files.remove(f)

    maxRealAscender = max(realAscenders)
    maxRealDescender = max(realDescenders)
    maxIdealAscender = max(idealAscenders)
    maxIdealDescender = max(idealDescenders)
    sTypoLineGap = (maxRealAscender + maxRealDescender) - (maxIdealAscender + maxIdealDescender)
    sTypoLineGap = 0

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalc_timestamp)

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
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


@click.group()
def copyVMetrics():
    pass


@copyVMetrics.command()
@click.option('-s', '--source-file', type=click.Path(exists=True, dir_okay=False, resolve_path=True), required=True,
              help='Source file. Vertical metrics from this font will be applied to all destination fonts.')
@click.option('-d', '--destination', type=click.Path(exists=True, resolve_path=True), required=True,
              help='Destination file or directory.')
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
def copy(source_file, destination, output_dir, recalc_timestamp, overwrite):
    """
    Copies vertical metrics from a source font to one or more destination fonts.
    """

    try:
        source_font = Font(source_file)

        ascender = source_font['hhea'].ascender
        descender = source_font['hhea'].descender
        lineGap = source_font['hhea'].lineGap

        usWinAscent = source_font['OS/2'].usWinAscent
        usWinDescent = source_font['OS/2'].usWinDescent
        sTypoAscender = source_font['OS/2'].sTypoAscender
        sTypoDescender = source_font['OS/2'].sTypoDescender
        sTypoLineGap = source_font['OS/2'].sTypoLineGap

    except Exception as e:
        click.secho('ERROR: {}'.format(e), fg='red')
        sys.exit()

    files = getFontsList(destination)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalc_timestamp)

            font['hhea'].ascender = ascender
            font['hhea'].descender = descender
            font['hhea'].lineGap = lineGap

            font['OS/2'].usWinAscent = usWinAscent
            font['OS/2'].usWinDescent = usWinDescent
            font['OS/2'].sTypoAscender = sTypoAscender
            font['OS/2'].sTypoDescender = sTypoDescender
            font['OS/2'].sTypoLineGap = sTypoLineGap

            output_file = makeOutputFileName(
                f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


cli = click.CommandCollection(sources=[alignVMetrics, copyVMetrics, setLineGap], help="""
Vertical metrics tools.
""")

import os

import click
from fontTools.ttLib import TTFont
from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.utils import (getFontsList, guessFamilyName, makeOutputFileName)


@click.group()
def makeCSS():
    pass


@makeCSS.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
def makecss(input_path):
    """
Parses all WOFF and WOFF2 files in INPUT_PATH and creates a CSS stylesheet to use them on web pages.
    """

    files = getFontsList(input_path)

    css_file = os.path.join(input_path, 'fonts.css') if os.path.isdir(input_path) \
        else os.path.join(os.path.dirname(input_path), 'fonts.css')
    with open(css_file, 'w') as stylesheet:
        pass

    unique_triplets = []
    for f in files:

        font = TTFontCLI(f)
        this_font_triplet = (
            guessFamilyName(font),
            font['OS/2'].usWeightClass,
            'italic' if font.isItalic() else 'normal'
        )
        if this_font_triplet not in unique_triplets:
            unique_triplets.append(this_font_triplet)

    unique_triplets.sort()

    font_faces = []
    for t in unique_triplets:

        font_face_data = {
            'font-family': t[0],
            'font-weight': t[1],
            'font-style': t[2],
            'woff_src': None,
            'woff2_src': None
        }

        for f in files:

            font = TTFontCLI(f)
            this_font_triplet = (
                guessFamilyName(font),
                font['OS/2'].usWeightClass,
                'italic' if font.isItalic() else 'normal'
            )
            if this_font_triplet == t:
                if font.flavor == 'woff':
                    font_face_data['woff_src'] = os.path.basename(f)
                if font.flavor == "woff2":
                    font_face_data['woff2_src'] = os.path.basename(f)

        font_faces.append(font_face_data)

    for ff in font_faces:
        css_string = "@font-face {\n"
        css_string += "  font-family: '{}';\n".format(ff['font-family'])
        css_string += "  src: "

        woff2_string = ""
        if ff['woff2_src'] is not None:
            woff2_string = "url('{}') format('woff2')".format(ff['woff2_src'])
            if ff['woff_src'] is not None:
                woff2_string += ',\n       '
            else:
                woff2_string += ';\n'
        css_string += woff2_string

        woff_string = ""
        if ff['woff_src'] is not None:
            woff_string = "url('{}') format('woff');\n".format(ff['woff_src'])
        css_string += woff_string

        css_string += '  font-weight: {};\n'.format(ff['font-weight'])
        css_string += '  font-style: {};'.format(ff['font-style'])
        css_string += '\n}\n'

        with open(css_file, 'a') as css:
            css.write(css_string)

    click.secho("{} created.".format(css_file), fg='green')


@click.group()
def fontToWebfont():
    pass


@fontToWebfont.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-f', '--flavor', type=click.Choice(choices=['woff', 'woff2']),
              help='Specify the flavor [woff|woff2] of the output files. If not specified, both WOFF and WOFF2 files '
                   'will be created')
@click.option('-d', '--delete-source-file', is_flag=True,
              help='If this option is active, source file will be deleted.')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t '
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of '
                   'file name). By default, files are overwritten.')
def compress(input_path, flavor, delete_source_file=False, output_dir=None, recalc_timestamp=False, overwrite=True):
    """
Converts OpenType fonts to WOFF/WOFF2 format.

Use the -f/--flavor option to specify flavor of output font files. May be 'woff' or 'woff2'. If no flavor is
specified, both WOFF and WOFF2 files will be created.
    """

    files = getFontsList(input_path)

    flavors = ['woff', 'woff2']
    if flavor == 'woff':
        flavors.remove('woff2')
    if flavor == 'woff2':
        flavors.remove('woff')

    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)
            if font.flavor is None:
                for flv in flavors:
                    output_file = makeOutputFileName(
                        f, outputDir=output_dir, extension='.' + flv, overWrite=overwrite)
                    font.flavor = flv
                    font.save(output_file)
                    click.secho('%s saved' % output_file, fg='green')
                if delete_source_file:
                    os.remove(f)
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


# decompress


@click.group()
def webfontToFont():
    pass


@webfontToFont.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-d', '--delete-source-file', is_flag=True,
              help='If this option is active, source file will be deleted after conversion.')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t '
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of '
                   'file name). By default, files are overwritten.')
def decompress(input_path, delete_source_file=False, output_dir=None, recalc_timestamp=False, overwrite=True):
    """
Converts WOFF/WOFF2 files to OpenType format.

Output will be a ttf or otf file, depending on the webfont flavor (TTF or CFF).
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFont(f, recalcTimestamp=recalc_timestamp)
            if font.flavor is not None:
                ext = '.otf' if font.sfntVersion == 'OTTO' else '.ttf'
                output_file = makeOutputFileName(f, outputDir=output_dir, extension=ext, overWrite=overwrite)
                font.flavor = None
                font.save(output_file)
                click.secho('%s saved' % os.path.basename(output_file), fg='green')
                if delete_source_file:
                    os.remove(f)
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


cli = click.CommandCollection(sources=[fontToWebfont, webfontToFont, makeCSS], help="""
Web fonts related tools.
""")

import os

import click

from ftcli.Lib.Font import Font
from ftcli.Lib.utils import getFontsList, is_nth_bit_set, set_nth_bit, unset_nth_bit, makeOutputFileName


@click.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-ver', '--set-version', 'target_version', type=click.IntRange(1, 5), help='Updates OS/2.version value.')
@click.option('-wg', '--set-weight', type=click.IntRange(1, 1000), help='Sets the OS/2.usWeightClass value.')
@click.option('-wd', '--set-width', type=click.IntRange(1, 9), help='Sets the OS/2.usWidthClass value.')
@click.option('-el', '--embed-level', type=click.Choice(['0', '2', '4', '8']), default=None,
              help="""
Sets OS/2.fsType bits 0-3 (embedding level).

\b
0: Installable embedding
2: Restricted License embedding
4: Preview & Print embedding
8: Editable embedding

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
""")
@click.option('-ns', '--no-subsetting', type=click.Choice(['0', '1']),
              help="""
Sets or clears OS/2.fsType bit 8 (No subsetting).

When this bit is set, the font may not be subsetted prior to embedding. Other embedding restrictions specified in bits
0 to 3 and bit 9 also apply.
              """)
@click.option('-be', '--bitmap-embedding-only', type=click.Choice(['0', '1']),
              help="""
Sets or clears OS/2.fsType bit 9 (Bitmap embedding only).

When this bit is set, only bitmaps contained in the font may be embedded. No outline data may be embedded. If there are
no bitmaps available in the font, then the font is considered unembeddable and the embedding services will fail. Other
embedding restrictions specified in bits 0-3 and 8 also apply.
              """)
@click.option('-b/-nb', '--set-bold/--unset-bold', default=None,
              help='Sets or clears the bold bits (OS/2.fsSelection bit 5 and head.macStyle bit 0).')
@click.option('-i/-ni', '--set-italic/--unset-italic', default=None,
              help='Sets or clears the italic bits (OS/2.fsSelection bit 0 and head.macStyle bit 1).')
@click.option('-utm/-no-utm', '--set-use-typo-metrics/--unset-use-typo-metrics', default=None,
              help="""
Sets or clears the USE_TYPO_METRICS bit (OS/2.fsSelection bit 7).

If set, it is strongly recommended that applications use OS/2.sTypoAscender - OS/2.sTypoDescender + OS/2.sTypoLineGap
as the default line spacing for this font.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection
""")
@click.option('-wws/-no-wws', '--set-wws/--unset-wws', default=None,
              help="""
Sets or clears the WWS bit (OS/2.fsSelection bit 8).

If the OS/2.fsSelection bit is set, the font has 'name' table strings consistent with a weight/width/slope family
without requiring use of name IDs 21 and 22.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection

Also: https://typedrawers.com/discussion/3857/fontlab-7-windows-reads-exported-font-name-differently

""")
@click.option('-ob/-no-ob', '--set-oblique/--unset-oblique', default=None,
              help='Sets or clears the oblique bit (OS/2.fsSelection bit 9).')
@click.option('-ach', '--set-ach-vend-id', type=str,
              help='Sets the the OS/2.achVendID tag (vendor\'s four-character identifier).')
@click.option('--recalc-codepage-ranges', is_flag=True,
              help='Recalculates the OS/2.ulCodePageRange1 and OS/2.ulCodePageRange2 values.')
@click.option('--recalc-unicode-ranges', is_flag=True,
              help='Recalculates the OS/2.ulUnicodeRange1, OS/2.ulUnicodeRange2, OS/2.ulUnicodeRange3 '
                   'and OS/2.ulUnicodeRange4 values.')
@click.option('--recalc-us-max-context', is_flag=True, help='Recalculates the OS/2.usMaxContent value.')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True),
              help='The output directory where the output files are to be created. If it doesn\'t exist, will be'
                   'created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False,
              help='Keeps the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True,
              help='Overwrites existing output files or save them to a new file (numbers are appended at the end of '
                   'file name). By default, files are overwritten.')
def cli(input_path, target_version, set_width, set_weight, embed_level, no_subsetting, bitmap_embedding_only,
        recalc_unicode_ranges, set_ach_vend_id, set_bold, set_italic, recalc_codepage_ranges, set_use_typo_metrics,
        set_wws, set_oblique, recalc_timestamp, recalc_us_max_context, output_dir, overwrite):
    """
    A command line tool to edit OS/2 table.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalc_timestamp)
            fontInfo = font.getFontInfo()

            is_bold = font.isBold()
            is_italic = font.isItalic()
            is_oblique = font.isOblique()
            uses_typo_metrics = font.usesTypoMetrics()
            is_wws = font.isWWS()
            usWeightClass = font['OS/2'].usWeightClass
            usWidthClass = font['OS/2'].usWidthClass

            modified = False

            if target_version is not None:
                current_version = font['OS/2'].version
                target_version = target_version

                # Prevent updating to the same version.
                if target_version == current_version:
                    click.secho(f'{os.path.basename(f)}: OS/2 version is already {current_version}!', fg='yellow')
                    continue

                # Prevent version downgrade.
                elif target_version < current_version:
                    click.secho(f'{os.path.basename(f)}: current OS/2 version is {current_version}. '
                                f'Please, insert a value greater than {current_version}', fg='yellow')
                    continue
                else:
                    font.setOS2Version(target_version=target_version)
                    modified = True

            # usWeightClass
            if set_weight is not None:
                if usWeightClass != set_weight:
                    font['OS/2'].usWeightClass = set_weight
                    modified = True

            # usWidthClass
            if set_width is not None:
                if usWidthClass != set_width:
                    font['OS/2'].usWidthClass = set_width
                    modified = True

            # fsType bits 0-3 (embed level).
            if embed_level is not None:
                # Convert string to integer as first thing.
                embed_level = int(embed_level)
                current_value = font.getEmbedLevel()
                print(repr(embed_level), repr(current_value))
                if not embed_level == current_value:
                    font.setEmbedLevel(embed_level)
                    modified = True

            # fsType bit 8.
            if no_subsetting is not None:
                # Convert string to bool as first thing.
                no_subsetting = bool(int(no_subsetting))
                current_value = font.getNoSubsettingValue()
                if not no_subsetting == current_value:
                    modified = True
                    if no_subsetting is True:
                        font.setNoSubsettingBit()
                    if no_subsetting is False:
                        font.clearNoSubsettingBit()

            # fsType bit 9.
            if bitmap_embedding_only is not None:
                # Convert string to bool as first thing.
                bitmap_embedding_only = bool(int(bitmap_embedding_only))
                current_value = font.getBitmapEmbedOnlyValue()
                if not bitmap_embedding_only == current_value:
                    modified = True
                    if bitmap_embedding_only is True:
                        font.setBitmapEmbedOnlyBit()
                    if bitmap_embedding_only is False:
                        font.clearBitmapEmbedOnlyBit()

                # print(modified)

            # ulUnicodeRange(1-4) bits.
            if recalc_unicode_ranges is True:
                if not font['OS/2'].getUnicodeRanges() == font['OS/2'].recalcUnicodeRanges(font):
                    font['OS/2'].setUnicodeRanges(font['OS/2'].recalcUnicodeRanges(font))
                    modified = True

            # achVendId 4 characters string.
            if set_ach_vend_id:
                if len(set_ach_vend_id) > 4:
                    set_ach_vend_id = set_ach_vend_id[0:4]
                    click.secho('\nach_vend_id was longer than 4 characters, it has been truncated.', fg='yellow')
                if len(set_ach_vend_id) < 4:
                    set_ach_vend_id = str(set_ach_vend_id).ljust(4)
                if not set_ach_vend_id == font['OS/2'].achVendID:
                    font.setAchVendID(set_ach_vend_id)
                    modified = True

            # Italic bit: fsSelection bit 0 and, consequently, 'head'.macStyle bit 1.
            if set_italic is not None:
                if is_italic != set_italic:
                    if set_italic is True:
                        font.setItalic()
                    else:
                        font.unsetItalic()
                    modified = True

            # Bold bit: fsSelection bit 5 and, consequently, 'head'.macStyle bit 0.
            if set_bold is not None:
                if is_bold != set_bold:
                    if set_bold is True:
                        font.setBold()
                    else:
                        font.unsetBold()
                    modified = True

            # Use Typo Metrics bit: fsSelection bit 7.
            if set_use_typo_metrics is not None:
                if uses_typo_metrics != set_use_typo_metrics:
                    font['OS/2'].version = 4
                    if set_use_typo_metrics is True:
                        if font['OS/2'].version > 3:
                            font.setUseTypoMetrics()
                            modified = True
                        else:
                            click.secho("\nfsSelection bits 7 is only defined in OS/2 table version 4 and up."
                                        "Current version: {}".format(font['OS/2'].version), fg='red')
                    if set_use_typo_metrics is False:
                        font.unsetUseTypoMetrics()
                        modified = True

            # Is WWS consistent bit: fsSelection bit 8.
            if set_wws is not None:
                if is_wws != set_wws:
                    if set_wws is True:
                        font.setWWS()
                    else:
                        font.unsetWWS()

                    modified = True

            # Oblique bit: fsSelection bit 8.
            if set_oblique is not None:
                if is_oblique != set_oblique:
                    if set_oblique is True:
                        font.setOblique()
                    else:
                        font.unsetOblique()

                    modified = True

            # ulCodePageRange(1-2) bits.
            if recalc_codepage_ranges is True:
                ulCodePageRange1, ulCodePageRange2 = font.recalcCodePageRanges()
                os2_version = font['OS/2'].version

                # Check if OS/2.version is greater than 0.
                if os2_version < 1:
                    click.secho(f'{os.path.basename(f)} OS/2 table version is {os2_version}. '
                                f'ulCodePageRange1 and ulCodePageRange2 are only defined in OS/2 version 1 and up.',
                                fg='red')
                    continue

                # Check if for some reason ulCodePageRange1 is not present.
                if not hasattr(font['OS/2'], 'ulCodePageRange1'):
                    font['OS/2'].ulCodePageRange1 = ulCodePageRange1
                    modified = True
                else:
                    if not font['OS/2'].ulCodePageRange1 == ulCodePageRange1:
                        font['OS/2'].ulCodePageRange1 = ulCodePageRange1
                        modified = True

                # Check if for some reason ulCodePageRange2 is not present.
                if not hasattr(font['OS/2'], 'ulCodePageRange2'):
                    font['OS/2'].ulCodePageRange2 = ulCodePageRange2
                    modified = True
                else:
                    if not font['OS/2'].ulCodePageRange2 == ulCodePageRange2:
                        font['OS/2'].ulCodePageRange2 = ulCodePageRange2
                        modified = True

            # usMaxContext value.
            if recalc_us_max_context is True:
                if not font['OS/2'].usMaxContext == font.recalcUsMaxContext():
                    font['OS/2'].usMaxContext = font.recalcUsMaxContext()
                    modified = True

            # General options
            if output_dir is None:
                output_dir = os.path.dirname(f)
            else:
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)

            output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
            if modified is True:
                font.save(output_file)
                click.secho(f'{output_file} --> saved', fg='green')
            else:
                click.secho(f'{f} --> no changes made', fg='yellow')

        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')

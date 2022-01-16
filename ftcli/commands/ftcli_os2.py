import os

import click

from ftcli.Lib.Font import Font
from ftcli.Lib.utils import getFontsList, makeOutputFileName


@click.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-v', '--version', type=click.IntRange(1, 5), help='Updates OS/2 table version.')
@click.option('-wg', '--weight', type=click.IntRange(1, 1000), help='Sets usWeightClass value.')
@click.option('-wd', '--width', type=click.IntRange(1, 9), help='Sets usWidthClass value.')
@click.option('-el', '--embed-level', type=click.Choice(['0', '2', '4', '8']), default=None,
              help="""
Sets/clears fsType bits 0-3 (embedding level).

\b
0: Installable embedding
2: Restricted License embedding
4: Preview & Print embedding
8: Editable embedding

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
""")
@click.option('-ns', '--no-subsetting', type=click.Choice(['0', '1']),
              help="""
Sets or clears fsType bit 8 (No subsetting).

When this bit is set, the font may not be subsetted prior to embedding. Other embedding restrictions specified in bits
0-3 and 9 also apply.
              """)
@click.option('-beo', '--bitmap-embedding-only', type=click.Choice(['0', '1']),
              help="""
Sets or clears fsType bit 9 (Bitmap embedding only).

When this bit is set, only bitmaps contained in the font may be embedded. No outline data may be embedded. If there are
no bitmaps available in the font, then the font is considered unembeddable and the embedding services will fail. Other
embedding restrictions specified in bits 0-3 and 8 also apply.
              """)
@click.option('-i/-ni', '--italic/--no-italic', default=None,
              help='Sets or clears the italic bits (fsSelection bit 0 and head.macStyle bit 1).')
@click.option('-b/-nb', '--bold/--no-bold', default=None,
              help='Sets or clears the bold bits (fsSelection bit 5 and head.macStyle bit 0).')
@click.option('-r', '--regular', is_flag=True, default=None,
              help="""
Sets fsSelection bit 6 and clears bold (fsSelection bit 5, head.macStyle bit 0) and italic (fsSelection bit 0, 
head.macStyle bit 1) bits.
              """)
@click.option('-utm', '--use-typo-metrics', type=click.Choice(['0', '1']),
              help="""
Sets or clears the USE_TYPO_METRICS bit (fsSelection bit 7).

If set, it is strongly recommended that applications use OS/2.sTypoAscender - OS/2.sTypoDescender + OS/2.sTypoLineGap
as the default line spacing for this font.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection
""")
@click.option('-wws', '--wws-consistent', type=click.Choice(['0', '1']),
              help="""
Sets or clears the WWS bit (fsSelection bit 8).

If the OS/2.fsSelection bit is set, the font has 'name' table strings consistent with a weight/width/slope family
without requiring use of name IDs 21 and 22.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection

Also: https://typedrawers.com/discussion/3857/fontlab-7-windows-reads-exported-font-name-differently

""")
@click.option('-ob', '--oblique', type=click.Choice(['0', '1']),
              help='Sets or clears the OBLIQUE bit (fsSelection bit 9).')
@click.option('-ach', '--ach-vend-id', type=str,
              help='Sets the achVendID tag (vendor\'s four-character identifier).')
@click.option('--recalc-unicode-ranges', is_flag=True,
              help='Recalculates the ulUnicodeRanges 1-4 values.')
@click.option('--recalc-codepage-ranges', is_flag=True,
              help='Recalculates ulCodePageRange 1-2 values.')
@click.option('--recalc-us-max-context', is_flag=True, help='Recalculates usMaxContext value.')
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
def cli(input_path, version, weight, width, embed_level, no_subsetting, bitmap_embedding_only, bold, italic, regular,
        use_typo_metrics, wws_consistent, oblique, ach_vend_id, recalc_unicode_ranges, recalc_codepage_ranges,
        recalc_us_max_context, output_dir, recalc_timestamp, overwrite):
    """
    Command line OS/2 table editor.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            # Add this control to save only modified files.
            modified = False
            font = Font(f, recalcTimestamp=recalc_timestamp)

            # OS/2 Table version.
            if version is not None:
                current_version = font['OS/2'].version

                # Prevent updating to the same version.
                if version == current_version:
                    click.secho(f'{os.path.basename(f)}: OS/2 version is already {current_version}!', fg='yellow')

                # Prevent version downgrade.
                elif version < current_version:
                    click.secho(f'{os.path.basename(f)}: current OS/2 version is {current_version}. '
                                f'Please, insert a value greater than {current_version}', fg='yellow')
                else:
                    font.setOS2Version(target_version=version)
                    modified = True

            # usWeightClass.
            if weight is not None:
                if font['OS/2'].usWeightClass != weight:
                    font['OS/2'].usWeightClass = weight
                    modified = True

            # usWidthClass.
            if width is not None:
                if font['OS/2'].usWidthClass != width:
                    font['OS/2'].usWidthClass = width
                    modified = True

            # Embed level: fsType bits 0-3.
            if embed_level is not None:
                # Convert string to integer as first thing.
                embed_level = int(embed_level)
                current_value = font.getEmbedLevel()
                if not embed_level == current_value:
                    font.setEmbedLevel(embed_level)
                    modified = True

            # No Subsetting: fsType bit 8.
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

            # Bitmap Embedding Only: fsType bit 9.
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

            # Italic bit: fsSelection bit 0 and, consequently, 'head'.macStyle bit 1.
            if italic is not None:
                if font.isItalic() != italic:
                    if italic is True:
                        font.setItalic()
                    else:
                        font.unsetItalic()
                    modified = True

            # Bold bit: fsSelection bit 5 and, consequently, 'head'.macStyle bit 0.
            if bold is not None:
                if font.isBold() != bold:
                    if bold is True:
                        font.setBold()
                    else:
                        font.unsetBold()
                    modified = True

            # Regular: fsSelection bit 6.
            if regular is not None:
                # Prevent from using -r with -b or -i
                if bold or italic:
                    print("\nThe -r/--regular switch can't be used in conjunction with -b/--bold or -i/--italic.")
                    break
                if font.isRegular() is False:
                    font.setRegular()
                    modified = True

            # Use Typo Metrics: fsSelection bit 7.
            if use_typo_metrics is not None:
                # Convert string to bool as first thing.
                use_typo_metrics=bool(int(use_typo_metrics))
                if font.usesTypoMetrics() != use_typo_metrics:
                    font['OS/2'].version = 4
                    if use_typo_metrics is True:
                        if font['OS/2'].version > 3:
                            font.setUseTypoMetrics()
                            modified = True
                        else:
                            click.secho("fsSelection bits 7 is only defined in OS/2 table version 4 and up."
                                        "Current version: {}".format(font['OS/2'].version), fg='yellow')
                    if use_typo_metrics is False:
                        font.unsetUseTypoMetrics()
                        modified = True

            # WWS consistent: fsSelection bit 8.
            if wws_consistent is not None:
                # Convert string to bool as first thing.
                wws_consistent = bool(int(wws_consistent))
                if font.isWWS() != wws_consistent:
                    if wws_consistent is True:
                        font.setWWS()
                    else:
                        font.unsetWWS()
                    modified = True

            # Oblique: fsSelection bit 8.
            if oblique is not None:
                # Convert string to bool as first thing.
                oblique = bool(int(oblique))
                if font.isOblique() != oblique:
                    if oblique is True:
                        font.setOblique()
                    else:
                        font.unsetOblique()

                    modified = True

            # achVendId 4 characters string.
            if ach_vend_id:
                if len(ach_vend_id) > 4:
                    ach_vend_id = ach_vend_id[0:4]
                    click.secho('ach_vend_id was longer than 4 characters, it has been truncated.', fg='yellow')
                if len(ach_vend_id) < 4:
                    ach_vend_id = str(ach_vend_id).ljust(4)
                if not ach_vend_id == font['OS/2'].achVendID:
                    font.setAchVendID(ach_vend_id)
                    modified = True

            # ulUnicodeRange1-4 bits.
            if recalc_unicode_ranges is True:
                if not font['OS/2'].getUnicodeRanges() == font['OS/2'].recalcUnicodeRanges(font):
                    font['OS/2'].setUnicodeRanges(font['OS/2'].recalcUnicodeRanges(font))
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

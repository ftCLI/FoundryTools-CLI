import os
from copy import copy

import click
from afdko.fdkutils import run_shell_command
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import check_output_dir, check_input_path
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    file_saved_message,
    file_not_changed_message,
    generic_error_message,
    generic_warning_message,
)


@click.command()
@add_file_or_path_argument()
@click.option(
    "-ver",
    "--version",
    type=click.IntRange(1, 5),
    help="Upgrades `OS/2` table version.",
)
@click.option("-wgh", "--weight", type=click.IntRange(1, 1000), help="Sets `usWeightClass` value.")
@click.option("-wdt", "--width", type=click.IntRange(1, 9), help="Sets `usWidthClass` value.")
@click.option(
    "-it/-no-it",
    "--italic/--no-italic",
    default=None,
    help="Sets or clears the ITALIC bits (`fsSelection` bit 0 and `head` table `macStyle` bit 1).",
)
@click.option(
    "-bd/-no-bd",
    "--bold/--no-bold",
    default=None,
    help="Sets or clears the BOLD bits (`OS/2.fsSelection` bit 5 and `head.macStyle` bit 0).",
)
@click.option(
    "-rg",
    "--regular",
    is_flag=True,
    default=None,
    help="""
Sets REGULAR (`fsSelection` bit) 6 and clears BOLD (`fsSelection` bit 5, `head.macStyle` bit 0) and ITALIC
(`fsSelection` bit 0, `head.macStyle` bit 1) bits. This is equivalent to `--no-bold --no-italic`.
              """,
)
@click.option(
    "-obl/-no-obl",
    "--oblique/--no-oblique",
    default=None,
    help="Sets or clears the OBLIQUE bit (`fsSelection` bit 9).",
)
@click.option(
    "-utm/-no-utm",
    "--use-typo-metrics/--no-use-typo-metrics",
    default=None,
    help="""
Sets or clears the USE_TYPO_METRICS bit (`fsSelection` bit 7).

If set, it is strongly recommended that applications use `OS/2.sTypoAscender` - `OS/2.sTypoDescender` + 
`OS/2.sTypoLineGap` as the default line spacing for the font.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection
""",
)
@click.option(
    "-wws/-no-wws",
    "--wws-consistent/--no-wws-consistent",
    default=None,
    help="""
Sets or clears the WWS bit (`fsSelection` bit 8).

If the `OS/2.fsSelection` bit is set, the font has `name` table strings consistent with a weight/width/slope family
without requiring use of name IDs 21 and 22.

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection

Also: https://typedrawers.com/discussion/3857/fontlab-7-windows-reads-exported-font-name-differently
""",
)
@click.option(
    "-vend",
    "--ach-vend-id",
    type=str,
    default=None,
    help="""
Sets the `achVendID` tag (vendor's four-character identifier).
""",
)
@click.option(
    "-el",
    "--embed-level",
    type=click.Choice(["0", "2", "4", "8"]),
    default=None,
    help="""
Sets/clears `fsType` bits 0-3 (EMBEDDING_LEVEL).

\b
0: Installable embedding
2: Restricted License embedding
4: Preview & Print embedding
8: Editable embedding

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
""",
)
@click.option(
    "-ns/-as",
    "--no-subsetting/--allow-subsetting",
    default=None,
    help="""
Sets or clears `fsType` bit 8 (NO_SUBSETTING).

When this bit is set, the font may not be subsetted prior to embedding. Other embedding restrictions specified in bits
0-3 and 9 also apply.
              """,
)
@click.option(
    "-beo/-no-beo",
    "--bitmap-embedding-only/--no-bitmap-embedding-only",
    default=None,
    help="""
Sets or clears `fsType` bit 9 (BITMAP_EMBEDDING_ONLY).

When this bit is set, only bitmaps contained in the font may be embedded. No outline data may be embedded. If there are
no bitmaps available in the font, then the font is considered unembeddable and the embedding services will fail. Other
embedding restrictions specified in bits 0-3 and 8 also apply.
              """,
)
@click.option(
    "--recalc-unicode-ranges",
    is_flag=True,
    default=None,
    help="Recalculates the `ulUnicodeRange*` values.",
)
@click.option(
    "--recalc-codepage-ranges",
    is_flag=True,
    default=None,
    help="Recalculates `ulCodePageRange1` and `ulCodePageRange2` values.",
)
@click.option(
    "--recalc-x-height",
    is_flag=True,
    default=None,
    help="Recalculates `sxHeight` value.",
)
@click.option(
    "--recalc-cap-height",
    is_flag=True,
    default=None,
    help="Recalculates `sCapHeight` value.",
)
@click.option(
    "--recalc-italic-bits",
    is_flag=True,
    default=None,
    help="""
              Sets or clears the italic bits in OS/2.fsSelection and in head.macStyle, according to the `italicAngle`
              value in `post` table. If `italicAngle` value is other than 0.0, italic bits will be set. If `italicAngle`
              value is 0.0, italic bits will be cleared.
              """,
)
@click.option(
    "--recalc-max-context",
    is_flag=True,
    default=None,
    help="Recalculates `usMaxContext` value.",
)
@click.option(
    "--import-unicodes",
    "unicodes_source_font",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    default=None,
    help="Imports `ulUnicodeRanges*` from a source font.",
)
@add_common_options()
def cli(input_path, recalcTimestamp, outputDir, overWrite, **kwargs):
    """Command line OS/2 table editor."""

    params = {k: v for k, v in kwargs.items() if v is not None}

    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)

            # Using copy instead of deepcopy and avoiding to compile OS/2 tables is faster
            os_2_table_copy = copy(font.os_2_table)

            # Changing bold and italic bits involves `head` table too
            head_table_copy = copy(font.head_table)

            # Upgrade version as first to avoid warning messages from fontTools
            if "version" in params.keys():
                if not font.os_2_table.version < params.get("version"):
                    generic_warning_message(
                        f"OS/2 target version ({font.os_2_table.version}) must be greater than current version ("
                        f"{font.os_2_table.version})."
                    )
                else:
                    font.upgrade_os2_version(target_version=params.get("version"))

            if "use_typo_metrics" in params.keys():
                if font.os_2_table.version < 4:
                    generic_warning_message(
                        "fsSelection bit 7 (USE_TYPO_METRICS) is only defined in OS/2 version 4 and up."
                    )
                else:
                    use_typo_metrics = params.get("use_typo_metrics")
                    if use_typo_metrics is True:
                        font.os_2_table.set_use_typo_metrics_bit()
                    else:
                        font.os_2_table.clear_use_typo_metrics_bit()

            if "wws_consistent" in params.keys():
                if font.os_2_table.version < 4:
                    generic_warning_message("fsSelection bit 8 (WWS) is only defined in OS/2 version 4 and up.")
                else:
                    wws_consistent = params.get("wws_consistent")
                    if wws_consistent is True:
                        font.os_2_table.set_wws_bit()
                    else:
                        font.os_2_table.clear_wws_bit()

            if "recalc_codepage_ranges" in params.keys():
                if font.os_2_table.version == 0:
                    generic_warning_message("codepage ranges are only defined in OS/2 version 1 and up.")
                else:
                    codepage_ranges = font.calculate_codepage_ranges()
                    font.os_2_table.set_codepage_ranges(codepage_ranges)

            if "recalc_x_height" in params.keys():
                if font.os_2_table.version < 2:
                    generic_warning_message("sxHeight is only defined in OS/2 version 2 and up.")
                else:
                    x_height = font.calculate_x_height()
                    font.os_2_table.set_x_height(x_height)

            if "recalc_cap_height" in params.keys():
                if font.os_2_table.version < 2:
                    generic_warning_message("sCapHeight is only defined in OS/2 version 2 and up.")
                else:
                    cap_height = font.calculate_cap_height()
                    font.os_2_table.set_cap_height(cap_height)

            if "recalc_max_context" in params.keys():
                if font.os_2_table.version < 2:
                    generic_warning_message("usMaxContext is only defined in OS/2 version 2 and up.")
                else:
                    max_context = font.calculate_max_context()
                    font.os_2_table.set_max_context(max_context)

            if "weight" in params.keys():
                font.os_2_table.set_weight_class(params.get("weight"))

            if "width" in params.keys():
                font.os_2_table.set_width_class(params.get("width"))

            if "ach_vend_id" in params.keys():
                ach_vend_id = params.get("ach_vend_id")
                font.os_2_table.set_ach_vend_id(ach_vend_id)

            # fsSelection

            if "bold" in params.keys():
                bold = params.get("bold")
                if bold is True:
                    font.set_bold()
                else:
                    font.unset_bold()

            if "italic" in params.keys():
                italic = params.get("italic")
                if italic is True:
                    font.set_italic()
                else:
                    font.unset_italic()

            if "regular" in params.keys():
                font.set_regular()

            if "oblique" in params.keys():
                oblique = params.get("oblique")
                if oblique is True:
                    font.set_oblique()
                else:
                    font.unset_oblique()

            # fsType

            if "embed_level" in params.keys():
                embed_level = int(params.get("embed_level"))
                font.os_2_table.set_embed_level(embed_level)

            if "no_subsetting" in params.keys():
                no_subsetting = params.get("no_subsetting")
                if no_subsetting is True:
                    font.os_2_table.set_no_subsetting_bit()
                else:
                    font.os_2_table.clear_no_subsetting_bit()

            if "bitmap_embedding_only" in params.keys():
                bitmap_embedding_only = params.get("bitmap_embedding_only")
                if bitmap_embedding_only is True:
                    font.os_2_table.set_bitmap_embed_only_bit()
                else:
                    font.os_2_table.clear_bitmap_embed_only_bit()

            if "recalc_unicode_ranges" in params.keys():
                # fontTools way, too permissive
                # unicode_ranges = font.os_2_table.recalcUnicodeRanges(font)

                temp_t1_file = makeOutputFileName(output_file, outputDir=output_dir, extension=".t1", overWrite=True)
                command = ["tx", "-t1", file, temp_t1_file]
                run_shell_command(command, suppress_output=True)

                temp_otf_file = makeOutputFileName(output_file, outputDir=output_dir, suffix="_tmp", overWrite=True)
                command = ["makeotf", "-f", temp_t1_file, "-o", temp_otf_file]
                run_shell_command(command, suppress_output=True)

                temp_font = Font(temp_otf_file)
                unicode_ranges = temp_font.os_2_table.getUnicodeRanges()
                temp_font.close()
                os.remove(temp_t1_file)
                os.remove(temp_otf_file)

                font.os_2_table.setUnicodeRanges(unicode_ranges)

            if "recalc_italic_bits" in params.keys():
                font.calculate_italic_bits()

            if "unicodes_source_font" in params.keys():
                try:
                    source_font = Font(params.get("unicodes_source_font"))
                    source_unicode_ranges = source_font.os_2_table.getUnicodeRanges()
                    font.os_2_table.setUnicodeRanges(source_unicode_ranges)
                except Exception as e:
                    click.secho(
                        f"An error occurred while importing unicode ranges from file "
                        f"{params.get('unicodes_source_font')}: {e}",
                        fg="red",
                    )

            # Check if tables have changed before saving the font. No need to compile here.
            if (font.os_2_table != os_2_table_copy) or (font.head_table != head_table_copy):
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)

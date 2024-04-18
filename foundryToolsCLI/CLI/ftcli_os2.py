import os
from copy import deepcopy, copy
from pathlib import Path
from typing import Optional

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.tables.OS_2 import TableOS2
from foundryToolsCLI.Lib.utils.bits_tools import unset_nth_bit
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_recursive_option,
    add_common_options,
)
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.timer import Timer

tbl_os2 = click.Group("subcommands")


@tbl_os2.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def recalc_x_height(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Recalculates sxHeight value.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            os_2: TableOS2 = font["OS/2"]
            if os_2.version < 2:
                logger.warning(Logs.x_height_not_defined, version=os_2.version)
                logger.skip(Logs.file_not_changed, file=file)
                continue

            current = os_2.sxHeight
            x_height = font.recalc_x_height()
            if current == x_height:
                logger.skip(Logs.file_not_changed, file=file)
                continue

            os_2.set_x_height(x_height)
            font.save(output_file)
            logger.success(Logs.file_saved, file=output_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def recalc_cap_height(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Recalculates sCapHeight value.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            os_2: TableOS2 = font["OS/2"]
            if os_2.version < 2:
                logger.warning(Logs.cap_height_not_defined, version=os_2.version)
                logger.skip(Logs.file_not_changed, file=file)
                continue

            current = os_2.sCapHeight
            cap_height = font.recalc_cap_height()
            if current == cap_height:
                logger.skip(Logs.file_not_changed, file=file)
                continue

            os_2.set_cap_height(cap_height)
            font.save(output_file)
            logger.success(Logs.file_saved, file=output_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def recalc_avg_width(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Recalculates xAvgCharWidth value.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            os_2: TableOS2 = font["OS/2"]

            current = os_2.xAvgCharWidth
            avg_char_width = font.recalc_avg_char_width()
            if current == avg_char_width:
                logger.skip(Logs.file_not_changed, file=file)
                continue

            os_2.xAvgCharWidth = avg_char_width
            font.save(output_file)
            logger.success(Logs.file_saved, file=output_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def recalc_max_context(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Recalculates usMaxContext value.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            os_2: TableOS2 = font["OS/2"]

            if os_2.version < 2:
                logger.warning(Logs.max_context_not_defined, version=os_2.version)
                logger.skip(Logs.file_not_changed, file=file)
                continue

            current = os_2.usMaxContex
            max_context = font.recalc_max_context()
            if current == max_context:
                logger.skip(Logs.file_not_changed, file=file)
                continue

            os_2.usMaxContext = max_context

            font.save(output_file)
            logger.success(Logs.file_saved, file=output_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def recalc_ranges(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Generates a temporary Type 1 from the font file using tx, converts that to an OpenType font using makeotf, reads the
    Unicode ranges and codepage ranges from the temporary OpenType font file, and then writes those ranges to the
    original font's OS/2 table.
    """

    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            temp_otf_fd, temp_otf_file = font.make_temp_otf()
            temp_font = Font(temp_otf_file)

            os_2: TableOS2 = font["OS/2"]
            os_2_temp: TableOS2 = temp_font["OS/2"]
            current_unicode_ranges = os_2.getUnicodeRanges()
            current_codepage_ranges = os_2.get_codepage_ranges()
            new_unicode_ranges = os_2_temp.getUnicodeRanges()
            new_codepage_ranges = os_2_temp.get_codepage_ranges()

            if (
                current_unicode_ranges != new_unicode_ranges
                or current_codepage_ranges != new_codepage_ranges
            ):
                os_2.setUnicodeRanges(bits=new_unicode_ranges)
                os_2.set_codepage_ranges(codepage_ranges=new_codepage_ranges)
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

            temp_font.close()
            os.close(temp_otf_fd)
            os.remove(temp_otf_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@click.option(
    "-it/-no-it",
    "--italic/--no-italic",
    "italic",
    default=None,
    help="Sets or clears the ITALIC bits (`fsSelection` bit 0 and `head` table `macStyle` bit 1).",
)
@click.option(
    "-us/-no-us",
    "--underscore/--no-underscore",
    "underscore",
    default=None,
    help="""
Sets or clears `fsType` bit 1 (UNDERSCORE).
""",
)
@click.option(
    "-ng/-no-ng",
    "--negative/--no-negative",
    "negative",
    default=None,
    help="""
Sets or clears `fsType` bit 2 (NEGATIVE).
""",
)
@click.option(
    "-ol/-no-ol",
    "--outlined/--no-outlined",
    "outlined",
    default=None,
    help="""
Sets or clears `fsType` bit 3 (OUTLINED).
""",
)
@click.option(
    "-st/-no-st",
    "--strikeout/--no-strikeout",
    "strikeout",
    default=None,
    help="""
Sets or clears `fsType` bit 4 (STRIKEOUT).
""",
)
@click.option(
    "-bd/-no-bd",
    "--bold/--no-bold",
    "bold",
    default=None,
    help="Sets or clears the BOLD bits (`OS/2.fsSelection` bit 5 and `head.macStyle` bit 0).",
)
@click.option(
    "-rg",
    "--regular",
    "regular",
    is_flag=True,
    default=None,
    help="""
Sets REGULAR (`fsSelection` bit 6) and clears BOLD (`fsSelection` bit 5, `head.macStyle` bit 0) and ITALIC
(`fsSelection` bit 0, `head.macStyle` bit 1) bits. This is equivalent to `--no-bold --no-italic`.
""",
)
@click.option(
    "-utm/-no-utm",
    "--use-typo-metrics/--no-use-typo-metrics",
    "use_typo_metrics",
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
    "wws_consistent",
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
    "-obl/-no-obl",
    "--oblique/--no-oblique",
    "oblique",
    default=None,
    help="Sets or clears the OBLIQUE bit (`fsSelection` bit 9).",
)
@click.option(
    "-el",
    "--embed-level",
    "embed_level",
    type=click.Choice(["0", "2", "4", "8"]),
    default=None,
    help="""
Sets/clears `fsType` bits 0-3 (EMBEDDING_LEVEL).

Valid fonts must set at most one of bits 1, 2 or 3; bit 0 is permanently reserved and must be zero. Valid values for
this sub-field are 0, 2, 4 or 8. The meaning of these values is as follows:

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
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def set_flags(
    input_path: Path,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    **kwargs,
):
    """
    Sets/clears the following flags in OS/2.fsSelection and OS/2.fsType fields:

    fsSelection:

    \b
    Bit 0: ITALIC
    Bit 1: UNDERSCORE
    Bit 2: NEGATIVE
    Bit 3: OUTLINED
    Bit 4: STRIKEOUT
    Bit 5: BOLD
    Bit 6: REGULAR
    Bit 7: USE_TYPO_METRICS
    Bit 8: WWS
    Bit 9: OBLIQUE

    fsType:

    \b
    Bits 0-3: Usage permissions
    Bit 8: No subsetting
    Bit 9: Bitmap embedding only
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    params = {k: v for k, v in kwargs.items() if v is not None}
    if len(params) == 0:
        logger.error(Logs.no_parameter)
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            head = font["head"]
            head_copy = deepcopy(head)
            os2 = font["OS/2"]
            os2_copy = deepcopy(os2)

            for flag, value in params.items():
                if flag in ("use_typo_metrics", "wws_consistent", "oblique") and os2.version < 4:
                    logger.warning(Logs.bits_7_8_9_not_defined, flag=flag, version=os2.version)
                    continue
                if flag == "embed_level":
                    value = int(value)
                set_flag = getattr(font, f"set_{flag}_flag")
                set_flag(value)

            if head_copy.compile(font) != head.compile(font) or os2_copy.compile(
                font
            ) != os2.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_os2.command()
@click.option(
    "-v", "target_version", type=click.IntRange(1, 5), required=True, help="Target version"
)
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def set_version(
    input_path: Path,
    target_version: int,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Upgrades OS/2 table version.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            os_2: TableOS2 = font["OS/2"]
            current_version = getattr(os_2, "version")

            if target_version <= current_version:
                logger.warning(f"Current OS/2 table version is already {current_version}")
                logger.skip(Logs.file_not_changed, file=file)
                continue

            setattr(os_2, "version", target_version)

            # When upgrading from version 0, ulCodePageRanges are to be recalculated.
            if current_version < 1:
                temp_otf_fd, temp_otf_file = font.make_temp_otf()
                temp_otf_font = Font(temp_otf_file)
                temp_os_2: TableOS2 = temp_otf_font["OS/2"]
                os_2.set_codepage_ranges(temp_os_2.get_codepage_ranges())

                temp_otf_font.close()
                os.close(temp_otf_fd)
                os.remove(temp_otf_file)

            # Return if upgrading from version 0 to version 1.
            if target_version == 1:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
                continue

            # Upgrading from version 1 requires creating sxHeight, sCapHeight, usDefaultChar, usBreakChar and
            # usMaxContext entries.
            if current_version < 2:
                os_2.set_x_height(font.recalc_x_height())
                os_2.set_cap_height(font.recalc_cap_height())
                os_2.set_default_char(0)
                os_2.set_break_char(32)
                max_context = font.recalc_max_context()
                if max_context is not None:
                    os_2.set_max_context(max_context)

            # Write default values if target_version == 5.
            if target_version > 4:
                setattr(os_2, "usLowerOpticalPointSize", 0)
                setattr(os_2, "usUpperOpticalPointSize", 65535 / 20)

            # Finally, make sure to clear bits 7, 8 and 9 in ['OS/2'].fsSelection when target version is lower than 4.
            if target_version < 4:
                for b in (7, 8, 9):
                    setattr(os_2, "fsSelection", unset_nth_bit(os_2.fsSelection, b))

            font.save(output_file)
            logger.success(Logs.file_saved, file=output_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_os2.command()
@add_file_or_path_argument()
@click.option(
    "--family-type", "bFamilyType", type=click.IntRange(0, 5), help="Sets 'bFamilyType' value"
)
@click.option(
    "--serif-style", "bSerifStyle", type=click.IntRange(0, 15), help="Sets 'bSerifStyle' value"
)
@click.option("--weight", "bWeight", type=click.IntRange(0, 11), help="Sets 'bWeight' value")
@click.option(
    "--proportion", "bProportion", type=click.IntRange(0, 9), help="Sets 'bProportion' value"
)
@click.option("--contrast", "bContrast", type=click.IntRange(0, 9), help="Sets 'bContrast' value")
@click.option(
    "--stroke-variation",
    "bStrokeVariation",
    type=click.IntRange(0, 9),
    help="Sets 'bStrokeVariation' value",
)
@click.option("--arm-style", "bArmStyle", type=click.IntRange(0, 11), help="Sets 'bArmStyle' value")
@click.option(
    "--letter-form", "bLetterForm", type=click.IntRange(0, 15), help="Sets 'bLetterForm' value"
)
@click.option("--midline", "bMidline", type=click.IntRange(0, 13), help="Sets 'bMidline' value")
@click.option("--x-height", "bXHeight", type=click.IntRange(0, 7), help="Sets 'bXHeight' value")
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def panose(
    input_path: Path,
    recalc_timestamp,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    **kwargs,
):
    """
    Command line panose editor.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    params = {k: v for k, v in kwargs.items() if v is not None}
    if len(params) == 0:
        logger.error(Logs.no_parameter)
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            os2_table: TableOS2 = font["OS/2"]
            panose_src = os2_table.panose
            panose_copy = copy(panose_src)

            for k, v in params.items():
                setattr(panose_src, k, v)

            if panose_copy.__dict__ != panose_src.__dict__:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@tbl_os2.command(no_args_is_help=True)
@add_file_or_path_argument()
@click.option(
    "-wght",
    "--weight",
    "usWeightClass",
    type=click.IntRange(1, 1000),
    help="Sets the ``usWeightClass`` value",
)
@click.option(
    "-wdth",
    "--width",
    "usWidthClass",
    type=click.IntRange(1, 9),
    help="Sets the ``usWidthClass`` value",
)
@click.option(
    "-tasc",
    "--typo-ascender",
    "sTypoAscender",
    type=int,
    help="Sets the ``sTypoAscender`` value",
)
@click.option(
    "-tdsc",
    "--typo-descender",
    "sTypoDescender",
    type=int,
    help="Sets the ``sTypoDescender`` value",
)
@click.option(
    "-tlg",
    "--typo-line-gap",
    "sTypoLineGap",
    type=int,
    help="Sets the ``sTypoLineGap`` value",
)
@click.option(
    "-wasc",
    "--win-ascent",
    "usWinAscent",
    type=int,
    help="Sets the ``usWinAscent`` value",
)
@click.option(
    "-wdsc",
    "--win-descent",
    "usWinDescent",
    type=int,
    help="Sets the ``usWinDescent`` value",
)
@click.option(
    "-xhgt",
    "--x-height",
    "sxHeight",
    type=int,
    help="Sets the ``sxHeight`` value",
)
@click.option(
    "-chgt",
    "--cap-height",
    "sCapHeight",
    type=int,
    help="Sets the ``sCapHeight`` value",
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def set_attrs(
    input_path: Path,
    recalc_timestamp: bool = False,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    **kwargs,
):
    """
    Command line OS/2 table editor.
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            os2_table: TableOS2 = font["OS/2"]
            os2_copy = copy(os2_table)

            for k, v in kwargs.items():
                if v is not None:
                    setattr(os2_table, k, v)

            if os2_copy.compile(font) != os2_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[tbl_os2],
    help="""
    A set of tools to manipulate the 'OS/2' table.
    """,
)

from pathlib import Path
from typing import Any, Optional, Union

import click
from fontTools.misc.roundTools import otRound
from foundrytools import Font
from foundrytools.core.tables.os_2 import InvalidOS2VersionError

from foundrytools_cli.utils import BaseCommand, choice_to_int_callback, ensure_at_least_one_param
from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing the ``OS/2`` table.")


@cli.command("recalc-avg-width", cls=BaseCommand)
def recalc_avg_char_width(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Recalculates the xAvgCharWidth value of the OS/2 table.
    """

    def task(font: Font) -> bool:
        font.t_os_2.table.recalcAvgCharWidth(font.ttfont)
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-x-height", cls=BaseCommand)
@click.option(
    "-gn",
    "--glyph-name",
    default="x",
    help="The glyph name to use for calculating the x-height. Default is 'x'.",
)
def recalc_x_height(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Recalculates the sxHeight value of the OS/2 table.
    """

    def task(font: Font, glyph_name: str = "x") -> bool:
        font.t_os_2.x_height = otRound(font.get_glyph_bounds(glyph_name)["y_max"])
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-cap-height", cls=BaseCommand)
@click.option(
    "-gn",
    "--glyph-name",
    default="H",
    help="The glyph name to use for calculating the cap height. Default is 'H'.",
)
def recalc_cap_height(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Recalculates the sCapHeight value of the OS/2 table.
    """

    def task(font: Font, glyph_name: str = "H") -> bool:
        font.t_os_2.cap_height = otRound(font.get_glyph_bounds(glyph_name)["y_max"])
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-max-context", cls=BaseCommand)
def recalc_max_context(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Recalculates the usMaxContext value of the OS/2 table.
    """

    def task(font: Font) -> bool:
        font.t_os_2.recalc_max_context()
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-codepage-ranges", cls=BaseCommand)
def recalc_codepage_ranges(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Recalculates the ulCodePageRange values of the OS/2 table.
    """

    def task(font: Font) -> bool:
        font.t_os_2.recalc_code_page_ranges()
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-unicode-ranges", cls=BaseCommand)
@click.option(
    "-p",
    "--percentage",
    type=click.FloatRange(0.0001, 100),
    default=33.0,
    help="Minimum percentage of coverage required for a Unicode range to be enabled.",
)
def recalc_unicode_ranges(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Recalculates the ulUnicodeRange values of the OS/2 table based on a minimum percentage of
    coverage.
    """

    def task(font: Font, percentage: float = 33) -> bool:
        result = font.t_os_2.recalc_unicode_ranges(percentage=percentage)
        if result:
            for block in result:
                logger.info(f"({block[0]}) {block[1]}: {block[2]}")
            return True
        return False

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-attrs", cls=BaseCommand)
@click.option(
    "-wght",
    "--weight-class",
    type=click.IntRange(1, 1000),
    help="""
    The new ``usWeightClass`` value.

    Indicates the visual weight (degree of blackness or thickness of strokes) of the
    characters in the font. Values from 1 to 1000 are valid.
    """,
)
@click.option(
    "-wdth",
    "--width-class",
    type=click.IntRange(1, 9),
    help="""
    The new ``usWidthClass`` value.

    Indicates a relative change from the normal aspect ratio (width to height ratio) as
    specified by a font designer for the glyphs in a font.
    """,
)
@click.option(
    "-vid",
    "--vendor-id",
    type=click.STRING,
    help="""
    The new ``achVendID`` value.

    The four-character identifier for the vendor of the given type face.
    """,
)
@click.option(
    "-tasc",
    "--typo-ascender",
    type=click.INT,
    help="""
    The new ``sTypoAscender`` value.

    The typographic ascender of the font. This field should be combined with the
    ``sTypoDescender`` and ``sTypoLineGap`` values to determine default line spacing.
    """,
)
@click.option(
    "-tdsc",
    "--typo-descender",
    type=click.INT,
    help="""
    The new ``sTypoDescender`` value.

    The typographic descender of the font. This field should be combined with the
    ``sTypoAscender`` and ``sTypoLineGap`` values to determine default line spacing.
    """,
)
@click.option(
    "-tlg",
    "--typo-line-gap",
    type=click.INT,
    help="""
    The new ``sTypoLineGap`` value.

    The typographic line gap of the font. This field should be combined with the
    ``sTypoAscender`` and ``sTypoDescender`` values to determine default line spacing.
    """,
)
@click.option(
    "-wasc",
    "--win-ascent",
    type=click.INT,
    help="""
    The new ``usWinAscent`` value.

    This field represents the “Windows ascender” metric. This should be used to specify the
    height above the baseline for a clipping region.
    """,
)
@click.option(
    "-wdsc",
    "--win-descent",
    type=click.INT,
    help="""
    The new ``usWinDescent`` value.

    This field represents the “Windows descender” metric. This should be used to specify the
    depth below the baseline for a clipping region.
    """,
)
@click.option(
    "-xhgt",
    "--x-height",
    type=click.INT,
    help="""
    The new ``sxHeight`` value.

    This metric specifies the distance between the baseline and the approximate height of
    non-ascending lowercase letters measured in FUnits. This value would normally be
    specified by a type designer but in situations where that is not possible, for example
    when a legacy font is being converted, the value may be set equal to the top of the
    unscaled and unhinted glyph bounding box of the glyph encoded at U+0078 (LATIN SMALL
    LETTER X). If no glyph is encoded in this position the field should be set to 0.

    This metric, if specified, can be used in font substitution: the xHeight value of one
    font can be scaled to approximate the apparent size of another.

    This field was defined in version 2 of the ``OS/2`` table.
    """,
)
@click.option(
    "-chgt",
    "--cap-height",
    type=click.INT,
    help="""
    The new ``sCapHeight`` value.

    This metric specifies the distance between the baseline and the approximate height of
    uppercase letters measured in FUnits. This value would normally be specified by a type
    designer but in situations where that is not possible, for example when a legacy font
    is being converted, the value may be set equal to the top of the unscaled and unhinted
    glyph bounding box of the glyph encoded at U+0048 (LATIN CAPITAL LETTER H). If no glyph
    is encoded in this position the field should be set to 0.

    This metric, if specified, can be used in systems that specify type size by capital
    height measured in millimeters. It can also be used as an alignment metric; the top of a
    drop capital, for instance, can be aligned to the sCapHeight metric of the first line of
    text.

    This field was defined in version 2 of the ``OS/2`` table.
    """,
)
def set_attrs(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Sets miscellaneous attributes of the 'OS/2' table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: dict[str, Optional[Union[int, float, str, bool]]]) -> bool:
        for attr, value in kwargs.items():
            if value is not None:
                try:
                    setattr(font.t_os_2, attr, value)
                except (ValueError, InvalidOS2VersionError) as e:
                    logger.warning(f"Error setting {attr} to {value}: {e}")
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("fsselection", cls=BaseCommand)
@click.option(
    "-it/-no-it",
    "--italic/--no-italic",
    "italic",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 0 (ITALIC).

    The bit 1 of the ``macStyle`` field in the ``head`` table will be set to the same value
    as bit 0 in the fsSelection field of the ``OS/2`` table.
    """,
)
@click.option(
    "-us/-no-us",
    "--underscore/--no-underscore",
    "underscore",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 1 (UNDERSCORE).

    Set to indicate that the font glyphs are underscored.
    """,
)
@click.option(
    "-ng/-no-ng",
    "--negative/--no-negative",
    "negative",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 2 (NEGATIVE).

    Set this bit when the font glyphs have their foreground and background reversed.
    """,
)
@click.option(
    "-ol/-no-ol",
    "--outline/--no-outline",
    "outline",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 3 (OUTLINE).

    Set this bit when the font has outline glyphs.
    """,
)
@click.option(
    "-so/-no-so",
    "--strikeout/--no-strikeout",
    "strikeout",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 4 (STRIKEOUT).

    Set this bit when the font has glyphs that are overstruck.
    """,
)
@click.option(
    "-bd/-no-bd",
    "--bold/--no-bold",
    "bold",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 5 (BOLD).

    The bit 0 of the ``macStyle`` field in the ``head`` table will be set to the same value
    as ``fsSelection`` bit 5.
    """,
)
@click.option(
    "-rg",
    "--regular",
    "regular",
    default=None,
    is_flag=True,
    help="""
    Sets the ``OS/2.fsSelection`` bit 6 (REGULAR).

    If bit 6 is set, then ``OS/2.fsSelection`` bits 0 and 5 will be cleared, as well as the
    ``macStyle`` bits 0 and 1 in the ``head`` table.
    """,
)
@click.option(
    "-utm/-no-utm",
    "--use-typo-metrics/--no-use-typo-metrics",
    "use_typo_metrics",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 7 (USE_TYPO_METRICS).

    If set, it is strongly recommended that applications use ``OS/2.sTypoAscender -
    OS/2.sTypoDescender + OS/2.sTypoLineGap`` as the default line spacing for this font.

    Bit 7 was defined in version 4 of the ``OS/2`` table.
    """,
)
@click.option(
    "-wws/-no-wws",
    "--wws-consistent/--no-wws-consistent",
    "wws_consistent",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 8 (WWS_CONSISTENT).

    If bit 8 is set, then ``name`` table strings for family and subfamily are provided that
    are consistent with a weight/width/slope family model without requiring the use of name
    IDs 21 or 22.

    Bit 8 was defined in version 4 of the ``OS/2`` table.
    """,
)
@click.option(
    "-obl/-no-obl",
    "--oblique/--no-oblique",
    "oblique",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsSelection`` bit 9 (OBLIQUE).

    If bit 9 is set, then this font is to be considered an “oblique” style by processes
    which make a distinction between oblique and italic styles, such as Cascading Style
    Sheets font matching. For example, a font created by algorithmically slanting an upright
    face will set this bit.

    This bit, unlike the ITALIC bit (bit 0), is not related to style-linking in applications
    that assume a four-member font-family model comprised of regular, italic, bold and bold
    italic. It may be set or unset independently of the ITALIC bit. In most cases, if
    OBLIQUE is set, then ITALIC will also be set, though this is not required.

    Bit 9 was defined in version 4 of the ``OS/2`` table.
    """,
)
def set_fs_selection(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Sets flags in the fsSelection field of the OS/2 table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: dict[str, Optional[bool]]) -> bool:
        for attr, value in kwargs.items():
            if value is not None:
                if hasattr(font.flags, attr):
                    setattr(font.flags, attr, value)
                elif hasattr(font.t_os_2.fs_selection, attr):
                    setattr(font.t_os_2.fs_selection, attr, value)
        # IMPORTANT: 'head' is a dependency of 'OS/2'. If 'font.t_head.is_modified' is evaluated
        # 'font.t_os_2.is_modified' to suppress fontTools warning about non-matching bits.
        return font.t_head.is_modified or font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("fstype", cls=BaseCommand)
@click.option(
    "-el",
    "--embed-level",
    type=click.Choice(choices=["0", "2", "4", "8"]),
    callback=choice_to_int_callback,
    help="""
    Usage permissions. Valid fonts must set at most one of bits 1, 2 or 3; bit 0 is
    permanently reserved and must be zero. Valid values for this sub-field are 0, 2, 4 or 8.
    The meaning of these values is as follows:

    0: Installable embedding: the font may be embedded, and may be permanently installed for
    use on a remote systems, or for use by other users. The user of the remote system
    acquires the identical rights, obligations and licenses for that font as the original
    purchaser of the font, and is subject to the same end-user license agreement, copyright,
    design patent, and/or trademark as was the original purchaser.

    2: Restricted License embedding: the font must not be modified, embedded or exchanged in
    any manner without first obtaining explicit permission of the legal owner.

    4: Preview & Print embedding: the font may be embedded, and may be temporarily loaded on
    other systems for purposes of viewing or printing the document. Documents containing
    Preview & Print fonts must be opened “read-only”; no edits can be applied to the
    document.

    8: Editable embedding: the font may be embedded, and may be temporarily loaded on other
    systems. As with Preview & Print embedding, documents containing Editable fonts may be
    opened for reading. In addition, editing is permitted, including ability to format new
    text using the embedded font, and changes may be saved.
    """,
)
@click.option(
    "-ns/-no-ns",
    "--no-subsetting/--subsetting",
    "no_subsetting",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsType`` bit 8 (NO_SUBSETTING).

    When this bit is set, the font may not be subsetted prior to embedding. Other embedding
    restrictions specified in bits 0 to 3 and bit 9 also apply.
    """,
)
@click.option(
    "-beo/-no-beo",
    "--bitmap-embed-only/--no-bitmap-embed-only",
    "bitmap_embed_only",
    default=None,
    is_flag=True,
    help="""
    Sets or clears the ``OS/2.fsType`` bit 9 (BITMAP_EMBED_ONLY).

    When this bit is set, only bitmaps contained in the font may be embedded. No outline
    data may be embedded. If there are no bitmaps available in the font, then the font is
    considered unembeddable and the embedding services will fail. Other embedding
    restrictions specified in bits 0-3 and 8 also apply.
    """,
)
def set_fs_type(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Set font embedding licensing rights for the font, defined in the fsType field of the OS/2 table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: dict[str, Optional[bool]]) -> bool:
        for attr, value in kwargs.items():
            if hasattr(font.t_os_2, attr) and value is not None:
                setattr(font.t_os_2, attr, value)
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("panose", cls=BaseCommand)
@click.option(
    "-ft",
    "--family-type",
    "bFamilyType",
    type=click.IntRange(0, 5),
    help="""
    Sets the 'bFamilyType' value.
    """,
)
@click.option(
    "-ss",
    "--serif-style",
    "bSerifStyle",
    type=click.IntRange(0, 15),
    help="""
    Sets the 'bSerifStyle' value.
    """,
)
@click.option(
    "-wt",
    "--weight",
    "bWeight",
    type=click.IntRange(0, 11),
    help="""
    Sets the 'bWeight' value.
    """,
)
@click.option(
    "-pr",
    "--proportion",
    "bProportion",
    type=click.IntRange(0, 9),
    help="""
    Sets the 'bProportion' value.
    """,
)
@click.option(
    "-ct",
    "--contrast",
    "bContrast",
    type=click.IntRange(0, 9),
    help="""
    Sets the 'bContrast' value.
    """,
)
@click.option(
    "-sv",
    "--stroke-variation",
    "bStrokeVariation",
    type=click.IntRange(0, 9),
    help="""
    Sets the 'bStrokeVariation' value.
    """,
)
@click.option(
    "-as",
    "--arm-style",
    "bArmStyle",
    type=click.IntRange(0, 11),
    help="""
    Sets the 'bArmStyle' value.
    """,
)
@click.option(
    "-lf",
    "--letter-form",
    "bLetterForm",
    type=click.IntRange(0, 15),
    help="""
    Sets the 'bLetterForm' value.
    """,
)
@click.option(
    "-ml",
    "--midline",
    "bMidline",
    type=click.IntRange(0, 13),
    help="""
    Sets the 'bMidline' value.
    """,
)
@click.option(
    "-xh",
    "--x-height",
    "bXHeight",
    type=click.IntRange(0, 7),
    help="""
    Sets the 'bXHeight' value.
    """,
)
def set_panose(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Sets the PANOSE classification in the OS/2 table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: dict[str, int]) -> bool:
        for attr, value in kwargs.items():
            if hasattr(font.t_os_2.table.panose, attr) and value is not None:
                setattr(font.t_os_2.table.panose, attr, value)
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("upgrade", cls=BaseCommand)
@click.option(
    "-v",
    "--target-version",
    type=click.IntRange(1, 5),
    help="""
    The version of the OS/2 table to set.
    """,
)
def upgrade(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Upgrades the OS/2 table version.

    If the target version is less or equal to the current version, the table is not modified.
    """

    def task(font: Font, target_version: int) -> bool:
        font.t_os_2.upgrade(target_version)
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()

from typing import Any, Dict, Optional, Union

from copy import deepcopy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.ttGlyphSet import _TTGlyphSetCFF, _TTGlyphSetGlyf

from foundryToolsCLI.Lib.tables.OS_2 import TableOS2
from foundryToolsCLI.Lib.tables.hhea import TableHhea
from foundryToolsCLI.Lib.tables.name import TableName
from foundryToolsCLI.Lib.tables.post import TablePost
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_recursive_option,
    add_common_options,
)
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.skia_tools import is_empty_glyph
from foundryToolsCLI.Lib.utils.timer import Timer

fix_fonts = click.Group("subcommands")


@fix_fonts.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def empty_notdef(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Fix empty .notdef glyph.

    Draw a simple rectangle to fill the empty .notdef glyph.

    Rationale:

    Glyph 0 must be assigned to a .notdef glyph. The .notdef glyph is very important for providing
    the user feedback that a glyph is not found in the font. This glyph should not be left without
    an outline as the user will only see what looks like a space if a glyph is missing and not be
    aware of the active font’s limitation.

    Fixing procedure:

    * Draw a simple rectangle to fill the empty .notdef glyph
    """

    def _draw_empty_notdef_cff(
            glyph_set: _TTGlyphSetCFF, width: int, height: int, thickness: int
    ) -> T2CharString:
        """
        Draws an empty .notdef glyph in a CFF font.

        Parameters:
            glyph_set (_TTGlyphSetCFF): The glyph set to which the .notdef glyph belongs.
            width (int): The width of the .notdef glyph.
            height (int): The height of the .notdef glyph.
            thickness (int): The thickness of the .notdef glyph.

        Returns:
            None
        """

        pen = T2CharStringPen(width=width, glyphSet=glyph_set)
        notdef_glyph = glyph_set[".notdef"]

        # Draw the outer contour (clockwise)
        pen.moveTo((0, 0))
        pen.lineTo((width, 0))
        pen.lineTo((width, height))
        pen.lineTo((0, height))
        pen.closePath()

        # Draw the inner contour (counterclockwise)
        pen.moveTo((thickness, thickness))
        pen.lineTo((thickness, height - thickness))
        pen.lineTo((width - thickness, height - thickness))
        pen.lineTo((width - thickness, thickness))
        pen.closePath()

        notdef_glyph.draw(pen)
        charstring = pen.getCharString()
        charstring.compile()
        return charstring

    def _draw_empty_notdef_glyf(
            glyph_set: Union[Dict[str, Any], _TTGlyphSetGlyf], width: int, height: int,
            thickness: int
    ) -> Glyph:
        """
        Draws an empty .notdef glyph in a glyf font.

        Parameters:
            glyph_set (_TTGlyphSetGlyf): The glyph set to which the .notdef glyph belongs.
            width (int): The width of the .notdef glyph.
            height (int): The height of the .notdef glyph.
            thickness (int): The thickness of the .notdef glyph.

        Returns:
            None
        """
        pen = TTGlyphPen(glyphSet=glyph_set)
        notdef_glyph = glyph_set['.notdef']

        # Draw the outer contour (clockwise)
        pen.moveTo((0, 0))
        pen.lineTo((0, height))
        pen.lineTo((width, height))
        pen.lineTo((width, 0))
        pen.closePath()

        # Draw the inner contour (clockwise)
        pen.moveTo((thickness, thickness))
        pen.lineTo((width - thickness, thickness))
        pen.lineTo((width - thickness, height - thickness))
        pen.lineTo((thickness, height - thickness))
        pen.closePath()

        notdef_glyph.draw(pen)
        return pen.glyph()

    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            glyph_set = font.getGlyphSet()

            if ".notdef" not in glyph_set:
                logger.warning("Font does not contain a .notdef glyph")
                logger.skip(Logs.file_not_changed, file=file)
                continue

            if not is_empty_glyph(glyph_set=glyph_set, glyph_name='.notdef'):
                logger.warning("The .notdef glyph is not empty")
                logger.skip(Logs.file_not_changed, file=file)
                continue

            width = round(font['head'].unitsPerEm / 1000 * 600)
            # The sCapHeight attribute is defined in the OS/2 version 2 and later. If the attribute
            # is not present, the height is calculated as a percentage of the width.
            try:
                height = font["OS/2"].sCapHeight
            except AttributeError:
                height = round(width * 1.25)
            thickness = round(width / 10)

            if font.is_otf:
                cff_table = font["CFF "]
                charstring = _draw_empty_notdef_cff(
                    glyph_set=glyph_set, width=width, height=height, thickness=thickness
                )
                cff_table.cff.topDictIndex[0].CharStrings[".notdef"].bytecode = charstring.bytecode

            else:
                glyph = _draw_empty_notdef_glyf(
                    glyph_set=glyph_set, width=width, height=height, thickness=thickness
                )
                font["glyf"][".notdef"] = glyph

            font["hmtx"][".notdef"] = (width, 0)
            font.save(output_file)
            logger.success(Logs.file_saved, file=output_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def monospace(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Fix metadata in monospaced fonts

    fontbakery check id: com.google.fonts/check/monospace

    Rationale:

    There are various metadata in the OpenType spec to specify if a font is monospaced or not. If
        the font is not truly monospaced, then no monospaced metadata should be set (as sometimes they
        mistakenly are...)

    Requirements for monospace fonts:

    * ``post.isFixedPitch`` - "Set to 0 if the font is proportionally spaced, non-zero if the font
    is not proportionally paced (monospaced)" (https://www.microsoft.com/typography/otspec/post.htm)

    * ``hhea.advanceWidthMax`` must be correct, meaning no glyph's width value is greater.
    (https://www.microsoft.com/typography/otspec/hhea.htm)

    * ``OS/2.panose.bProportion`` must be set to 9 (monospace) on latin text fonts.

    * ``OS/2.panose.bSpacing`` must be set to 3 (monospace) on latin handwritten or latin symbol
    fonts.

    * Spec says: "The PANOSE definition contains ten digits each of which currently describes up to sixteen variations.
    Windows uses ``bFamilyType``, ``bSerifStyle`` and ``bProportion`` in the font mapper to determine family type. It
    also uses ``bProportion`` to determine if the font is monospaced."
    (https://www.microsoft.com/typography/otspec/os2.htm#pan, https://monotypecom-test.monotype.de/services/pan2)

    * ``OS/2.xAvgCharWidth`` must be set accurately. "OS/2.xAvgCharWidth is used when rendering monospaced fonts, at
    least by Windows GDI" (https://typedrawers.com/discussion/comment/15397/#Comment_15397)

    * ``CFF.cff.TopDictIndex[0].isFixedPitch`` must be set to ``True`` for CFF fonts.

    Fixing procedure:

    If the font is monospaced, then:

    * Set ``post.isFixedPitch`` to ``True`` (1)

    * Correct the ``hhea.advanceWidthMax`` value

    * Set the ``OS/2.panose.bProportion`` value to 9 or 3, according to the ``OS/2.panose.bFamilyType`` value

    * Set ``CFF.cff.TopDictIndex[0].isFixedPitch`` to ``True`` for CFF fonts
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

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            glyph_metrics_stats = font.glyph_metrics_stats()
            seems_monospaced = glyph_metrics_stats["seems_monospaced"]
            width_max = glyph_metrics_stats["width_max"]

            # Do nothing if the font does not seem monospaced
            if not seems_monospaced:
                logger.skip(Logs.not_monospaced, file=file)
                continue

            hhea_table: TableHhea = font["hhea"]
            hhea_table_changed = False

            # Ensure that hhea.advanceWidthMax is correct
            current_width_max = hhea_table.advanceWidthMax
            if current_width_max != width_max:
                hhea_table.advanceWidthMax = width_max
                hhea_table_changed = True
                logger.info(
                    "hhea.advanceWidthMax: {old} -> {new}", old=current_width_max, new=width_max
                )

            # Ensure that post.isFixedPitch is non-zero when the font is monospaced
            post_table: TablePost = font["post"]
            post_table_changed = False

            if post_table.isFixedPitch == 0:
                post_table.set_fixed_pitch(True)
                logger.info("post.isFixedPitch: {old} -> {new}", old=0, new=1)
                post_table_changed = True

            # Ensure that OS/2.panose.bProportion is correctly set
            os2_table: TableOS2 = font["OS/2"]
            os2_table_changed = False

            # Ensure that panose.bFamilyType is non-zero when panose.bProportion is 9
            current_family_type = os2_table.panose.bFamilyType

            if os2_table.panose.bFamilyType == 0:
                os2_table.panose.bFamilyType = 2
                logger.info(
                    "OS/2.panose.bFamilyType: {old} -> {new}", old=current_family_type, new=2
                )
                os2_table_changed = True

            # Ensure that panose.bProportion is 9 when the font is monospaced in latin text fonts (bFamilyType = 2)
            current_proportion = os2_table.panose.bProportion
            if os2_table.panose.bFamilyType == 2:
                if not os2_table.panose.bProportion == 9:
                    os2_table.panose.bProportion = 9
                    logger.info(
                        "OS/2.panose.bProportion: {old} -> {new}", old=current_proportion, new=9
                    )
                    os2_table_changed = True

            # Ensure that panose.bProportion is 3 when the font is monospaced in latin handwritten fonts
            # (bFamilyType = 3) and in latin symbol fonts (bFamilyType = 5)
            if os2_table.panose.bFamilyType in [3, 5]:
                if not os2_table.panose.bProportion == 3:
                    os2_table.panose.bProportion = 3
                    logger.info(
                        "OS/2.panose.bProportion: {old} -> {new}", old=current_proportion, new=3
                    )
                    os2_table_changed = True

            # Ensure that CFF.cff.TopDictIndex[0].isFixedPitch is True for CFF fonts
            cff_table_changed = False
            if font.is_otf:
                cff_table = font["CFF "]
                top_dict = cff_table.cff.topDictIndex[0]
                if not getattr(top_dict, "isFixedPitch", 1):
                    setattr(top_dict, "isFixedPitch", True)
                    logger.info(
                        "CFF.cff.TopDictIndex[0].isFixedPitch: {old} -> {new}", old=0, new=1
                    )
                    cff_table_changed = True

            # Check if one of the tables has changed and save the font.
            if hhea_table_changed or post_table_changed or os2_table_changed or cff_table_changed:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def nbsp_width(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Fix whitespace widths.

    fontbakery check id: com.google.fonts/check/whitespace_widths

    Rationale:

    If the ``space`` and ``nbspace`` glyphs have different widths, then Google Workspace has problems with the font.

    The ``nbspace`` is used to replace the space character in multiple situations in documents; such as the space before
    punctuation in languages that do that. It avoids the punctuation to be separated from the last word and go to next
    line.

    This is automatic substitution by the text editors, not by fonts. It's also used by designers in text composition
    practice to create nicely shaped paragraphs. If the ``space`` and the ``nbspace`` are not the same width, it breaks
    the text composition of documents.

    Fixing procedure:

    * Check if ``nbspace`` and space glyphs have the same width. If not, correct ``nbspace`` width to match the
    ``space`` width.
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

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            hmtx_table = font["hmtx"]
            hmtx_table_copy = deepcopy(hmtx_table)

            best_cmap = font.getBestCmap()
            space_name = best_cmap[0x0020]
            nbspace_name = best_cmap[0x00A0]

            font["hmtx"][nbspace_name] = font["hmtx"][space_name]

            if hmtx_table_copy.compile(font) != hmtx_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@click.option(
    "-m",
    "--mode",
    type=click.IntRange(1, 3),
    default=1,
    help="""
              \b
              1: sets only the italic bits and clears the oblique bit
              2: sets italic and oblique bits
              3: sets only the oblique bit and clears italic bits
              """,
)
@click.option(
    "--min-slant",
    type=click.FloatRange(min=0.0, max_open=True),
    default=2.0,
    show_default=True,
    help="""Minimum slant value under which the font is considered upright.
    
    The italic angle is calculated by drawing the 'H' glyph with the fontTools.pens.statisticsPen.StatisticsPen and
    rounding the value of the pen's 'slant' attribute. In few cases, upright fonts may return non-zero slant values
    (e.g.: 1.0). They will be considered as uprights anyway, if the returned italic angle's absolute value is lower than
    the minimum (default is 2.0).
    """,
)
@add_common_options()
@Timer(logger=logger.info)
def italic_angle(
    input_path: Path,
    mode: int = 1,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
    min_slant: float = 2.0,
):
    """
    Fix italic angle and italic/oblique bits.

    fontbakery check ids:

    \b
    * com.google.fonts/check/italic_angle
    * com.google.fonts/check/caret_slope

    Rationale:
    The ``post`` table ``italicAngle`` property should be a reasonable amount, likely not more than 30°. Note that in
    the OpenType specification, the value is negative for a rightward lean.

    https://docs.microsoft.com/en-us/typography/opentype/spec/post

    Checks whether ``hhea.caretSlopeRise`` and ``hhea.caretSlopeRun`` match with ``post.italicAngle``.

    For Upright fonts, you can set ``hhea.caretSlopeRise`` to 1 and ``hhea.caretSlopeRun`` to 0.

    For Italic fonts, you can set ``hhea.caretSlopeRise`` to ``head.unitsPerEm`` and calculate ``hhea.caretSlopeRun``
    like this:

    ``round(math.tan(math.radians(-1 * font["post"].italicAngle)) * font["head"].unitsPerEm)``

    This check allows for a 0.1° rounding difference between the Italic angle as calculated by the caret slope and
    ``post.italicAngle``

    Fixing procedure:

    * Recalculate ``post.italicAngle``

    * Recalculate ``hhea.caretSlopeRise`` and ``hhea.caretSlopeRun`` according to the calculated ``post.italicAngle``

    * Set/clear the italic and/or oblique bits according to the calculated values

    * In CFF fonts, recalculate also ``CFF.topDictIndex[0].ItalicAngle`` and set it to ``post.italicAngle`` rounded to
    the nearest integer
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

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            post_table: TablePost = font["post"]
            hhea_table: TableHhea = font["hhea"]

            # Check post.italicAngle
            post_italic_angle = post_table.italicAngle
            calculated_post_italic_angle = font.calculate_italic_angle(min_slant=min_slant)
            post_italic_angle_ok = font.check_italic_angle(min_slant=min_slant)

            if post_italic_angle_ok:
                logger.opt(colors=True).info(
                    "post.italicAngle: {post_italic_angle} -> <green>OK</>",
                    post_italic_angle=post_italic_angle,
                )
            else:
                post_table.set_italic_angle(calculated_post_italic_angle)
                logger.opt(colors=True).info(
                    "post.italicAngle: <red>{old}</> -> <green>{new}</>",
                    old=post_italic_angle,
                    new=calculated_post_italic_angle,
                )

            calculated_rise = font.calculate_caret_slope_rise()
            calculated_run = font.calculate_caret_slope_run()

            # Check hhea italic angle
            rise = hhea_table.caretSlopeRise
            run = hhea_table.caretSlopeRun
            hhea_italic_angle = font.calculate_run_rise_angle()
            hhea_italic_angle_ok = abs(post_table.italicAngle - hhea_italic_angle) < 0.1
            if hhea_italic_angle_ok:
                logger.opt(colors=True).info(
                    "hhea.caretSlopeRise: {rise} -> <green>OK</>", rise=rise
                )
                logger.opt(colors=True).info("hhea.caretSlopeRun: {run} -> <green>OK</>", run=run)
            else:
                if hhea_table.caretSlopeRise != calculated_rise:
                    hhea_table.caretSlopeRise = calculated_rise
                    logger.opt(colors=True).info(
                        "hhea.caretSlopeRise: <red>{rise}</> -> <green>{new}</>",
                        rise=rise,
                        new=calculated_rise,
                    )
                if hhea_table.caretSlopeRun != calculated_run:
                    hhea_table.caretSlopeRun = calculated_run
                    logger.opt(colors=True).info(
                        "hhea.caretSlopeRun: <red>{run}</> -> <green>{new}</>",
                        run=run,
                        new=calculated_run,
                    )

            # Check CFF italic angle
            if font.is_otf:
                cff_table = font["CFF "]
                cff_italic_angle = cff_table.cff.topDictIndex[0].ItalicAngle
                cff_italic_angle_ok = cff_italic_angle == round(post_table.italicAngle)

                if cff_italic_angle_ok:
                    logger.opt(colors=True).info(
                        "CFF.cff.topDictIndex[0].ItalicAngle: {cff_italic_angle} -> <green>OK</>",
                        cff_italic_angle=cff_italic_angle,
                    )
                else:
                    cff_table.cff.topDictIndex[0].ItalicAngle = round(post_table.italicAngle)
                    logger.opt(colors=True).info(
                        "CFF.cff.topDictIndex[0].ItalicAngle: <red>{old}</> -> <green>{new}</>",
                        old=cff_italic_angle,
                        new=round(post_table.italicAngle),
                    )
            else:
                cff_italic_angle_ok = True

            # Set or clear italic/oblique bits according to post.italicAngle
            is_italic = font.is_italic
            is_oblique = font.is_oblique
            font.calculate_italic_bits(mode=mode)

            if font.is_italic == is_italic:
                italic_bits_ok = True
            else:
                italic_bits_ok = False

            if font.is_oblique == is_oblique:
                oblique_bit_ok = True
            else:
                oblique_bit_ok = False

            if italic_bits_ok:
                logger.opt(colors=True).info("Italic: {italic} -> <green>OK</>", italic=is_italic)
            else:
                logger.opt(colors=True).info(
                    "Italic: <red>{old}</> -> <green>{new}</>", old=is_italic, new=font.is_italic
                )

            if oblique_bit_ok:
                logger.opt(colors=True).info(
                    "Oblique: {oblique} -> <green>OK</>", oblique=is_oblique
                )
            else:
                logger.opt(colors=True).info(
                    "Oblique: <red>{old}</> -> <green>{new}</>", old=is_oblique, new=font.is_oblique
                )

            # Don't save the file if nothing has been modified
            if (
                post_italic_angle_ok
                and hhea_italic_angle_ok
                and cff_italic_angle_ok
                and italic_bits_ok
                and oblique_bit_ok
            ):
                logger.skip(Logs.file_not_changed, file=file)
                continue

            font.save(output_file)
            logger.success(Logs.file_saved, file=output_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def nbsp_missing(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Fix missing whitespace glyphs.

    fontbakery check id: com.google.fonts/check/whitespace_glyphs

    Rationale:

    Font contains glyphs for whitespace characters?

    Fixing procedure:

    * Add a glyph for the missing ``nbspace`` character by double mapping the ``space`` character
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

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            cmap_table = font["cmap"]
            cmap_table_copy = deepcopy(cmap_table)

            for t in cmap_table.tables:
                if t.isUnicode():
                    if 0xA0 not in t.cmap.keys():
                        t.cmap[0xA0] = "space"

            if cmap_table_copy.compile(font) != cmap_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def decompose_transformed(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Decompose glyphs with transformed components.

    fontbakery check id: com.google.fonts/check/transformed_components

    Rationale:

    Some families have glyphs which have been constructed by using transformed components e.g. the 'u' being constructed
    from a flipped 'n'.

    From a designers point of view, this sounds like a win (less work). However, such approaches can lead to
    rasterization issues, such as having the 'u' not sitting on the baseline at certain sizes after running the font
    through ttfautohint.

    Other issues are outlines that end up reversed when only one dimension is flipped while the other isn't.

    As of July 2019, Marc Foley observed that ttfautohint assigns cvt values to transformed glyphs as if they are not
    transformed and the result is they render very badly, and that vttLib does not support flipped components.

    When building the font with fontmake, the problem can be fixed by adding this to the command line:

    ``--filter DecomposeTransformedComponentsFilter``

    Fixing procedure:

    * Decompose composite glyphs that have transformed components.
    """

    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    import pathops

    fonts = get_fonts_in_path(
        input_path=input_path,
        recursive=recursive,
        allow_cff=False,
        recalc_timestamp=recalc_timestamp,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            glyph_set = font.getGlyphSet()
            glyph_table = font["glyf"]
            glyph_table_copy = deepcopy(glyph_table)

            for glyph_name in glyph_set.keys():
                decompose = False
                glyf = glyph_table[glyph_name]
                if not glyf.isComposite():
                    continue
                for component in glyf.components:
                    _, transform = component.getComponentInfo()

                    # Font is hinted, decompose glyphs with *any* transformations
                    if font.is_hinted_ttf:
                        if transform[0:4] != (1, 0, 0, 1):
                            decompose = True
                    # Font is unhinted, decompose only glyphs with transformations where only one dimension is flipped
                    # while the other isn't. Otherwise the outline direction is intact and since the font is unhinted,
                    # no rendering problems are to be expected
                    else:
                        if transform[0] * transform[3] < 0:
                            decompose = True

                if decompose:
                    dc_pen = DecomposingRecordingPen(glyph_set)
                    glyph_set[glyph_name].draw(dc_pen)

                    path = pathops.Path()
                    path_pen = path.getPen()
                    dc_pen.replay(path_pen)

                    path.simplify()

                    ttPen = TTGlyphPen(None)
                    path.draw(ttPen)
                    glyph_table[glyph_name] = ttPen.glyph()

            if glyph_table_copy.compile(font) != glyph_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def duplicate_components(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Remove duplicate components.

    fontbakery check id: com.google.fonts/check/glyf_non_transformed_duplicate_components

    Rationale:

    There have been cases in which fonts had faulty double quote marks, with each of them containing two single quote
    marks as components with the same x, y coordinates which makes them visually look like single quote marks.

    This check ensures that glyphs do not contain duplicate components which have the same x,y coordinates.

    Fixing procedure:

    * Remove duplicate components which have the same x,y coordinates.
    """

    fonts = get_fonts_in_path(
        input_path=input_path,
        allow_cff=False,
        recursive=recursive,
        recalc_timestamp=recalc_timestamp,
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            glyph_table = font["glyf"]
            glyph_table_copy = deepcopy(glyph_table)

            for glyph_name in glyph_table.keys():
                glyf = glyph_table[glyph_name]
                if not glyf.isComposite():
                    continue

                seen = []

                for comp in glyf.components:
                    comp_info = {
                        "glyph": glyph_name,
                        "component": comp.glyphName,
                        "x": comp.x,
                        "y": comp.y,
                    }
                    if comp_info in seen:
                        glyf.components.remove(comp)
                    else:
                        seen.append(comp_info)

            if glyph_table_copy.compile(font) != glyph_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def kern_table(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Fix ``kern`` table.

    fontbakery check id: com.google.fonts/check/kern_table

    Rationale:

    Even though all fonts should have their kerning implemented in the ``GPOS`` table, there may be kerning info at the
    ``kern`` table as well.

    Some applications such as MS PowerPoint require kerning info on the kern table. More specifically, they require a
    format 0 kern subtable from a kern table version 0 with only glyphs defined in the ``cmap`` table, which is the only
    one that Windows understands (and which is also the simplest and more limited of all the kern subtables).

    Google Fonts ingests fonts made for download and use on desktops, and does all web font optimizations in the serving
    pipeline (using libre libraries that anyone can replicate.)

    Ideally, TTFs intended for desktop users (and thus the ones intended for Google Fonts) should have both ``kern`` and
    ``GPOS`` tables.

    Given all of the above, we currently treat kerning on a v0 ``kern`` table as a good-to-have (but optional) feature.

    Fixing procedure:

    * Remove glyphs that are not defined in the ``cmap`` table from the ``kern`` table.
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

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            if "kern" not in font:
                logger.skip(Logs.file_not_changed, file=file)
                continue

            kern = font["kern"]

            if all(kernTable.format != 0 for kernTable in kern.kernTables):
                logger.warning(f"{file.name}: The 'kern' table doesn't have any format-0 subtable")
                continue

            kern_table_copy = deepcopy(kern)

            character_glyphs = set()
            for table in font["cmap"].tables:
                character_glyphs.update(table.cmap.values())

            for table in kern.kernTables:
                if table.format == 0:
                    pairs_to_delete = []
                    for left_glyph, right_glyph in table.kernTable.keys():
                        if (
                            left_glyph not in character_glyphs
                            or right_glyph not in character_glyphs
                        ):
                            pairs_to_delete.append((left_glyph, right_glyph))
                    if len(pairs_to_delete) > 0:
                        for pair in pairs_to_delete:
                            del table.kernTable[pair]

            if kern_table_copy.compile(font) != kern.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def strip_names(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Remove leading and trailing spaces from ``name`` table entries.

    fontbakery check id: com.google.fonts/check/name/trailing_spaces

    Rationale:

    Name table records must not have trailing spaces.

    Fixing procedure:

    * Remove leading and trailing spaces from all NameRecords in the ``name`` table.

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

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)

            name_table.remove_leading_trailing_spaces()

            if name_table_copy.compile(font) != name_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)

            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_common_options()
@Timer(logger=logger.info)
def empty_names(
    input_path: Path,
    output_dir: Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Remove empty NameRecords from ``name`` table.

    fontbakery check id: com.adobe.fonts/check/name/empty_records

    Rationale:

    Check name table for empty records.

    Fixing procedure:

    * Remove empty NameRecords from the ``name`` table.


    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            logger.opt(colors=True).info(Logs.checking_file, file=file)

            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)

            name_table.remove_empty_names()

            if name_table_copy.compile(font) != name_table.compile(font):
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)

            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[fix_fonts],
    help="""
    A set of commands to detect and automatically fix font errors.
    """,
)

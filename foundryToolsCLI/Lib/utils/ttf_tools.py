"""
Adapted code from fontTools.ttLib.removeOverlaps to fix contours direction
"""

from typing import Mapping

from fontTools.ttLib import ttFont
from fontTools.ttLib.tables import _g_l_y_f
from fontTools.ttLib.tables import _h_m_t_x

from foundryToolsCLI.Lib.utils.logger import logger
from foundryToolsCLI.Lib.utils.skia_tools import (
    remove_tiny_paths,
    skia_path_from_glyph,
    ttf_glyph_from_skia_path,
    simplify_path,
    ttf_components_overlap,
    same_path,
)


class CorrectTTFContoursError(Exception):
    pass


_TTGlyphMapping = Mapping[str, ttFont._TTGlyph]


def correct_glyph_contours(
    glyph_name: str,
    glyph_set: _TTGlyphMapping,
    glyf_table: _g_l_y_f.table__g_l_y_f,
    hmtx_table: _h_m_t_x.table__h_m_t_x,
    remove_hinting: bool = True,
    min_area: int = 25,
) -> bool:
    glyph = glyf_table[glyph_name]

    if (
        glyph.numberOfContours > 0
        or glyph.isComposite()
        and ttf_components_overlap(glyph, glyph_set)
    ):
        path_1 = skia_path_from_glyph(glyph_name, glyph_set)
        path_2 = skia_path_from_glyph(glyph_name, glyph_set)
        path_2 = simplify_path(path_2, glyph_name, clockwise=True)
        if min_area > 0:
            path_2 = remove_tiny_paths(path_2, glyph_name=glyph_name, min_area=min_area)

        if not same_path(path_1=path_1, path_2=path_2):
            glyf_table[glyph_name] = glyph = ttf_glyph_from_skia_path(path_2)
            assert not glyph.program
            width, lsb = hmtx_table[glyph_name]
            if lsb != glyph.xMin:
                hmtx_table[glyph_name] = (width, glyph.xMin)
            return True

    if remove_hinting:
        glyph.removeHinting()
    return False


def correct_ttf_contours(
    font: ttFont.TTFont,
    remove_hinting: bool = True,
    ignore_errors: bool = False,
    min_area: int = 25,
    verbose: bool = False,
) -> None:
    try:
        glyf_table = font["glyf"]
    except KeyError:
        raise NotImplementedError("Not a TTF font")

    glyph_set = font.getGlyphSet()
    hmtx_table = font["hmtx"]

    glyph_names = font.getGlyphOrder()

    # process all simple glyphs first, then composites with increasing component depth,
    # so that by the time we test for component intersections the respective base glyphs
    # have already been simplified
    glyph_names = sorted(
        glyph_names,
        key=lambda name: (
            glyf_table[name].getCompositeMaxpValues(glyf_table).maxComponentDepth
            if glyf_table[name].isComposite()
            else 0,
            name,
        ),
    )
    modified = list()
    for glyph_name in glyph_names:
        try:
            if correct_glyph_contours(
                glyph_name=glyph_name,
                glyph_set=glyph_set,
                glyf_table=glyf_table,
                hmtx_table=hmtx_table,
                remove_hinting=remove_hinting,
                min_area=min_area,
            ):
                modified.append(glyph_name)
        except CorrectTTFContoursError:
            if not ignore_errors:
                raise
            logger.error(f"Failed to remove overlaps for '{glyph_name}'")

    if verbose:
        modified = sorted(modified)
        logger.info(f"{len(modified)} {'glyph' if len(modified) == 1 else 'glyphs'} modified")


def decomponentize(font: ttFont.TTFont):
    """
    This function decomponentizes composite glyphs in a TrueType font.
    """
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    glyph_set = font.getGlyphSet()
    glyf_table = font["glyf"]
    dr_pen = DecomposingRecordingPen(glyph_set)
    tt_pen = TTGlyphPen(None)

    for glyph_name in font.glyphOrder:
        glyph = glyf_table[glyph_name]
        if not glyph.isComposite():
            continue
        dr_pen.value = []
        tt_pen.init()
        glyph.draw(dr_pen, glyf_table)
        dr_pen.replay(tt_pen)
        glyf_table[glyph_name] = tt_pen.glyph()

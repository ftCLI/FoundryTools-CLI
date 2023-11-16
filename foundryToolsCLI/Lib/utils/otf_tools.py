from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib.ttFont import TTFont

from foundryToolsCLI.Lib.tables.CFF_ import TableCFF
from foundryToolsCLI.Lib.utils.logger import logger
from foundryToolsCLI.Lib.utils.skia_tools import (
    remove_tiny_paths,
    skia_path_from_glyph,
    t2_charstring_from_skia_path,
    same_path,
    simplify_path,
)


def correct_otf_contours(font: TTFont, min_area: int = 25, verbose: bool = False) -> None:
    try:
        cff_table: TableCFF = font["CFF "]
    except KeyError:
        raise NotImplementedError("Not an OTF font")

    glyph_set = font.getGlyphSet()

    modified = []
    charstrings = {}

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(width=v.width, glyphSet=glyph_set)
        glyph_set[k].draw(t2_pen)
        charstrings[k] = t2_pen.getCharString()

        path_1 = skia_path_from_glyph(glyph_name=k, glyph_set=glyph_set)
        path_2 = skia_path_from_glyph(glyph_name=k, glyph_set=glyph_set)
        path_2 = simplify_path(path=path_2, glyph_name=k, clockwise=False)

        if min_area > 0:
            path_2 = remove_tiny_paths(
                path=path_2, glyph_name=k, min_area=min_area, verbose=verbose
            )

        if not same_path(path_1=path_1, path_2=path_2):
            modified.append(k)
            charstrings[k] = t2_charstring_from_skia_path(path=path_2, width=v.width)

    if verbose:
        modified = sorted(modified)

        if len(modified) > 0:
            logger.info(f"The following glyphs have been modified: {', '.join(modified)}")
        else:
            logger.info("No glyphs modified")

    ps_name = cff_table.get_fb_ps_name()
    font_info = cff_table.get_fb_font_info()
    private_dict = cff_table.get_fb_private_dict()
    fb = FontBuilder(font=font)
    fb.setupCFF(
        psName=ps_name, fontInfo=font_info, privateDict=private_dict, charStringsDict=charstrings
    )

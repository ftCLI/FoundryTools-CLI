import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib.ttFont import TTFont

from ftCLI.Lib.utils.click_tools import generic_error_message, generic_info_message


def fix_cff_contours(font: TTFont, min_area: int = 25):
    glyph_set = font.getGlyphSet()
    cff = font['CFF '].cff
    top_dict = cff.topDictIndex[0]

    charstrings = {}
    for k, v in glyph_set.items():
        pathops_path = pathops.Path()
        pathops_pen = pathops_path.getPen(glyphSet=glyph_set)
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        try:
            glyph_set[k].draw(pathops_pen)

            new_path = pathops.Path()
            for contour in pathops_path.contours:
                if contour.area > min_area:
                    new_path.addPath(contour)
                else:
                    generic_info_message(f"tiny path removed from glyph {k}")

                pathops_path = new_path

            pathops_path.simplify()
            pathops_path.draw(t2_pen)
            charstring = t2_pen.getCharString()
            charstrings[k] = charstring
        except Exception as e:
            if k != ".notdef":
                generic_error_message(f"Failed to get charstring for glyph {k}: {e}")

    ps_name = cff.fontNames[0]
    font_info = {
        key: value for key, value in top_dict.rawDict.items()
        if key not in ("FontBBox", "charset", "Encoding", "Private", "CharStrings")
    }
    private_dict = {
        key: value for key, value in top_dict.Private.rawDict.items()
        if key not in ("Subrs", "defaultWidthX", "nominalWidthX")
    }

    fb = FontBuilder(font=font)
    fb.setupCFF(
        psName=ps_name,
        fontInfo=font_info,
        privateDict=private_dict,
        charStringsDict=charstrings
    )

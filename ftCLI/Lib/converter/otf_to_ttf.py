import logging

from fontTools import configLogger
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTLibError, newTable

from ftCLI.Lib.Font import Font

log = logging.getLogger()
configLogger(logger=log)

# default approximation error, measured in UPEM
MAX_ERR = 1.0

# default 'post' table format
POST_FORMAT = 2.0

# assuming the input contours' direction is correctly set (counter-clockwise),
# we just flip it to clockwise
REVERSE_DIRECTION = True


def glyphs_to_quadratic(glyphs, max_err=MAX_ERR, reverse_direction=REVERSE_DIRECTION):
    quadGlyphs = {}
    for gname in glyphs.keys():
        glyph = glyphs[gname]
        ttPen = TTGlyphPen(glyphs)
        cu2quPen = Cu2QuPen(ttPen, max_err, reverse_direction=reverse_direction)
        glyph.draw(cu2quPen)
        quadGlyphs[gname] = ttPen.glyph()
    return quadGlyphs


def update_hmtx(ttFont, glyf):
    hmtx = ttFont["hmtx"]
    for glyphName, glyph in glyf.glyphs.items():
        if hasattr(glyph, "xMin"):
            hmtx[glyphName] = (hmtx[glyphName][0], glyph.xMin)


def convert_font(ttFont: Font, post_format=POST_FORMAT, **kwargs):
    if ttFont.sfntVersion != "OTTO":
        raise TTLibError("Not a OpenType font (bad sfntVersion)")
    assert "CFF " in ttFont

    glyphOrder = ttFont.getGlyphOrder()

    ttFont["loca"] = newTable("loca")
    ttFont["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder = glyphOrder
    glyf.glyphs = glyphs_to_quadratic(ttFont.getGlyphSet(), **kwargs)
    del ttFont["CFF "]
    if "VORG" in ttFont:
        del ttFont["VORG"]
    glyf.compile(ttFont)
    update_hmtx(ttFont, glyf)

    ttFont["maxp"] = maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    maxp.maxZones = 1
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = max(len(g.components if hasattr(g, "components") else []) for g in glyf.glyphs.values())
    maxp.compile(ttFont)

    post = ttFont["post"]
    post.formatType = post_format
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyphOrder
    try:
        post.compile(ttFont)
    except OverflowError:
        post.formatType = 3
        log.warning("Dropping glyph names, they do not fit in 'post' table.")

    ttFont.sfntVersion = "\000\001\000\000"


def run(input_file, output_file, recalc_timestamp=False):
    font = Font(input_file, recalcTimestamp=recalc_timestamp)
    convert_font(font, post_format=2.0, max_err=1.0, reverse_direction=True)
    font.save(output_file)

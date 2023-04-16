from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTLibError, newTable

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.click_tools import generic_warning_message


class Options(object):
    def __init__(self):
        self.max_err = 1.0
        self.reverse_direction = True
        self.post_format = 2.0


class CFFToTrueType(object):
    def __init__(self, font: Font):
        self.font = font
        self.options = Options()

    def run(self):
        if self.font.sfntVersion != "OTTO":
            raise TTLibError("Not a OpenType font (bad sfntVersion)")
        assert "CFF " in self.font

        glyphOrder = self.font.getGlyphOrder()

        self.font["loca"] = newTable("loca")
        self.font["glyf"] = glyf = newTable("glyf")
        glyf.glyphOrder = glyphOrder
        glyf.glyphs = self.glyphs_to_quadratic(glyphs=self.font.getGlyphSet())
        del self.font["CFF "]
        if "VORG" in self.font:
            del self.font["VORG"]
        glyf.compile(self.font)
        self.update_hmtx(glyf)

        self.font["maxp"] = maxp = newTable("maxp")
        maxp.tableVersion = 0x00010000
        maxp.maxZones = 1
        maxp.maxTwilightPoints = 0
        maxp.maxStorage = 0
        maxp.maxFunctionDefs = 0
        maxp.maxInstructionDefs = 0
        maxp.maxStackElements = 0
        maxp.maxSizeOfInstructions = 0
        maxp.maxComponentElements = max(
            len(g.components if hasattr(g, "components") else []) for g in glyf.glyphs.values()
        )
        maxp.compile(self.font)

        post = self.font["post"]
        post.formatType = self.options.post_format
        post.extraNames = []
        post.mapping = {}
        post.glyphOrder = glyphOrder
        try:
            post.compile(self.font)
        except OverflowError:
            post.formatType = 3
            generic_warning_message("Dropping glyph names, they do not fit in 'post' table.")

        self.font.sfntVersion = "\000\001\000\000"
        return self.font

    def update_hmtx(self, glyf):
        hmtx = self.font["hmtx"]
        for glyphName, glyph in glyf.glyphs.items():
            if hasattr(glyph, "xMin"):
                hmtx[glyphName] = (hmtx[glyphName][0], glyph.xMin)

    def glyphs_to_quadratic(self, glyphs):
        quadGlyphs = {}
        for gname in glyphs.keys():
            glyph = glyphs[gname]
            ttPen = TTGlyphPen(glyphs)
            cu2quPen = Cu2QuPen(ttPen, max_err=self.options.max_err, reverse_direction=self.options.reverse_direction)
            glyph.draw(cu2quPen)
            quadGlyphs[gname] = ttPen.glyph()
        return quadGlyphs

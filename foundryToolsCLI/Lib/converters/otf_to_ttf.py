import time
from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTLibError, newTable

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.converters.options import CFFToTrueTypeOptions
from foundryToolsCLI.Lib.utils.click_tools import generic_info_message, file_saved_message, generic_error_message


class OTF2TTFRunner(object):
    def __init__(self):
        super().__init__()
        self.options = CFFToTrueTypeOptions()

    def run(self, source_fonts: list[Font]) -> None:
        converted_files_count = 0
        start_time = time.time()

        for count, source_font in enumerate(source_fonts, start=1):
            t = time.time()

            try:
                print()
                file = Path(source_font.reader.file.name)
                generic_info_message(f"Converting file {count} of {len(source_fonts)}: {file.name}")

                # If the source font is a WOFF or WOFF2, we add a suffix to avoid unwanted overwriting
                if source_font.flavor is None:
                    ext = ".ttf"
                    suffix = ""
                else:
                    ext = source_font.get_real_extension()
                    suffix = ".ttf"
                file_name = file.name.replace(".otf", "").replace(".ttf", "").replace(".woff2", "").replace(".woff", "")

                output_file = Path(
                    makeOutputFileName(
                        file_name,
                        extension=ext,
                        suffix=suffix,
                        outputDir=self.options.output_dir,
                        overWrite=self.options.overwrite,
                    )
                )

                converter = CFFToTrueType(font=source_font)
                converter.options.max_err = self.options.max_err
                ttf_font = converter.run()
                ttf_font.save(output_file)
                ttf_font.close()

                generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")
                file_saved_message(output_file)
                converted_files_count += 1

            except Exception as e:
                generic_error_message(e)
            finally:
                source_font.close()

        print()
        generic_info_message(f"Total files     : {len(source_fonts)}")
        generic_info_message(f"Converted files : {converted_files_count}")
        generic_info_message(f"Elapsed time    : {round(time.time() - start_time, 3)} seconds")


class CFFToTrueType(object):
    def __init__(self, font: Font):
        self.font = font
        self.options = CFFToTrueTypeOptions()

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

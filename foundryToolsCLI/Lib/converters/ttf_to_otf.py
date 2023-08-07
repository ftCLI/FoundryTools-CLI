import os
import tempfile
import time
from pathlib import Path

import click
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.converters.options import TrueTypeToCFFOptions
from foundryToolsCLI.Lib.converters.otf_to_ttf import CFFToTrueType
from foundryToolsCLI.Lib.utils.click_tools import (
    file_saved_message,
    generic_info_message,
    generic_error_message,
    generic_warning_message,
)


class TTF2OTFRunner(object):
    def __init__(self):
        super().__init__()
        self.options = TrueTypeToCFFOptions()

    def run(self, source_fonts: list[Font]) -> None:
        converted_files_count = 0
        start_time = time.time()

        for count, source_font in enumerate(source_fonts, start=1):
            t = time.time()

            try:
                file = Path(source_font.reader.file.name)
                print()
                generic_info_message(f"Converting file {count} of {len(source_fonts)}: {file.name}")

                # If the source font is a WOFF or WOFF2, we add a suffix to avoid unwanted overwriting
                flavor = source_font.flavor
                if flavor is None:
                    ext = ".otf"
                    suffix = ""
                else:
                    ext = source_font.get_real_extension()
                    suffix = ".otf"
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

                temp_source_fd, temp_source_file = tempfile.mkstemp(suffix=".ttf")
                if self.options.scale_upm:
                    source_font.ttf_scale_upem(units_per_em=self.options.scale_upm)
                    source_font.save(temp_source_file)
                    source_font = Font(temp_source_file, recalcTimestamp=self.options.recalc_timestamp)

                # Decomponentize the source font
                source_font.ttf_decomponentize()

                tolerance = self.options.tolerance / 1000 * source_font["head"].unitsPerEm
                failed, charstrings = get_qu2cu_charstrings(font=source_font, tolerance=tolerance)

                if len(failed) > 0:
                    generic_info_message(f"Retrying to get {len(failed)} charstrings...")
                    t2_ttf2otf_converter = TrueTypeToCFF(font=source_font)
                    t2_charstrings = get_t2_charstrings(font=source_font)
                    t2_otf_font: Font = t2_ttf2otf_converter.run(charstrings=t2_charstrings)
                    t2_otf_2_ttf_converter = CFFToTrueType(font=t2_otf_font)
                    t2_otf_2_ttf_font = t2_otf_2_ttf_converter.run()
                    _, fallback_charstrings = get_qu2cu_charstrings(t2_otf_2_ttf_font)

                    for c in failed:
                        try:
                            generic_info_message(f"{c}", nl=False)
                            charstrings[c] = fallback_charstrings[c]
                            click.secho(f" -> {click.style('OK', fg='green')}")
                        except Exception as e:
                            click.secho(f" -> {click.style('FAIL', fg='red')} ({e})")
                            generic_error_message(e)

                ttf2otf_converter = TrueTypeToCFF(font=source_font)
                cff_font: Font = ttf2otf_converter.run(charstrings=charstrings)

                cff_font.otf_fix_contours(min_area=25, verbose=False)

                if self.options.subroutinize:
                    cff_font.otf_subroutinize()

                cff_font.flavor = flavor
                cff_font.save(output_file)
                if os.path.exists(temp_source_file):
                    os.close(temp_source_fd)
                    os.remove(temp_source_file)

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


class TrueTypeToCFF(object):
    def __init__(self, font: Font):
        self.font = font

    def run(self, charstrings: dict):
        cff_font_info = get_cff_font_info(font=self.font)
        post_values = get_post_values(font=self.font)

        fb = FontBuilder(font=self.font)
        fb.isTTF = False
        for table in ["glyf", "cvt ", "loca", "fpgm", "prep", "gasp", "LTSH", "hdmx"]:
            if table in fb.font:
                del fb.font[table]

        fb.setupCFF(
            psName=self.font["name"].getDebugName(6),
            charStringsDict=charstrings,
            fontInfo=cff_font_info,
            privateDict={},
        )
        fb.setupDummyDSIG()
        fb.setupMaxp()
        fb.setupPost(**post_values)

        return fb.font


def get_cff_font_info(font: Font) -> dict:
    """
    Setup CFF topDict

    :return: A dictionary of the font info.
    """

    font_revision = str(round(font["head"].fontRevision, 3)).split(".")
    major_version = str(font_revision[0])
    minor_version = str(font_revision[1]).ljust(3, "0")

    cff_font_info = dict(
        version=".".join([major_version, str(int(minor_version))]),
        FullName=font["name"].getBestFullName(),
        FamilyName=font["name"].getBestFamilyName(),
        ItalicAngle=font["post"].italicAngle,
        UnderlinePosition=font["post"].underlinePosition,
        UnderlineThickness=font["post"].underlineThickness,
        isFixedPitch=False if font["post"].isFixedPitch == 0 else True,
    )

    return cff_font_info


def get_post_values(font: Font) -> dict:
    post_info = dict(
        italicAngle=round(font["post"].italicAngle),
        underlinePosition=font["post"].underlinePosition,
        underlineThickness=font["post"].underlineThickness,
        isFixedPitch=font["post"].isFixedPitch,
        minMemType42=font["post"].minMemType42,
        maxMemType42=font["post"].maxMemType42,
        minMemType1=font["post"].minMemType1,
        maxMemType1=font["post"].maxMemType1,
    )
    return post_info


def get_qu2cu_charstrings(font: Font, tolerance: float = 1.0):
    qu2cu_charstrings = {}
    failed = []
    glyph_set = font.getGlyphSet()

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
        try:
            glyph_set[k].draw(qu2cu_pen)
            qu2cu_charstrings[k] = t2_pen.getCharString()
        except NotImplementedError as e:
            generic_warning_message(f"{k}: {e}")
            failed.append(k)

    return failed, qu2cu_charstrings


def get_makeotf_charstrings(font: Font) -> dict:
    makeotf_fd, makeotf_file = font.make_temp_otf()
    fallback_otf = Font(makeotf_file)
    fallback_otf.otf_fix_contours(verbose=False)
    makeotf_charstrings = get_t2_charstrings(fallback_otf)
    fallback_otf.close()
    os.close(makeotf_fd)
    os.remove(makeotf_file)
    return makeotf_charstrings


def get_t2_charstrings(font: Font) -> dict:
    """
    Get CFF charstrings using T2CharStringPen

    :return: CFF charstrings.
    """
    t2_charstrings = {}
    glyph_set = font.getGlyphSet()

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        glyph_set[k].draw(t2_pen)
        charstring = t2_pen.getCharString()
        t2_charstrings[k] = charstring

    return t2_charstrings

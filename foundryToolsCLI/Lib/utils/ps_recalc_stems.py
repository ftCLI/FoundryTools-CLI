import typing as t

from pathlib import Path

from afdko.otfautohint.__main__ import ReportOptions, get_stemhist_options, _validate_path
from afdko.otfautohint.autohint import fontWrapper, FontInstance, openFont
from afdko.otfautohint.hinter import glyphHinter
from afdko.otfautohint.report import Report

H_STEM_GLYPHS = ["A", "H", "T", "S", "C", "O"]
V_STEM_GLYPHS = ["E", "H", "I", "K", "L", "M", "N", "T", "U"]

__all__ = ["get_stems", "recalc_stems"]


def get_stems(
    file_path: Path, glyph_list: t.List[str]
) -> t.Tuple[t.List[t.Tuple[int, int, t.List[str]]], t.List[t.Tuple[int, int, t.List[str]]]]:
    """
    Retrieves stem data from a font file for a given list of glyphs.

    Parameters:
        file_path`: The path to the font file.
        glyph_list`: A list of glyph names for which stem data will be
        retrieved.

    Returns:
        Tuple: a tuple containing two lists: the first list contains the horizontal stem data,
        and the second list contains the vertical stem data. Each list contains tuples of the
        form (stem width, stem count, glyph names).
    """
    file_path = _validate_path(file_path)
    _, parsed_args = get_stemhist_options(args=[file_path])
    options = ReportOptions(parsed_args)
    options.report_all_stems = True
    options.report_zones = False
    options.glyphList = glyph_list

    font = openFont(file_path, options=options)
    font_instance = FontInstance(font=font, inpath=file_path, outpath=file_path)

    fw = fontWrapper(options=options, fil=[font_instance])
    dict_record = fw.dictManager.getDictRecord()

    hinter = glyphHinter(options=options, dictRecord=dict_record)
    hinter.initialize(options=options, dictRecord=dict_record)
    gmap = map(hinter.hint, fw)

    report = Report()
    for name, r in gmap:
        report.glyphs[name] = r

    h_stems, v_stems, _, _ = report._get_lists(options)
    h_stems.sort(key=report._sort_count)
    v_stems.sort(key=report._sort_count)

    return h_stems, v_stems


def recalc_stems(
    file_path: Path,
    h_stems_glyphs: t.Optional[t.List[str]] = None,
    v_stems_glyphs: t.Optional[t.List[str]] = None,
) -> t.Tuple[int, int]:
    """
    Recalculates the StdHW and StdVW values for a given font file.

    Parameters:
        file_path: A `Path` object representing the path to the file.
        h_stems_glyphs: A list of glyph names to use for calculating the horizontal stems.
        v_stems_glyphs: A list of glyph names to use for calculating the vertical stems.

    Returns:
        A tuple containing the recalculated stem values for horizontal and vertical stems. The first
        value in the tuple represents the horizontal stem value, and the second value represents the
        vertical stem value.
    """

    if h_stems_glyphs is None:
        h_stems_glyphs = H_STEM_GLYPHS
    if v_stems_glyphs is None:
        v_stems_glyphs = V_STEM_GLYPHS

    h_stems, _ = get_stems(file_path=file_path, glyph_list=h_stems_glyphs)
    _, v_stems = get_stems(file_path=file_path, glyph_list=v_stems_glyphs)

    if not h_stems:
        raise ValueError("No horizontal stems found")
    if not v_stems:
        raise ValueError("No vertical stems found")

    return int(h_stems[0][1]), int(v_stems[0][1])

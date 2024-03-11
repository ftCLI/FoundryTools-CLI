import itertools
from collections.abc import Mapping, Callable

import pathops
from fontTools.misc.roundTools import otRound
from fontTools.pens.t2CharStringPen import T2CharStringPen, T2CharString
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import ttFont
from fontTools.ttLib.tables import _g_l_y_f
from fontTools.ttLib.ttGlyphSet import _TTGlyphSet

from foundryToolsCLI.Lib.utils.logger import logger, Logs

_TTGlyphMapping = Mapping[str, ttFont._TTGlyph]


def remove_tiny_paths(path: pathops.Path, glyph_name, min_area: int = 25, verbose: bool = True):
    """
    Removes tiny paths from a pathops.Path.

    :param path: the path from which to remove the tiny paths
    :param glyph_name: the glyph name
    :param min_area: the minimum are of a path
    :param verbose: if True, logs the removed tiny paths
    :return: the cleaned path
    """
    cleaned_path = pathops.Path()
    for contour in path.contours:
        if contour.area >= min_area:
            cleaned_path.addPath(contour)
        else:
            if verbose:
                logger.info(Logs.tiny_path_removed, glyph_name=glyph_name)
    return cleaned_path


def skia_path_from_glyph(glyph_name: str, glyph_set: _TTGlyphMapping) -> pathops.Path:
    """
    Returns a pathops.Path from a glyph

    :param glyph_name: the glyph name
    :param glyph_set: the glyphSet to which the glyph belongs
    :return: a pathops.Path object
    """
    path = pathops.Path()
    pen = path.getPen(glyphSet=glyph_set)
    glyph_set[glyph_name].draw(pen)
    return path


def skia_path_from_component(component: _g_l_y_f.GlyphComponent, glyph_set: _TTGlyphMapping):
    base_glyph_name, transformation = component.getComponentInfo()
    path = skia_path_from_glyph(glyph_name=base_glyph_name, glyph_set=glyph_set)
    return path.transform(*transformation)


def ttf_glyph_from_skia_path(path: pathops.Path) -> _g_l_y_f.Glyph:
    tt_pen = TTGlyphPen(glyphSet=None)
    path.draw(tt_pen)
    glyph = tt_pen.glyph()
    glyph.recalcBounds(glyfTable=None)
    return glyph


def t2_charstring_from_skia_path(path: pathops.Path, width: int) -> T2CharString:
    t2_pen = T2CharStringPen(width, glyphSet=None)
    path.draw(t2_pen)
    charstring = t2_pen.getCharString()
    return charstring


def round_path(path: pathops.Path, rounder: Callable[[float], float] = otRound) -> pathops.Path:
    """
    Rounds the points coordinate of a pathops.Path

    :param path: the path to round
    :param rounder: the function to call
    :return: the path with rounded points
    """
    rounded_path = pathops.Path()
    for verb, points in path:
        rounded_path.add(verb, *((rounder(p[0]), rounder(p[1])) for p in points))
    return rounded_path


def simplify_path(path: pathops.Path, glyph_name: str, clockwise: bool) -> pathops.Path:
    """
    Simplify a pathops.Path by removing overlaps, fixing contours direction and, optionally, removing tiny paths

    :param path: the pathops.Path to simplify
    :param glyph_name: the glyph name
    :param clockwise: must be True for TTF fonts, False for OTF fonts
    :return: the simplified path
    """

    # skia-pathops has a bug where it sometimes fails to simplify paths when there
    # are float coordinates and control points are very close to one another.
    # Rounding coordinates to integers works around the bug.
    # Since we are going to round glyf coordinates later on anyway, here it is
    # ok(-ish) to also round before simplify. Better than failing the whole process
    # for the entire font.
    # https://bugs.chromium.org/p/skia/issues/detail?id=11958
    # https://github.com/google/fonts/issues/3365

    try:
        return pathops.simplify(path, fix_winding=True, clockwise=clockwise)
    except pathops.PathOpsError:
        pass

    path = round_path(path)
    try:
        path = pathops.simplify(path, fix_winding=True, clockwise=clockwise)
        logger.info(
            f"skia-pathops failed to simplify glyph '{glyph_name}' with float coordinates, but succeeded using rounded "
            f"integer coordinates"
        )
        return path
    except pathops.PathOpsError as e:
        logger.error(f"skia-pathops failed to simplify glyph '{glyph_name}': {e}")

    raise AssertionError("Unreachable")


def same_path(path_1: pathops.Path, path_2: pathops.Path) -> bool:
    """
    Checks if two pathops paths are the same

    :param path_1: the first path
    :param path_2: the second path
    :return: True if the paths are the same, False if the paths are different
    """
    if {tuple(c) for c in path_1.contours} != {tuple(c) for c in path_2.contours}:
        return False
    else:
        return True


def ttf_components_overlap(glyph: _g_l_y_f.Glyph, glyph_set: _TTGlyphMapping) -> bool:
    if not glyph.isComposite():
        raise ValueError("This method only works with TrueType composite glyphs")
    if len(glyph.components) < 2:
        return False

    component_paths = {}

    def _get_nth_component_path(index: int) -> pathops.Path:
        if index not in component_paths:
            component_paths[index] = skia_path_from_glyph_component(
                glyph.components[index], glyph_set
            )
        return component_paths[index]

    return any(
        pathops.op(
            _get_nth_component_path(i),
            _get_nth_component_path(j),
            pathops.PathOp.INTERSECTION,
            fix_winding=True,
            keep_starting_points=False,
            clockwise=True,
        )
        for i, j in itertools.combinations(range(len(glyph.components)), 2)
    )


def skia_path_from_glyph_component(component: _g_l_y_f.GlyphComponent, glyph_set: _TTGlyphMapping):
    base_glyph_name, transformation = component.getComponentInfo()
    path = skia_path_from_glyph(base_glyph_name, glyph_set)
    return path.transform(*transformation)


def is_empty_glyph(glyph_set: _TTGlyphSet, glyph_name: str) -> bool:
    """
    Returns True if the glyph is empty.

    Parameters:
        glyph_set (_TTGlyphSet): The glyph set.
        glyph_name (str): The name of the glyph.

    Returns:
        bool: True if the glyph is empty.
    """

    path = skia_path_from_glyph(glyph_name=glyph_name, glyph_set=glyph_set)
    return path.area == 0

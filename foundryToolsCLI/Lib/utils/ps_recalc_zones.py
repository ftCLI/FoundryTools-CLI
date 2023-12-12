import typing as t
from collections import Counter

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.ttFont import TTFont

UPPERCASE_LETTERS = [chr(i) for i in range(65, 91)]  # A-Z
UPPERCASE_DESCENDERS = ["J", "Q"]
LOWERCASE_LETTERS = [chr(i) for i in range(97, 123)]  # a-z
LOWERCASE_DESCENDERS = ["f", "g", "j", "p", "q", "y"]
LOWERCASE_ASCENDERS = ["b", "d", "f", "h", "k", "l", "t"]

DESCENDER_GLYPHS = list(set(LOWERCASE_DESCENDERS) - {"f", "j"})
BASELINE_GLYPHS = list(
    set(UPPERCASE_LETTERS + LOWERCASE_LETTERS)
    - set(LOWERCASE_DESCENDERS)
    - set(UPPERCASE_DESCENDERS)
)
X_HEIGHT_GLYPHS = list(set(LOWERCASE_LETTERS) - set(LOWERCASE_ASCENDERS + ["i", "j"]))
UPPERCASE_GLYPHS = UPPERCASE_LETTERS
ASCENDER_GLYPHS = list(set(LOWERCASE_ASCENDERS) - {"t"})


__all__ = ["recalc_zones", "GlyphBounds"]


class GlyphBounds(t.TypedDict):
    """
    A type representing the bounds of a glyph.
    """

    xMin: float
    yMin: float
    xMax: float
    yMax: float


def get_glyph_bounds(font: TTFont, glyph_name: str) -> GlyphBounds:
    """
    Get the bounds of a glyph.

    Parameters:
        font (TTFont): The TTFont object.
        glyph_name (str): The name of the glyph.

    Returns:
        GlyphBounds: The bounds of the glyph.

    Raises:
        ValueError: If the glyph does not exist in the font.
    """
    glyph_set = font.getGlyphSet()
    if glyph_name not in glyph_set:
        raise ValueError(f"Glyph '{glyph_name}' does not exist in the font.")

    bounds_pen = BoundsPen(glyphSet=glyph_set)

    glyph_set[glyph_name].draw(bounds_pen)
    bounds = GlyphBounds(
        xMin=bounds_pen.bounds[0],
        yMin=bounds_pen.bounds[1],
        xMax=bounds_pen.bounds[2],
        yMax=bounds_pen.bounds[3],
    )

    return bounds


def get_glyph_bounds_many(font: TTFont, glyph_names: t.List[str]) -> t.Dict[str, GlyphBounds]:
    """
    Get the bounds of multiple glyphs in a given font.

    Parameters:
        font (TTFont): The TTFont object.
        glyph_names (List[str]): A list of glyph names.

    Returns:
        dict: A dictionary containing glyph names as keys and GlyphBounds objects as values.
    """
    glyphs_bounds = {}
    for glyph_name in glyph_names:
        try:
            bounds = get_glyph_bounds(font=font, glyph_name=glyph_name)
            glyphs_bounds[glyph_name] = bounds
        except ValueError:
            pass

    return glyphs_bounds


def get_pair(counter: Counter) -> t.List[float]:
    """
    Get the two most common elements from the given counter.

    Parameters:
        counter (Counter): The counter object containing elements and their counts.

    Returns:
        List[float]: List containing the pair of most common elements.
    """
    most_common = counter.most_common(2)
    if len(counter) == 1:
        return [most_common[0][0], most_common[0][0]]
    return sorted([most_common[0][0], most_common[1][0]])


def lists_overlaps(lists: t.List[t.List[float]]) -> bool:
    """
    Check if there are overlapping intervals in a list of lists.

    Args:
        lists (List[List[float]]): A list of lists, where each inner list represents an interval.

    Returns:
        bool: True if there are overlapping intervals, False otherwise.
    """
    for i in range(len(lists) - 1):
        if lists[i][1] > lists[i + 1][0]:
            return True
    return False


def fix_lists_overlaps(lists: t.List[t.List[float]]) -> t.List[t.List[float]]:
    """
    Fixes overlaps in a list of lists of floats.

    Args:
        lists (List[List[float]]): A list of lists of floats.

    Returns:
        List[List[float]]: The input list with any overlaps fixed.
    """
    for i in range(len(lists) - 1):
        if lists[i][1] > lists[i + 1][0]:
            lists[i + 1][0] = lists[i][1]
            lists[i + 1] = sorted(lists[i + 1])
    return lists


def fix_min_separation_limits(lists: t.List[t.List[float]], limit: int) -> t.List[t.List[float]]:
    """
    Fixes the minimum separation between zones.

    Args:
        lists (List[List[float]]): A list of lists of floats.
        limit (int): The minimum separation between zones.

    Returns:
        List[List[float]]: The input list with the minimum separation between zones fixed.
    """
    for i in range(len(lists) - 1):
        if lists[i + 1][0] - lists[i][1] < limit:
            # If the difference between the two values is less than 3, then
            # set the second value to the first value
            if lists[i + 1][1] - lists[i][1] > limit:
                lists[i + 1][0] = lists[i + 1][1]
            else:
                # Remove the second list
                lists.pop(i + 1)
    return lists


def calculate_zone(
    font: TTFont, glyph_names: t.List[str], min_or_max: t.Literal["yMin", "yMax"]
) -> t.List[float]:
    """
    Calculates the minimum and maximum vertical values for a given zone.

    Parameters:
        font: TTFont object representing the font.
        glyph_names: List of glyph names to process.
        min_or_max: Literal specifying whether to process the minimum ('yMin') or maximum ('yMax')
            values.

    Returns:
        List of float values representing the minimum or maximum vertical values for each glyph.

    """
    data = get_glyph_bounds_many(font=font, glyph_names=glyph_names)
    counter = Counter([v[min_or_max] for v in data.values()])
    return get_pair(counter)


def recalc_zones(
    font: TTFont,
    descender_glyphs: t.Optional[t.List[str]] = None,
    baseline_glyphs: t.Optional[t.List[str]] = None,
    x_height_glyphs: t.Optional[t.List[str]] = None,
    uppercase_glyphs: t.Optional[t.List[str]] = None,
    ascender_glyphs: t.Optional[t.List[str]] = None,
) -> t.Tuple[t.List[int], t.List[int]]:
    """
    Recalc Zones

    Recalculates the zones for a given TTFont object.

    Parameters:
        font (TTFont): The TTFont object.
        descender_glyphs (List[str]): A list of glyph names to use for calculating the descender
            zone.
        baseline_glyphs (List[str]): A list of glyph names to use for calculating the baseline
            zone.
        x_height_glyphs (List[str]): A list of glyph names to use for calculating the x-height
            zone.
        uppercase_glyphs (List[str]): A list of glyph names to use for calculating the uppercase
            zone.
        ascender_glyphs (List[str]): A list of glyph names to use for calculating the ascender
            zone.

    Returns:
        Tuple[List[int], List[int]]: A tuple containing two lists. The first list contains the
            values for the OtherBlues zones, and the second list contains the values for the
            BlueValues zones.
    """

    if descender_glyphs is None:
        descender_glyphs = DESCENDER_GLYPHS
    if baseline_glyphs is None:
        baseline_glyphs = BASELINE_GLYPHS
    if x_height_glyphs is None:
        x_height_glyphs = X_HEIGHT_GLYPHS
    if uppercase_glyphs is None:
        uppercase_glyphs = UPPERCASE_GLYPHS
    if ascender_glyphs is None:
        ascender_glyphs = ASCENDER_GLYPHS

    descender_zone = calculate_zone(font=font, glyph_names=descender_glyphs, min_or_max="yMin")
    baseline_zone = calculate_zone(font=font, glyph_names=baseline_glyphs, min_or_max="yMin")
    x_height_zone = calculate_zone(font=font, glyph_names=x_height_glyphs, min_or_max="yMax")
    uppercase_zone = calculate_zone(font=font, glyph_names=uppercase_glyphs, min_or_max="yMax")
    ascender_zone = calculate_zone(font=font, glyph_names=ascender_glyphs, min_or_max="yMax")

    zones = sorted([descender_zone, baseline_zone, x_height_zone, uppercase_zone, ascender_zone])
    if lists_overlaps(zones):
        zones = fix_lists_overlaps(zones)

    min_separation = font["CFF "].cff.topDictIndex[0].Private.BlueFuzz * 2 + 1
    zones = fix_min_separation_limits(zones, limit=min_separation)

    other_blues = [int(v) for v in zones[0]]

    blue_values = []
    for zone in zones[1:]:
        blue_values.extend([int(v) for v in zone])

    return other_blues, blue_values

from fontTools.misc.psCharStrings import T2CharString


def get_glyph_bounds(glyph_set, glyph_name: str) -> dict:
    if glyph_set.get(glyph_name) is None:
        return dict(xMin=0, yMin=0, xMax=0, yMax=0)
    bounds = T2CharString.calcBounds(glyph_set[glyph_name], glyph_set)
    if bounds:
        return dict(xMin=bounds[0], yMin=bounds[1], xMax=bounds[2], yMax=bounds[3])
    else:
        return dict(xMin=0, yMin=0, xMax=0, yMax=0)


def get_glyphs_bounds_all(glyph_set) -> dict:
    metrics = {}
    for glyph_name in glyph_set.keys():
        bounds = T2CharString.calcBounds(glyph_set[glyph_name], glyph_set)
        if bounds:
            metrics[glyph_name] = dict(xMin=bounds[0], yMin=bounds[1], xMax=bounds[2], yMax=bounds[3])
        else:
            metrics[glyph_name] = None

    return metrics

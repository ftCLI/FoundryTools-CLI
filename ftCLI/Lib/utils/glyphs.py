from fontTools.misc.psCharStrings import T2CharString


def get_glyph_bounds(glyph_set, glyph_name: str) -> dict:
    if glyph_set.get(glyph_name) is None:
        return dict(xMin=0, yMin=0, xMax=0, yMax=0)
    bounds = T2CharString.calcBounds(glyph_set[glyph_name], glyph_set)
    if bounds is not None:
        return dict(xMin=bounds[0], yMin=bounds[1], xMax=bounds[2], yMax=bounds[3])
    else:
        return dict(xMin=0, yMin=0, xMax=0, yMax=0)


def get_glyphs_metrics_all(glyph_set):
    mtx = {}
    for glyph_name in glyph_set.keys():
        bounds = T2CharString.calcBounds(glyph_set[glyph_name], glyph_set)
        if bounds is not None:
            mtx[glyph_name] = dict(xMin=bounds[0], yMin=bounds[1], xMax=bounds[2], yMax=bounds[3])
        else:
            mtx[glyph_name] = None
    # print(mtx)

    # for i in mtx.values():
    # print(i)

    lowest_glyph = None
    min_y = 99999
    for k, v in mtx.items():
        # print(k, v)
        if v:
            if v["yMin"] < min_y:
                min_y = v["yMin"]
                lowest_glyph = {k: v}

    print(lowest_glyph)

    max_y = -99999

    # max_y = max([metric['yMax'] for metric in mtx.values() if metric])
    # max_y = max([metric['yMax'] for metric in mtx])

    # print()
    # print(min_y)
    # print(max_y)

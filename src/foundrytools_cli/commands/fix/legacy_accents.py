from foundrytools import Font
from foundrytools.constants import T_CMAP, T_GDEF, T_HMTX
from foundrytools.core.tables import GdefTable

from foundrytools_cli.utils.logger import logger


def fix_legacy_accents(font: Font) -> bool:
    """Check that legacy accents aren't used in composite glyphs."""

    # code-points for all legacy chars
    legacy_accents = {
        0x00A8,  # DIAERESIS
        0x02D9,  # DOT ABOVE
        0x0060,  # GRAVE ACCENT
        0x00B4,  # ACUTE ACCENT
        0x02DD,  # DOUBLE ACUTE ACCENT
        0x02C6,  # MODIFIER LETTER CIRCUMFLEX ACCENT
        0x02C7,  # CARON
        0x02D8,  # BREVE
        0x02DA,  # RING ABOVE
        0x02DC,  # SMALL TILDE
        0x00AF,  # MACRON
        0x00B8,  # CEDILLA
        0x02DB,  # OGONEK
    }

    reverse_cmap = font.ttfont[T_CMAP].buildReversed()
    hmtx = font.ttfont[T_HMTX]

    # Check whether legacy accents have positive width. Just print a warning if they don't.
    for name in reverse_cmap:
        if reverse_cmap[name].intersection(legacy_accents) and hmtx[name][0] == 0:
            logger.warning(
                f'Width of legacy accent "{name}" is zero; should be positive.',
            )

    # Check whether legacy accents appear in GDEF as marks.
    # Not being marks in GDEF also typically means that they don't have anchors, as font compilers
    # would have otherwise classified them as marks in GDEF.
    if T_GDEF in font.ttfont and font.ttfont[T_GDEF].table.GlyphClassDef:
        deleted = set()
        gdef = GdefTable(ttfont=font.ttfont)
        class_defs = gdef.table.table.GlyphClassDef.classDefs
        for name in reverse_cmap:
            if (
                reverse_cmap[name].intersection(legacy_accents)
                and name in class_defs
                and class_defs[name] == 3
            ):
                del class_defs[name]
                deleted.add(name)

        if deleted:
            logger.info(
                f"Deleted {len(deleted)} legacy accents from GDEF table: {', '.join(deleted)}"
            )
            return True

    return False

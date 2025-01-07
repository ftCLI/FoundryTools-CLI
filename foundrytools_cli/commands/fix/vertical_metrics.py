from foundrytools import Font


def main(font: Font, safe_bottom: int, safe_top: int) -> bool:
    """
    Adjusts the vertical metrics of a font to ensure consistency across the family.
    """

    font.t_os_2.win_ascent = safe_top
    font.t_os_2.win_descent = abs(safe_bottom)
    font.t_os_2.typo_ascender = safe_top
    font.t_os_2.typo_descender = safe_bottom
    font.t_os_2.typo_line_gap = 0
    font.t_hhea.ascent = safe_top
    font.t_hhea.descent = safe_bottom
    font.t_hhea.line_gap = 0

    # Set the USE_TYPO_METRICS bit
    if font.t_os_2.version >= 4:
        font.t_os_2.fs_selection.use_typo_metrics = True

    return font.t_os_2.is_modified or font.t_hhea.is_modified

from shutil import get_terminal_size
from typing import Any

from fontTools.misc.timeTools import timestampToString
from foundrytools import Font
from rich.console import Console
from rich.table import Table

from foundrytools_cli.utils import wrap_string

TERMINAL_WIDTH = 120
FONT_STYLE = "[bold cyan]Font file: {name}[reset]"


def _get_font_info(font: Font) -> dict[str, dict[str, str]]:
    font_info = {
        "sfnt_versions": {
            "label": "SFNT version",
            "value": "PostScript" if font.is_ps else "TrueType",
        },
        "flavor": {"label": "Flavor", "value": font.ttfont.flavor},
        "glyphs_number": {"label": "Number of glyphs", "value": font.ttfont["maxp"].numGlyphs},
        "family_name": {"label": "Family name", "value": font.t_name.get_best_family_name()},
        "subfamily_name": {
            "label": "Subfamily name",
            "value": font.t_name.get_best_subfamily_name(),
        },
        "full_name": {"label": "Full name", "value": font.t_name.get_debug_name(4)},
        "postscript_name": {"label": "PostScript name", "value": font.t_name.get_debug_name(6)},
        "unique_identifier": {"label": "Unique ID", "value": font.t_name.get_debug_name(3)},
        "vendor_code": {"label": "Vendor code", "value": font.t_os_2.vendor_id},
        "version": {"label": "Version", "value": str(round(font.t_head.font_revision, 3))},
        "date_created": {
            "label": "Date created",
            "value": timestampToString(font.t_head.created_timestamp),
        },
        "date_modified": {
            "label": "Date modified",
            "value": timestampToString(font.t_head.modified_timestamp),
        },
        "us_width_class": {"label": "usWidthClass", "value": font.t_os_2.width_class},
        "us_weight_class": {"label": "usWeightClass", "value": font.t_os_2.weight_class},
        "is_bold": {"label": "Font is bold", "value": font.flags.is_bold},
        "is_italic": {"label": "Font is italic", "value": font.flags.is_italic},
        "is_oblique": {"label": "Font is oblique", "value": font.flags.is_oblique},
        "is_wws_consistent": {
            "label": "WWS consistent",
            "value": font.t_os_2.fs_selection.wws_consistent,
        },
        "use_typo_metrics": {
            "label": "Use Typo Metrics",
            "value": font.t_os_2.fs_selection.use_typo_metrics,
        },
        "underline_position": {"label": "UL position", "value": font.t_post.underline_position},
        "underline_thickness": {"label": "UL thickness", "value": font.t_post.underline_thickness},
        "italic_angle": {"label": "Italic angle", "value": font.t_post.italic_angle},
        "caret_slope_rise": {"label": "Caret Slope Rise", "value": font.t_hhea.caret_slope_rise},
        "caret_slope_run": {"label": "Caret Slope Run", "value": font.t_hhea.caret_slope_run},
        "caret_offset": {"label": "Caret Offset", "value": font.t_hhea.caret_offset},
        "embed_level": {"label": "Embedding", "value": f"{font.t_os_2.embed_level}"},
    }

    return font_info


def _get_v_metrics(font: Font) -> dict[str, list[dict[str, Any]]]:
    font_v_metrics: dict[str, list[dict[str, Any]]] = {
        "os2_metrics": [
            {"label": "sTypoAscender", "value": font.t_os_2.typo_ascender},
            {"label": "sTypoDescender", "value": font.t_os_2.typo_descender},
            {"label": "sTypoLineGap", "value": font.t_os_2.typo_line_gap},
            {"label": "usWinAscent", "value": font.t_os_2.win_ascent},
            {"label": "usWinDescent", "value": font.t_os_2.win_descent},
        ],
        "hhea_metrics": [
            {"label": "ascent", "value": font.t_hhea.ascent},
            {"label": "descent", "value": font.t_hhea.descent},
            {"label": "lineGap", "value": font.t_hhea.line_gap},
        ],
        "head_metrics": [
            {"label": "unitsPerEm", "value": font.t_head.units_per_em},
            {"label": "xMin", "value": font.t_head.x_min},
            {"label": "yMin", "value": font.t_head.y_min},
            {"label": "xMax", "value": font.t_head.x_max},
            {"label": "yMax", "value": font.t_head.y_max},
            {
                "label": "Font BBox",
                "value": f"({font.t_head.x_min}, {font.t_head.y_min}) "
                f"({font.t_head.x_max}, {font.t_head.y_max})",
            },
        ],
    }

    return font_v_metrics


def _get_feature_tags(font: Font) -> list[str]:
    """
    Returns a sorted list of all the feature tags in the font's GSUB and GPOS tables

    :return: A list of feature tags.
    """
    feature_tags = set[str]()
    for table_tag in ("GSUB", "GPOS"):
        if table_tag in font.ttfont:
            if (
                not font.ttfont[table_tag].table.ScriptList
                or not font.ttfont[table_tag].table.FeatureList
            ):
                continue
            feature_tags.update(
                feature_record.FeatureTag
                for feature_record in font.ttfont[table_tag].table.FeatureList.FeatureRecord
            )
    return sorted(feature_tags)


def main(font: Font) -> None:
    """
    Prints a table with the font's basic information, vertical metrics, font tables, and font
    features

    :param font: The Font object to print information about
    :type font: Font
    """

    terminal_width = min(TERMINAL_WIDTH, get_terminal_size()[0] - 1)

    table = Table(
        title="\nftCLI - Font Info Viewer",
        title_style="bold green",
        show_header=False,
    )

    font_info = _get_font_info(font)
    v_metrics = _get_v_metrics(font)
    feature_tags = _get_feature_tags(font)

    table.add_row(FONT_STYLE.format(name=font.file.name if font.file else font.bytesio))
    table.add_section()

    sub_table_1 = Table(box=None, show_header=False)
    for v in font_info.values():
        sub_table_1.add_row(f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value'])}")

    sub_table_2 = Table(box=None, show_header=False)
    for v in v_metrics["os2_metrics"]:
        sub_table_2.add_row(
            f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}"
        )

    sub_table_3 = Table(box=None, show_header=False)
    for v in v_metrics["hhea_metrics"]:
        sub_table_3.add_row(
            f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}"
        )

    sub_table_4 = Table(box=None, show_header=False)
    for v in v_metrics["head_metrics"]:
        sub_table_4.add_row(
            f"[bold cyan]{v['label'].ljust(16)}[reset] : {str(v['value']).rjust(4)}"
        )

    table.add_row("[bold green]BASIC INFORMATION")
    table.add_section()
    table.add_row(sub_table_1)
    table.add_section()
    table.add_row("[bold green]VERTICAL METRICS")
    table.add_section()
    table.add_row("[bold magenta]OS/2 table")
    table.add_row(sub_table_2)
    table.add_row("\n[bold magenta]hhea table")
    table.add_row(sub_table_3)
    table.add_row("\n[bold magenta]head table")
    table.add_row(sub_table_4)
    table.add_section()
    table.add_row(f"[bold green]FONT TABLES[reset] ({len(font.ttfont.keys())})")
    table.add_section()
    table.add_row(
        wrap_string(
            string=", ".join(list(font.ttfont.keys())),
            initial_indent=0,
            indent=0,
            width=terminal_width,
        )
    )
    if len(feature_tags) > 0:
        table.add_section()
        table.add_row(f"[bold green]FONT FEATURES[reset] ({len(feature_tags)})")
        table.add_section()
        table.add_row(
            wrap_string(
                string=", ".join([str(t) for t in feature_tags]),
                initial_indent=0,
                indent=0,
                width=terminal_width,
            )
        )

    console = Console()
    console.print(table)

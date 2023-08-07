import os
from copy import deepcopy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.tables.OS_2 import TableOS2
from foundryToolsCLI.Lib.tables.hhea import TableHhea
from foundryToolsCLI.Lib.tables.name import TableName
from foundryToolsCLI.Lib.tables.post import TablePost
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, get_output_dir, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    generic_error_message,
    file_saved_message,
    file_not_changed_message,
    generic_warning_message,
    generic_success_message,
    generic_info_message,
)

fix_fonts = click.Group("subcommands")


@fix_fonts.command()
@add_file_or_path_argument()
@add_common_options()
def monospace(input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True):
    """
    If the family is monospaced:

    \b
    * post.isFixedPitch must be set to a non-zero value
    * OS/2.panose.bProportion must be set to 9
    * CFF.cff.TopDictIndex[0].isFixedPitch must be set to True

    fontbakery check id: com.google.fonts/check/monospace
    """

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            post_table: TablePost = font["post"]
            os2_table: TableOS2 = font["OS/2"]
            post_table_copy = deepcopy(post_table)
            os2_table_copy = deepcopy(os2_table)

            post_table.set_fixed_pitch(True)

            if os2_table.panose.bProportion != 9:
                os2_table.panose.bProportion = 9
                # Ensure that panose.bFamilyType is non-zero when panose.bProportion is 9
                if os2_table.panose.bFamilyType == 0:
                    os2_table.panose.bFamilyType = 2

            post_table_changed = False
            if post_table_copy.compile(font) != post_table.compile(font):
                post_table_changed = True

            os2_table_changed = False
            if os2_table_copy.compile(font) != os2_table.compile(font):
                os2_table_changed = True

            cff_table_changed = False
            if font.is_otf:
                cff_table = font["CFF "]
                cff_table_copy = deepcopy(cff_table)
                top_dict = cff_table.cff.topDictIndex[0]
                setattr(top_dict, "isFixedPitch", True)

                if cff_table_copy.compile(font) != cff_table.compile(font):
                    cff_table_changed = True

            if post_table_changed or os2_table_changed or cff_table_changed:
                font.save(output_file)
                file_saved_message(output_file)

            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_common_options()
def nbsp_width(input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True):
    """
    Checks if 'nbspace' and 'space' glyphs have the same width. If not, corrects 'nbspace' width to match 'space' width.

    fontbakery check id: com.google.fonts/check/whitespace_widths
    """

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            hmtx_table = font["hmtx"]
            hmtx_table_copy = deepcopy(hmtx_table)

            best_cmap = font.getBestCmap()
            space_name = best_cmap[0x0020]
            nbspace_name = best_cmap[0x00A0]

            font["hmtx"][nbspace_name] = font["hmtx"][space_name]

            if hmtx_table_copy.compile(font) != hmtx_table.compile(font):
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@click.option(
    "-m",
    "--mode",
    type=click.IntRange(1, 3),
    default=1,
    help="""
              \b
              1: sets only the italic bits and clears the oblique bit
              2: sets italic and oblique bits
              3: sets only the oblique bit and clears italic bits
              """,
)
@add_common_options()
def italic_angle(
    input_path: Path, mode: int = 1, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True
):
    """
    Recalculates post.italicAngle, hhea.caretSlopeRise, hhea.caretSlopeRun and sets/clears the italic/oblique bits
    according to the calculated values. In CFF fonts, also CFF.topDictIndex[0].ItalicAngle is recalculated.
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        print()

        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            generic_info_message(f"Checking file: {file.name}")

            post_table: TablePost = font["post"]
            hhea_table: TableHhea = font["hhea"]

            # Check post.italicAngle
            post_italic_angle = post_table.italicAngle
            calculated_post_italic_angle = font.calculate_italic_angle()
            post_italic_angle_ok = font.check_italic_angle()
            if post_italic_angle_ok:
                generic_success_message(
                    f"post.italicAngle    : {click.style(post_italic_angle, fg='green', bold=True)}"
                )
            else:
                post_table.set_italic_angle(calculated_post_italic_angle)
                generic_warning_message(
                    f"post.italicAngle    : "
                    f"{click.style(post_italic_angle, fg='red', bold=True)} -> "
                    f"{click.style(calculated_post_italic_angle, fg='green', bold=True)}"
                )

            calculated_rise = font.calculate_caret_slope_rise()
            calculated_run = font.calculate_caret_slope_run()

            # Check hhea italic angle
            rise = hhea_table.caretSlopeRise
            run = hhea_table.caretSlopeRun
            hhea_italic_angle = font.calculate_run_rise_angle()
            hhea_italic_angle_ok = abs(post_table.italicAngle - hhea_italic_angle) < 0.1
            if hhea_italic_angle_ok:
                generic_success_message(f"hhea.caretSlopeRise : {click.style(rise, fg='green', bold=True)}")
                generic_success_message(f"hhea.caretSlopeRun  : {(click.style(run, fg='green', bold=True))}")
            else:
                hhea_table.caretSlopeRise = calculated_rise
                generic_warning_message(
                    f"hhea.caretSlopeRise : {click.style(rise, fg='red', bold=True)} -> "
                    f"{click.style(calculated_rise, fg='green', bold=True)}"
                )
                hhea_table.caretSlopeRun = calculated_run
                generic_warning_message(
                    f"hhea.caretSlopeRun  : {click.style(run, fg='red', bold=True)} -> "
                    f"{click.style(calculated_run, fg='green', bold=True)}"
                )

            # Check CFF italic angle
            if font.is_otf:
                cff_table = font["CFF "]
                cff_italic_angle = cff_table.cff.topDictIndex[0].ItalicAngle
                cff_italic_angle_ok = cff_italic_angle == round(post_table.italicAngle)

                if cff_italic_angle_ok:
                    generic_success_message(
                        f"CFF.ItalicAngle     : " f"{click.style(cff_italic_angle, fg='green', bold=True)}"
                    )
                else:
                    cff_table.cff.topDictIndex[0].ItalicAngle = round(post_table.italicAngle)
                    generic_warning_message(
                        f"CFF.ItalicAngle     : "
                        f"{click.style(cff_italic_angle, fg='red', bold=True)} -> "
                        f"{click.style(cff_table.cff.topDictIndex[0].ItalicAngle, fg='green', bold=True)}"
                    )
            else:
                cff_italic_angle_ok = True

            # Set or clear italic/oblique bits according to post.italicAngle
            is_italic = font.is_italic
            is_oblique = font.is_oblique
            font.calculate_italic_bits(mode=mode)

            if font.is_italic == is_italic:
                italic_bits_ok = True
            else:
                italic_bits_ok = False

            if font.is_oblique == is_oblique:
                oblique_bit_ok = True
            else:
                oblique_bit_ok = False

            if italic_bits_ok:
                generic_success_message(f"Italic              : " f"{click.style(is_italic, fg='green', bold=True)}")
            else:
                generic_info_message(
                    f"Italic              : "
                    f"{click.style(is_italic, fg='red', bold=True)} -> "
                    f"{click.style(font.is_italic, fg='green', bold=True)}"
                )

            if oblique_bit_ok:
                generic_success_message(f"Oblique             : " f"{click.style(is_oblique, fg='green', bold=True)}")
            else:
                generic_info_message(
                    f"Oblique             : "
                    f"{click.style(is_oblique, fg='red', bold=True)} -> "
                    f"{click.style(font.is_oblique, fg='green', bold=True)}"
                )

            # Don't save the file if nothing has been modified
            if (
                post_italic_angle_ok
                and hhea_italic_angle_ok
                and cff_italic_angle_ok
                and italic_bits_ok
                and oblique_bit_ok
            ):
                file_not_changed_message(file)
                continue

            font.save(output_file)
            file_saved_message(output_file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_common_options()
def nbsp_missing(input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True):
    """
    Checks if the font has a non-breaking space character, and if it doesn't, it adds one by double mapping 'space'
    """

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            cmap_table = font["cmap"]
            cmap_table_copy = deepcopy(cmap_table)

            for t in cmap_table.tables:
                if t.isUnicode():
                    if 0xA0 not in t.cmap.keys():
                        t.cmap[0xA0] = "space"

            if cmap_table_copy.compile(font) != cmap_table.compile(font):
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_common_options()
def decompose_transformed(
    input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True
):
    """
    Decomposes composite glyphs that have transformed components.

    fontbakery check id: com.google.fonts/check/transformed_components
    """

    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    import pathops

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            glyph_set = font.getGlyphSet()
            glyph_table = font["glyf"]
            glyph_table_copy = deepcopy(glyph_table)

            for glyph_name in glyph_set.keys():
                decompose = False
                glyf = glyph_table[glyph_name]
                if not glyf.isComposite():
                    continue
                for component in glyf.components:
                    _, transform = component.getComponentInfo()

                    # Font is hinted, decompose glyphs with *any* transformations
                    if font.is_hinted_ttf:
                        if transform[0:4] != (1, 0, 0, 1):
                            decompose = True
                    # Font is unhinted, decompose only glyphs with transformations where only one dimension is flipped
                    # while the other isn't. Otherwise the outline direction is intact and since the font is unhinted,
                    # no rendering problems are to be expected
                    else:
                        if transform[0] * transform[3] < 0:
                            decompose = True

                if decompose:
                    dc_pen = DecomposingRecordingPen(glyph_set)
                    glyph_set[glyph_name].draw(dc_pen)

                    path = pathops.Path()
                    path_pen = path.getPen()
                    dc_pen.replay(path_pen)

                    path.simplify()

                    ttPen = TTGlyphPen(None)
                    path.draw(ttPen)
                    glyph_table[glyph_name] = ttPen.glyph()

            if glyph_table_copy.compile(font) != glyph_table.compile(font):
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_common_options()
def duplicate_components(
    input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True
):
    """
    Removes duplicate components which have the same x,y coordinates.

    fontbakery check id: com.google.fonts/check/glyf_non_transformed_duplicate_components
    """

    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            glyph_table = font["glyf"]
            glyph_table_copy = deepcopy(glyph_table)

            for glyph_name in glyph_table.keys():
                glyf = glyph_table[glyph_name]
                if not glyf.isComposite():
                    continue

                seen = []

                for comp in glyf.components:
                    comp_info = {
                        "glyph": glyph_name,
                        "component": comp.glyphName,
                        "x": comp.x,
                        "y": comp.y,
                    }
                    if comp_info in seen:
                        glyf.components.remove(comp)
                    else:
                        seen.append(comp_info)

            if glyph_table_copy.compile(font) != glyph_table.compile(font):
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_common_options()
def kern_table(input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True):
    """
    Some applications such as MS PowerPoint require kerning info on the kern table. More specifically, they require a
    format 0 kern subtable from a kern table version 0 with only glyphs defined in the cmap table.

    Given this, the command deletes all kerning pairs from kern v0 subtables where one of the two glyphs is not defined
    in the cmap table.

    fontbakery check id: com.google.fonts/check/kern_table
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            if "kern" not in font:
                continue

            kern = font["kern"]

            if all(kernTable.format != 0 for kernTable in kern.kernTables):
                generic_warning_message(f"{os.path.basename(file)} The 'kern' table doesn't have any format-0 subtable")
                continue

            kern_table_copy = deepcopy(kern)

            character_glyphs = set()
            for table in font["cmap"].tables:
                character_glyphs.update(table.cmap.values())

            for table in kern.kernTables:
                if table.format == 0:
                    pairs_to_delete = []
                    for left_glyph, right_glyph in table.kernTable.keys():
                        if left_glyph not in character_glyphs or right_glyph not in character_glyphs:
                            pairs_to_delete.append((left_glyph, right_glyph))
                    if len(pairs_to_delete) > 0:
                        for pair in pairs_to_delete:
                            del table.kernTable[pair]

            if kern_table_copy.compile(font) != kern.compile(font):
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


@fix_fonts.command()
@add_file_or_path_argument()
@add_common_options()
def strip_names(input_path: Path, output_dir: Path = None, recalc_timestamp: bool = False, overwrite: bool = True):
    """
    Removes leading and trailing spaces from all namerecords.

    fontbakery check id: com.google.fonts/check/name/trailing_spaces
    """
    fonts = get_fonts_in_path(input_path=input_path, recalc_timestamp=recalc_timestamp)
    output_dir = get_output_dir(input_path=input_path, output_dir=output_dir)
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            name_table: TableName = font["name"]
            name_table_copy = deepcopy(name_table)

            name_table.remove_leading_trailing_spaces()

            if name_table_copy.compile(font) != name_table.compile(font):
                font.save(output_file)
                file_saved_message(output_file)

            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[fix_fonts],
    help="""
    A set of commands to detect and automatically fix font errors.
    """,
)

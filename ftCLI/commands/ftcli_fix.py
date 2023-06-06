import os
from copy import deepcopy

import click
from afdko.fdkutils import run_shell_command
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import check_output_dir, check_input_path
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    generic_error_message,
    file_saved_message,
    file_not_changed_message,
    generic_warning_message,
    generic_success_message,
    generic_info_message,
)


@click.group()
def fix_monospaced_fonts():
    pass


@fix_monospaced_fonts.command()
@add_file_or_path_argument()
@add_common_options()
def monospace(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    If the family is monospaced:

    \b
    * post.isFixedPitch must be set to a non-zero value
    * OS/2.panose.bProportion must be set to 9
    * CFF.cff.TopDictIndex[0].isFixedPitch must be set to True

    fontbakery check id: com.google.fonts/check/monospace
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            post_table_copy = deepcopy(font.post_table)
            os2_table_copy = deepcopy(font.os_2_table)

            font.post_table.set_fixed_pitch(True)

            if font.os_2_table.panose.bProportion != 9:
                font.os_2_table.panose.bProportion = 9
                # Ensure that panose.bFamilyType is non-zero when panose.bProportion is 9
                if font.os_2_table.panose.bFamilyType == 0:
                    font.os_2_table.panose.bFamilyType = 2

            post_table_changed = False
            if post_table_copy.compile(font) != font.post_table.compile(font):
                post_table_changed = True

            os2_table_changed = False
            if os2_table_copy.compile(font) != font.os_2_table.compile(font):
                os2_table_changed = True

            cff_table_changed = False
            if font.is_cff:
                cff_table = font["CFF "]
                cff_table_copy = deepcopy(cff_table)
                top_dict = cff_table.cff.topDictIndex[0]
                setattr(top_dict, "isFixedPitch", True)

                if cff_table_copy.compile(font) != cff_table.compile(font):
                    cff_table_changed = True

            if post_table_changed or os2_table_changed or cff_table_changed:
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(file)

            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def fix_os2_table_unicode_codepage():
    pass


@fix_os2_table_unicode_codepage.command()
@add_file_or_path_argument()
@add_common_options()
def os2_ranges(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Generates a temporary Type 1 from the font file using tx, converts that to an OpenType font using makeotf, reads the
    Unicode ranges and codepage ranges from the temporary OpenType font file, and then writes those ranges to the
    original font's OS/2 table.
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)

            os_2_table_copy = deepcopy(font.os_2_table)

            temp_t1_file = makeOutputFileName(output_file, outputDir=output_dir, extension=".t1", overWrite=True)
            command = ["tx", "-t1", file, temp_t1_file]
            run_shell_command(command, suppress_output=True)

            temp_otf_file = makeOutputFileName(output_file, outputDir=output_dir, suffix="_tmp", overWrite=True)
            command = ["makeotf", "-f", temp_t1_file, "-o", temp_otf_file]
            run_shell_command(command, suppress_output=True)

            temp_font = Font(temp_otf_file)
            unicode_ranges = temp_font.os_2_table.getUnicodeRanges()
            ul_codepage_range_1 = temp_font.os_2_table.ulCodePageRange1
            ul_codepage_range_2 = temp_font.os_2_table.ulCodePageRange2

            temp_font.close()
            os.remove(temp_t1_file)
            os.remove(temp_otf_file)

            font.os_2_table.setUnicodeRanges(unicode_ranges)
            font.os_2_table.ulCodePageRange1 = ul_codepage_range_1
            font.os_2_table.ulCodePageRange2 = ul_codepage_range_2

            if os_2_table_copy.compile(font) != font.os_2_table.compile(font):
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def fix_non_breaking_space_width():
    pass


@fix_non_breaking_space_width.command()
@add_file_or_path_argument()
@add_common_options()
def nbsp_width(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Checks if 'nbspace' and 'space' glyphs have the same width. If not, corrects 'nbspace' width to match 'space' width.

    fontbakery check id: com.google.fonts/check/whitespace_widths
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            hmtx_table = font["hmtx"]
            hmtx_table_copy = deepcopy(hmtx_table)

            best_cmap = font.getBestCmap()
            space_name = best_cmap[0x0020]
            nbspace_name = best_cmap[0x00A0]

            font["hmtx"][nbspace_name] = font["hmtx"][space_name]

            if hmtx_table_copy.compile(font) != hmtx_table.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def fix_caret_offset():
    pass


@fix_caret_offset.command()
@add_file_or_path_argument()
@add_common_options()
def caret_offset(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Recalculates hhea.caretOffset value.
    """

    files = check_input_path(input_path, allow_variable=False, allow_extensions=[".ttf", ".otf"])
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        print()
        generic_info_message(f"Checking file: {os.path.basename(file)}")
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)

            offset = font.hhea_table.caretOffset

            temp_t1_file = makeOutputFileName(file, extension=".t1", suffix="_tmp", overWrite=True)
            temp_otf_file = makeOutputFileName(file, extension=".otf", suffix="_tmp", overWrite=True)
            run_shell_command(["tx", "-t1", file, temp_t1_file], suppress_output=True)
            run_shell_command(
                ["makeotf", "-f", temp_t1_file, "-o", temp_otf_file],
                suppress_output=True,
            )

            temp_font = Font(temp_otf_file)
            calculated_offset = temp_font.hhea_table.caretOffset

            temp_font.close()
            os.remove(temp_t1_file)
            os.remove(temp_otf_file)

            offset_ok = offset == calculated_offset

            if offset_ok:
                generic_success_message(f"hhea.caretOffset: {click.style(offset, fg='green', bold=True)}")
                file_not_changed_message(os.path.basename(file))
            else:
                font.hhea_table.caretOffset = calculated_offset
                generic_warning_message(
                    f"hhea.caretOffset: {click.style(offset, fg='red', bold=True)} -> "
                    f"{click.style(calculated_offset, fg='green', bold=True)}"
                )
                font.save(output_file)
                file_saved_message(os.path.basename(file))

        except Exception as e:
            generic_error_message(e)


@click.group()
def fix_italic_metadata():
    pass


@fix_italic_metadata.command()
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
def italic_angle(input_path, mode, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Recalculates post.italicAngle, hhea.caretSlopeRise, hhea.caretSlopeRun and sets/clears the italic/oblique bits
    according to the calculated values. In CFF fonts, also CFF.topDictIndex[0].ItalicAngle is recalculated.
    """
    files = check_input_path(input_path, allow_variable=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        print()
        generic_info_message(f"Checking file: {os.path.basename(file)}")
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)

            # Check post.italicAngle
            post_italic_angle = font.post_table.italicAngle
            calculated_post_italic_angle = font.calculate_italic_angle()
            post_italic_angle_ok = font.check_italic_angle()
            if post_italic_angle_ok:
                generic_success_message(
                    f"post.italicAngle    : {click.style(post_italic_angle, fg='green', bold=True)}"
                )
            else:
                font.post_table.set_italic_angle(calculated_post_italic_angle)
                generic_warning_message(
                    f"post.italicAngle    : "
                    f"{click.style(post_italic_angle, fg='red', bold=True)} -> "
                    f"{click.style(calculated_post_italic_angle, fg='green', bold=True)}"
                )

            calculated_rise = font.calculate_caret_slope_rise()
            calculated_run = font.calculate_caret_slope_run()

            # Check hhea italic angle
            rise = font.hhea_table.caretSlopeRise
            run = font.hhea_table.caretSlopeRun
            hhea_italic_angle = font.calculate_run_rise_angle()
            hhea_italic_angle_ok = abs(font.post_table.italicAngle - hhea_italic_angle) < 0.1
            if hhea_italic_angle_ok:
                generic_success_message(f"hhea.caretSlopeRise : {click.style(rise, fg='green', bold=True)}")
                generic_success_message(f"hhea.caretSlopeRun  : {(click.style(run, fg='green', bold=True))}")
            else:
                font.hhea_table.caretSlopeRise = calculated_rise
                generic_warning_message(
                    f"hhea.caretSlopeRise : {click.style(rise, fg='red', bold=True)} -> "
                    f"{click.style(calculated_rise, fg='green', bold=True)}"
                )
                font.hhea_table.caretSlopeRun = calculated_run
                generic_warning_message(
                    f"hhea.caretSlopeRun  : {click.style(run, fg='red', bold=True)} -> "
                    f"{click.style(calculated_run, fg='green', bold=True)}"
                )

            # Check CFF italic angle
            if font.is_cff:
                cff_table = font["CFF "]
                cff_italic_angle = cff_table.cff.topDictIndex[0].ItalicAngle
                cff_italic_angle_ok = cff_italic_angle == round(font.post_table.italicAngle)

                if cff_italic_angle_ok:
                    generic_success_message(
                        f"CFF.ItalicAngle     : " f"{click.style(cff_italic_angle, fg='green', bold=True)}"
                    )
                else:
                    cff_table.cff.topDictIndex[0].ItalicAngle = round(font.post_table.italicAngle)
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


@click.group()
def fix_missing_nbspace():
    pass


@fix_missing_nbspace.command()
@add_file_or_path_argument()
@add_common_options()
def nbsp_missing(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Checks if the font has a non-breaking space character, and if it doesn't, it adds one by double mapping 'space'
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)

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


@click.group()
def decompose_transformed_components():
    pass


@decompose_transformed_components.command()
@add_file_or_path_argument()
@add_common_options()
def decompose_transformed(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Decomposes composite glyphs that have transformed components.

    fontbakery check id: com.google.fonts/check/transformed_components
    """

    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    import pathops

    files = check_input_path(input_path, allow_cff=False, allow_variable=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)

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


@click.group()
def remove_glyf_duplicate_components():
    pass


@remove_glyf_duplicate_components.command()
@add_file_or_path_argument()
@add_common_options()
def duplicate_components(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Removes duplicate components which have the same x,y coordinates.

    fontbakery check id: com.google.fonts/check/glyf_non_transformed_duplicate_components
    """

    files = check_input_path(input_path, allow_cff=False, allow_variable=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

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
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def fix_unmapped_glyphs_kern_table():
    pass


@fix_unmapped_glyphs_kern_table.command()
@add_file_or_path_argument()
@add_common_options()
def kern_table(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Some applications such as MS PowerPoint require kerning info on the kern table. More specifically, they require a
    format 0 kern subtable from a kern table version 0 with only glyphs defined in the cmap table.

    Given this, the command deletes all kerning pairs from kern v0 subtables where one of the two glyphs is not defined
    in the cmap table.

    fontbakery check id: com.google.fonts/check/kern_table
    """
    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
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
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def remove_leading_and_trailing_spaces():
    pass


@remove_leading_and_trailing_spaces.command()
@add_file_or_path_argument()
@add_common_options()
def strip_names(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Removes leading and trailing spaces from all namerecords.

    fontbakery check id: com.google.fonts/check/name/trailing_spaces
    """
    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)

            name_table_copy = deepcopy(font.name_table)

            font.name_table.remove_leading_trailing_spaces()

            if name_table_copy.compile(font) != font.name_table.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)

            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def fix_uprights_values():
    pass


@fix_uprights_values.command()
@add_file_or_path_argument()
@add_common_options()
def uprights(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Assuming that the font is correctly set as upright (i.e.: italic oblique bits are all clear), the script sets the
    following values:

    \b
    post.italicAngle = 0.0
    hhea.caretSlopeRise = 1
    hhea.caretSlopeRun = 0
    hhea.caretOffset = 0
    CFF.cff.topDictIndex[0].ItalicAngle = 0 (only if the font has a CFF table)

    The font is saved only if at least one table has changed.
    """

    files = check_input_path(input_path)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            post_table_copy = deepcopy(font.post_table)
            hhea_table = font.hhea_table
            hhea_table_copy = deepcopy(hhea_table)

            font_has_changed = False

            if not font.is_italic:
                font.post_table.set_italic_angle(0)
                if font.is_cff:
                    cff_table = font["CFF "]
                    cff_table_copy = deepcopy(font["CFF "])
                    font["CFF "].cff.topDictIndex[0].ItalicAngle = 0
                else:
                    cff_table = None
                    cff_table_copy = None

                hhea_table.caretSlopeRise = 1
                hhea_table.caretSlopeRun = 0
                hhea_table.caretOffset = 0

                if cff_table and cff_table_copy:
                    if cff_table_copy.compile(font) != cff_table.compile(font):
                        font_has_changed = True
                if post_table_copy.compile(font) != font.post_table.compile(font):
                    font_has_changed = True
                if hhea_table_copy.compile(font) != hhea_table.compile(font):
                    font_has_changed = True

            if font_has_changed:
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


cli = click.CommandCollection(
    sources=[
        fix_os2_table_unicode_codepage,
        fix_non_breaking_space_width,
        fix_italic_metadata,
        fix_caret_offset,
        fix_missing_nbspace,
        fix_monospaced_fonts,
        decompose_transformed_components,
        remove_glyf_duplicate_components,
        fix_unmapped_glyphs_kern_table,
        remove_leading_and_trailing_spaces,
        fix_uprights_values,
    ],
    help="""
    A set of commands to detect and automatically fix font errors.
    """,
)

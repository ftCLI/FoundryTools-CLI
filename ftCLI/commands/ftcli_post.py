from copy import copy

import click
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import get_fonts_list, get_output_dir, check_output_dir
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    file_saved_message,
    file_not_changed_message,
    generic_error_message, no_valid_fonts_message,
)


@click.command()
@add_file_or_path_argument()
@click.option(
    "--italic-angle",
    type=click.FloatRange(-90.0, 90.0),
    help="""
              Sets the `italicAngle` value.
              """,
)
@click.option(
    "--ul-position",
    type=int,
    help="""
              Sets the `underlinePosition` value.
              """,
)
@click.option(
    "--ul-thickness",
    type=int,
    help="""
              Sets the `underlineThickness` value.
              """,
)
@click.option(
    "--fixed-pitch/--no-fixed-pitch",
    default=None,
    help="""
              Sets or clears the `isFixedPitch` value.
              """,
)
@add_common_options()
def cli(input_path, recalcTimestamp, outputDir, overWrite, **kwargs):
    """Command line post table editor."""

    params = {k: v for k, v in kwargs.items() if v is not None}

    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    files = get_fonts_list(input_path)
    if len(files) == 0:
        no_valid_fonts_message(input_path)
        return

    output_dir = get_output_dir(input_path=input_path, output_dir=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)

            # Using copy instead of deepcopy and avoiding to compile `post` tables is faster

            # Make a copy of the `post` table to check later if it has been modified
            post_table_copy = copy(font.post_table)
            if font.is_cff:
                cff_table_copy = copy(font["CFF "])
            else:
                cff_table_copy = None

            # Process the arguments
            if "italic_angle" in params.keys():
                font.post_table.set_italic_angle(params.get("italic_angle"))
                if font.is_cff:
                    font["CFF "].cff.topDictIndex[0].ItalicAngle = int(params.get("italic_angle"))

            if "ul_position" in params.keys():
                font.post_table.set_underline_position(params.get("ul_position"))

            if "ul_thickness" in params.keys():
                font.post_table.set_underline_thickness(params.get("ul_thickness"))

            if "fixed_pitch" in params.keys():
                font.post_table.set_fixed_pitch(params.get("fixed_pitch"))

            font.save(output_file)

            # Check if tables have changed before saving the font. No need to compile here.
            if not font.is_cff:
                if (font.post_table.compile(font)) != post_table_copy.compile(font):
                    font.save(output_file)
                    file_saved_message(output_file)
                else:
                    file_not_changed_message(file)

            else:
                if cff_table_copy:
                    if (font.post_table.compile(font), font["CFF "].compile(font)) != (
                        post_table_copy.compile(font),
                        cff_table_copy.compile(font),
                    ):
                        font.save(output_file)
                        file_saved_message(output_file)
                else:
                    file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)

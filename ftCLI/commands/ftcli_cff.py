from copy import deepcopy

import click
from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.cli_tools import check_input_path, check_output_dir
from ftCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    generic_error_message,
    file_saved_message,
    file_not_changed_message,
)


@click.group()
def del_cff_names():
    pass


@del_cff_names.command()
@add_file_or_path_argument()
@click.option("--full-name", "FullName", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] FullName")
@click.option("--family-name", "FamilyName", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] FamilyName")
@click.option("--weight", "Weight", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Weight")
@click.option("--version", "version", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] version")
@click.option("--copyright", "Copyright", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Copyright")
@click.option("--notice", "Notice", is_flag=True, help="Deletes CFF.cff.topDictIndex[0] Copyright")
@add_common_options()
def del_names(input_path, recalcTimestamp=False, outputDir=None, overWrite=True, **kwargs):
    """
    Deletes CFF names.
    """

    params = {k: v for k, v in kwargs.items() if v}
    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    files = check_input_path(input_path, allow_ttf=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            cff_table = font["CFF "]
            cff_table_copy = deepcopy(cff_table)
            top_dict = cff_table.cff.topDictIndex[0]

            for k in params.keys():
                try:
                    del top_dict.rawDict[k]
                except KeyError:
                    pass

            if cff_table.compile(font) != cff_table_copy.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def set_cff_names():
    pass


@set_cff_names.command()
@add_file_or_path_argument()
@click.option("--font-names", "fontNames", type=str, help="Sets CFF.cff.fontNames value")
@click.option(
    "--full-name",
    "FullName",
    type=str,
    help="Sets CFF.cff.topDictIndex[0] FullName value",
)
@click.option(
    "--family-name",
    "FamilyName",
    type=str,
    help="Sets CFF.cff.topDictIndex[0] FamilyName value",
)
@click.option("--weight", "Weight", type=str, help="Sets CFF.cff.topDictIndex[0] Weight value")
@click.option("--version", "version", type=str, help="Sets CFF.cff.topDictIndex[0] version value")
@add_common_options()
def set_names(input_path, recalcTimestamp=False, outputDir=None, overWrite=True, **kwargs):
    """
    Sets CFF names.
    """

    params = {k: v for k, v in kwargs.items() if v is not None}
    if len(params) == 0:
        generic_error_message("Please, pass at least a valid parameter.")
        return

    files = check_input_path(input_path, allow_ttf=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            cff_table = font["CFF "]
            cff_table_copy = deepcopy(cff_table)
            top_dict = cff_table.cff.topDictIndex[0]

            if "fontNames" in params.keys():
                cff_table.cff.fontNames = [params.get("fontNames")]
                del params["fontNames"]

            for attr_name, attr_value in params.items():
                setattr(top_dict, attr_name, attr_value)

            if cff_table.compile(font) != cff_table_copy.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def cff_find_and_replace():
    pass


@cff_find_and_replace.command()
@add_file_or_path_argument()
@click.option("-os", "--old-string", required=True, help="The string to be replaced")
@click.option(
    "-ns",
    "--new-string",
    required=True,
    help="The string to replace the old string with",
    show_default=True,
)
@add_common_options()
def find_replace(
    input_path,
    old_string,
    new_string,
    outputDir=None,
    recalcTimestamp=False,
    overWrite=True,
):
    """
    Finds a string in the following items of CFF table topDict and replaces it with a new string: `version`, `FullName`,
    `FamilyName`, `Weight`, `Copyright`, `Notice`.
    """

    files = check_input_path(input_path, allow_ttf=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            cff_table = font["CFF "]
            cff_table_copy = deepcopy(cff_table)
            cff_font_name = cff_table.cff.fontNames[0]
            cff_table.cff.fontNames = [cff_font_name.replace(old_string, new_string).replace("  ", " ").strip()]

            top_dict = cff_table.cff.topDictIndex[0]
            attr_list = [
                "version",
                "FullName",
                "FamilyName",
                "Weight",
                "Copyright",
                "Notice",
            ]

            for attr_name in attr_list:
                try:
                    old_value = str(getattr(top_dict, attr_name))
                    new_value = old_value.replace(old_string, new_string).replace("  ", " ").strip()
                    setattr(top_dict, attr_name, new_value)
                except AttributeError:
                    pass

            if cff_table.compile(font) != cff_table_copy.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)

        except Exception as e:
            generic_error_message(e)


@click.group()
def fix_cff_version_string():
    pass


@fix_cff_version_string.command()
@add_file_or_path_argument()
@add_common_options()
def fix_version(input_path, recalcTimestamp=False, outputDir=None, overWrite=True):
    """
    Aligns topDict version string to the head.fontRevision value.

    For example, if head.fontRevision value is 2.001, CFF topDict version value will be 2.1.
    """

    files = check_input_path(input_path, allow_ttf=False)
    output_dir = check_output_dir(input_path=input_path, output_path=outputDir)

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            cff_table = font["CFF "]
            cff_table_copy = deepcopy(cff_table)
            font.fix_cff_top_dict_version()

            if cff_table_copy.compile(font) != cff_table.compile(font):
                output_file = makeOutputFileName(file, outputDir=output_dir, overWrite=overWrite)
                font.save(output_file)
                file_saved_message(output_file)
            else:
                file_not_changed_message(file)
        except Exception as e:
            generic_error_message(e)


cli = click.CommandCollection(
    sources=[
        fix_cff_version_string,
        set_cff_names,
        del_cff_names,
        cff_find_and_replace,
    ],
    help="""
Command line CFF table editor.
""",
)

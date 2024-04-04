import os
import tempfile
import typing as t
from copy import deepcopy
from pathlib import Path

import click
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTFont
from pathvalidate import sanitize_filename, sanitize_filepath

from foundryToolsCLI.Lib.tables.CFF_ import TableCFF
from foundryToolsCLI.Lib.tables.OS_2 import TableOS2
from foundryToolsCLI.Lib.tables.head import TableHead
from foundryToolsCLI.Lib.tables.name import TableName
from foundryToolsCLI.Lib.utils.cli_tools import get_fonts_in_path, initial_check_pass
from foundryToolsCLI.Lib.utils.click_tools import (
    add_file_or_path_argument,
    add_recursive_option,
    add_common_options,
    choice_to_int_callback,
)
from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.utils.timer import Timer

utils = click.Group("subcommands")


@utils.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def add_dsig(
    input_path: Path,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Adds a dummy DSIG table to the fonts, unless the table is already present, or the font flavor is woff2.
    """

    fonts = get_fonts_in_path(
        input_path=input_path,
        recursive=recursive,
        recalc_timestamp=recalc_timestamp,
        allow_extensions=[".ttf", ".otf", ".woff"],
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            if "DSIG" not in font:
                font.add_dummy_dsig()
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.warning("DSIG table already present in the font. Skipping.")
                logger.skip(Logs.file_not_changed, file=file)
        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@utils.command()
@add_file_or_path_argument()
@click.option(
    "-t",
    "table_tags",
    multiple=True,
    required=True,
    help="""TableTag of the table(s) to delete. Can be repeated to delete multiple tables at once.""",
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def del_table(
    input_path: Path,
    table_tags: t.Tuple,
    recursive: bool = False,
    recalc_timestamp: bool = False,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
):
    """
    Deletes the specified tables from the fonts.
    """

    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    table_tags = tuple(set(tag.ljust(4, " ") for tag in table_tags))

    for font in fonts:
        removed_tables_counter = 0
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            for tag in table_tags:
                if tag in font.keys():
                    del font[tag]
                    removed_tables_counter += 1
                else:
                    logger.warning(f"'{tag}' table is not present in {file.name}")

            if removed_tables_counter > 0:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@utils.command()
@click.option(
    "-f",
    "--foundry",
    "sort_by_foundry",
    is_flag=True,
    help="""
    Organize fonts by foundry.

    Foundry directory will be created at top level, with Family Name directory as child.

    Foundry name is obtained trying to read nameID 8 (Manufacturer Name), using as fallback nameID 9 (Designer).
    If nor nameID 8 nor nameID 9 are present in the 'name' table, the string is retrieved from achVendID in the 'OS/2'
    table.
    """,
)
@click.option(
    "-e",
    "--extension",
    "sort_by_extension",
    is_flag=True,
    help="Moves fonts into a folder named after their real extension.",
)
@click.option(
    "-v",
    "--version",
    "sort_by_version",
    is_flag=True,
    help="Appends the version string to the family folder.",
)
@add_file_or_path_argument()
@Timer(logger=logger.info)
def font_organizer(
    input_path: Path,
    sort_by_foundry: bool = False,
    sort_by_extension: bool = False,
    sort_by_version: bool = False,
):
    """
    Sorts fonts in folders by family name and optionally by foundry, font revision and extension.
    """
    fonts = get_fonts_in_path(input_path=input_path)
    if not initial_check_pass(fonts=fonts):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_dir = file.parent
            family_name = font.guess_family_name()

            foundry = font.guess_foundry_name() if sort_by_foundry else None
            if foundry:
                output_dir = output_dir.joinpath(foundry)

            version = f" v{round(font['head'].fontRevision, 3)}" if sort_by_version else None
            if version:
                family_name = family_name + version
            output_dir = output_dir.joinpath(family_name)

            extension = font.get_real_extension() if sort_by_extension else None
            if extension:
                extension = extension.replace(".", "")
                output_dir = output_dir.joinpath(extension)

            output_dir = sanitize_filepath(output_dir, platform="auto")
            output_dir.mkdir(parents=True, exist_ok=True)

            target = Path(makeOutputFileName(output_dir.joinpath(file.name), overWrite=False))
            file.rename(target=target)

            logger.opt(colors=True).success(f"{file} <magenta>--></> <cyan>{target}</>")

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@utils.command()
@add_file_or_path_argument()
@click.option(
    "-s",
    "--source",
    type=click.Choice(choices=["1", "2", "3", "4", "5"]),
    default="1",
    callback=choice_to_int_callback,
    help="""
              The source string(s) from which to extract the new file name. Default is 1 (FamilyName-StyleName), used
              also as fallback name when 4 or 5 are passed but the font is TrueType

              \b
              1: FamilyName-StyleName
              2: PostScript Name
              3: Full Font Name
              4: CFF TopDict fontNames (CFF fonts only)
              5: CFF TopDict FullName (CFF fonts only)
              """,
)
@add_recursive_option()
@Timer(logger=logger.info)
def font_renamer(input_path: Path, source: str, recursive: bool = False):
    """
    Rename font files according to the provided source string.
    """

    fonts = get_fonts_in_path(input_path=input_path, recursive=recursive)
    if not initial_check_pass(fonts=fonts):
        return

    for font in fonts:
        file = Path(font.reader.file.name)

        if font.is_ttf and source in (4, 5):
            logger.warning(
                f"Source 4 and 5 con be used for OTF files only. Using source=1 for {file.name}"
            )

        old_file_name, old_file_extension = file.stem, file.suffix
        new_file_name = sanitize_filename(font.get_file_name(source=source), platform="auto")
        new_file_extension = font.get_real_extension()

        if f"{new_file_name}{new_file_extension}" != f"{old_file_name}{old_file_extension}":
            try:
                output_file = Path(
                    makeOutputFileName(
                        new_file_name,
                        extension=new_file_extension,
                        outputDir=file.parent,
                        overWrite=False,
                    )
                )
                file.rename(output_file)
                logger.opt(colors=True).success(
                    f"{file.name} <magenta>--></> <cyan>{output_file.name}</>"
                )
            except Exception as e:
                logger.exception(e)
        else:
            logger.skip(Logs.file_not_changed, file=file.name)

        font.close()


@utils.command()
@add_file_or_path_argument()
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def rebuild(
    input_path: Path,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Rebuilds fonts by converting to XML and then converting back to the original format
    """
    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )
    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))
            logger.opt(colors=True).info(Logs.current_file, file=file)

            flavor = font.flavor

            fd, xml_file = tempfile.mkstemp()
            os.close(fd)
            font.saveXML(xml_file)

            rebuilt_font = TTFont(recalcTimestamp=recalc_timestamp)
            rebuilt_font.importXML(xml_file)
            rebuilt_font.flavor = flavor
            rebuilt_font.save(output_file)

            logger.success(Logs.file_saved, file=output_file)

            if os.path.exists(xml_file):
                os.remove(xml_file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


@utils.command()
@add_file_or_path_argument()
@click.option("-major", type=click.IntRange(0, 999), help="Major version")
@click.option("-minor", type=click.IntRange(0, 999), help="Minor version")
@click.option(
    "-ui", "--unique-identifier", is_flag=True, help="Recalculates nameID 3 (Unique identifier)"
)
@click.option(
    "-vs", "--version-string", is_flag=True, help="Recalculates nameID 5 (version string)"
)
@click.option(
    "-p",
    "--platform-id",
    type=click.Choice(choices=["1", "3"]),
    callback=choice_to_int_callback,
    help="""
    platformID of the NameRecord to add (1: Macintosh, 3: Windows).

    When recalculating Unique identifier and/or Version string, update only the NameRecords matching
    the specified platformID.
    """,
)
@add_recursive_option()
@add_common_options()
@Timer(logger=logger.info)
def set_revision(
    input_path: Path,
    major: t.Optional[int] = None,
    minor: t.Optional[int] = None,
    unique_identifier: bool = False,
    version_string: bool = False,
    platform_id: int = None,
    recursive: bool = False,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
):
    """
    Sets [head].fontRevision and CFF.cff.topDictIndex[0].version values.

    Optionally, also nameID 3 (Unique identifier) and nameID 5 (Version string) can be recalculated by using
    `--unique-identifier` and `--version-string options`. Even if Unique identifier and Version string should be changed
    according to the new version, they are optional to leave control to the user, who could choose to set those names
    manually with ftcli name set-name or ftcli name find-replace commands.
    """

    if major is None and minor is None:
        logger.error("At least one parameter of -minor or -major must be passed")
        return

    fonts = get_fonts_in_path(
        input_path=input_path, recursive=recursive, recalc_timestamp=recalc_timestamp
    )

    if not initial_check_pass(fonts=fonts, output_dir=output_dir):
        return

    for font in fonts:
        try:
            file = Path(font.reader.file.name)
            output_file = Path(makeOutputFileName(file, outputDir=output_dir, overWrite=overwrite))

            head_table: TableHead = font["head"]

            has_changed = False

            old_font_revision = str(head_table.get_font_revision()).rjust(3, "0")
            old_major_version = str(old_font_revision).split(".")[0]
            old_minor_version = str(old_font_revision).split(".")[1]

            new_major_version = str(major) if major is not None else old_major_version
            new_minor_version = str(minor).rjust(3, "0") if minor is not None else old_minor_version
            new_font_revision = f"{new_major_version}.{new_minor_version}"

            if old_font_revision != new_font_revision:
                head_table.set_font_revision(float(new_font_revision))
                has_changed = True

            if font.is_otf:
                cff: TableCFF = font["CFF "]
                old_cff_version = cff.get_font_version()
                new_cff_version = f"{int(new_major_version)}.{int(new_minor_version)}"
                if old_cff_version != new_cff_version:
                    cff.set_font_version(new_cff_version)
                    has_changed = True

            if unique_identifier or version_string:
                name_table: TableName = font["name"]
                name_table_copy = deepcopy(name_table)

                if unique_identifier:
                    os2: TableOS2 = font["OS/2"]
                    vend_id = os2.get_vend_id()
                    ps_name = name_table.getDebugName(6)
                    name_table.add_name(
                        font,
                        string=f"{new_font_revision};{vend_id};{ps_name}",
                        name_id=3,
                        platform_id=platform_id,
                    )

                if version_string:
                    name_table.add_name(
                        font,
                        string=f"Version {new_font_revision}",
                        name_id=5,
                        platform_id=platform_id,
                    )

                if name_table_copy.compile(font) != name_table.compile(font):
                    has_changed = True

            if has_changed:
                font.save(output_file)
                logger.success(Logs.file_saved, file=output_file)
            else:
                logger.skip(Logs.file_not_changed, file=file)

        except Exception as e:
            logger.exception(e)
        finally:
            font.close()


cli = click.CommandCollection(
    sources=[utils],
    help="""
    Miscellaneous utilities.
    """,
)

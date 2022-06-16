import os

import click

from ftcli.Lib.Font import Font
from ftcli.Lib.utils import getFontsList, makeOutputFileName, add_file_or_path_argument, add_common_options


@click.group()
def addPrefix():
    pass


@addPrefix.command()
@add_file_or_path_argument()
@click.option('--prefix', required=True, type=str, help="The prefix string.")
@click.option('-n', '--name-id', 'nameIDs', required=True, multiple=True, type=click.IntRange(0, 32767),
              help="nameID where to add the prefix. This option can be repeated multiple times (for example: -n 3 -n 5"
                   "-n 6).")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If no platform is specified, the prefix will be added in both tables.")
@add_common_options()
def add_prefix(input_path, prefix, nameIDs, platform, outputDir, recalcTimestamp, overWrite):
    """Adds a prefix to the specified namerecords.
    """
    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            font.addPrefix(prefix=prefix, name_ids=nameIDs, platform=platform)
            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


@click.group()
def addSuffix():
    pass


@addSuffix.command()
@add_file_or_path_argument()
@click.option('--suffix', required=True, type=str, help="The suffix string")
@click.option('-n', '--name-id', 'nameIDs', required=True, multiple=True, type=click.IntRange(0, 32767),
              help="nameID where to add the suffix. This option can be repeated multiple times (for example: -n 3 -n 5 "
                   "-n 6).")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If no platform is specified, the suffix will be added in both tables.")
@add_common_options()
def add_suffix(input_path, suffix, nameIDs, platform, outputDir, recalcTimestamp, overWrite):
    """Adds a suffix to the specified namerecords.
    """
    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            font.addSuffix(suffix=suffix, name_ids=nameIDs, platform=platform)
            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')

        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


@click.group()
def cleanNameTable():
    pass


@cleanNameTable.command()
@add_file_or_path_argument()
@click.option('-ex', '--exclude-namerecord', type=int, multiple=True,
              help="NameIDs to skip. The specified nameIDs won't be deleted. This option can be repeated multiple "
                   "times (for example: -ex 3 -ex 5 -ex 6).")
@add_common_options()
def clean_name_table(input_path, exclude_namerecord, outputDir, recalcTimestamp, overWrite):
    """Deletes all namerecords from the `name` table.

    Use `-ex / --exclude-namerecord` (can be repeated multiple times) to preserve the specified namerecords.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            for name in font['name'].names:
                if name.nameID in exclude_namerecord:
                    continue
                font.delNameRecord(nameID=name.nameID, language='ALL')
            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


# copy-names
@click.group()
def copyNames():
    pass


@copyNames.command()
@click.option('-s', '--source_font', required=True, type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              help="Path to the source font.")
@click.option('-d', '--dest_font', required=True, type=click.Path(exists=True, resolve_path=True, dir_okay=False),
              help="Path to the destination font.")
@add_common_options()
def copy_names(source_font, dest_font, outputDir, recalcTimestamp, overWrite):
    """Copies the `name` table from a source font to destination font.

    Usage:

        ftcli names copy_names -s SourceFont.otf -d DestFont.otf
    """

    try:
        s = Font(source_font)
        d = Font(dest_font, recalcTimestamp=recalcTimestamp)
        d['name'] = s['name']
        output_file = makeOutputFileName(dest_font, outputDir=outputDir, overWrite=overWrite)
        d.save(output_file)
        click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
    except Exception as e:
        click.secho(f'ERROR: {e}', fg='red')


# del-mac-names
@click.group()
def delMacNames():
    pass


@delMacNames.command()
@add_file_or_path_argument()
@click.option('-ex', '--exclude-namerecord', type=click.IntRange(0, 32767), multiple=True,
              help="NameIDs to ignore. The specified nameIDs won't be deleted. This option can be repeated multiple "
                   "times (for example: -ex 3 -ex 5 -ex 6).")
@add_common_options()
def del_mac_names(input_path, exclude_namerecord, outputDir, recalcTimestamp, overWrite):
    """Deletes all namerecords where platformID is equal to 1.

    According to Apple (https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html), "names with
    platformID 1 were required by earlier versions of macOS. Its use on modern platforms is discouraged. Use names with
    platformID 3 instead for maximum compatibility. Some legacy software, however, may still require names with
    platformID 1, platformSpecificID 0".

    Use the `-ex / --exclude-namerecord` option to prevent certain namerecords to be deleted:

        ftcli names del-mac-names INPUT_PATH -ex 1

    The option can be repeated to exclude multiple namerecords from deletion:

        ftcli names del-mac-names INPUT_PATH -ex 1 -ex 3 -ex 6

    `INPUT_PATH` can be a single font file or a folder containing fonts.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            font.delMacNames(exclude_namerecord=exclude_namerecord)
            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


# del-names
@click.group()
def delNames():
    pass


@delNames.command()
@add_file_or_path_argument()
@click.option('-n', '--name-id', 'nameIDs', type=int, required=True, multiple=True,
              help="nameID (Integer)")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If no platform is specified, the namerecord will be deleted from both tables.")
@click.option('-l', '--language', default="en", show_default=True,
              help="Specify the name ID language (eg: 'de'), or use 'ALL' to delete the name ID from all languages.")
@add_common_options()
def del_names(input_path, nameIDs, platform, language, outputDir, recalcTimestamp, overWrite):
    """Deletes the specified namerecord(s) from the name table.

    Use the `-l/--language` option to delete a namerecord in a language different from 'en'. Use `ftcli names lang-help`
    to display available languages.

    Use `-l ALL` to delete the name ID from all languages.

    The `-n/--name-id` option can be repeated to delete multiple name records at once. For example:

        ftcli names del-names C:\\Fonts -n 1 -n 2 -n 6

    The above command will delete nameIDs 1, 2 and 6.
    """
    windows = False if platform == "mac" else True
    mac = False if platform == "win" else True

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            for n in nameIDs:
                font.delNameRecord(n, language=language, windows=windows, mac=mac)
            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


# find-replace
@click.group()
def findReplace():
    pass


@findReplace.command()
@add_file_or_path_argument()
@click.option("-os", "--old-string", required=True,
              help="old string")
@click.option('-ns', '--new-string', required=True,
              help="new string", show_default=True)
@click.option('-n', '--name-id', type=click.IntRange(0, 32767),
              help="nameID (Integer between 0 and 32767). If not specified, the string will be replaced in all"
                   "namerecords.")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If no platform is specified, the string will be replaced in both tables.")
@click.option('-cff', '--fix-cff', is_flag=True,
              help="Replaces the string in the CFF table.")
@click.option('-ex', '--exclude-namerecord', type=click.IntRange(0, 32767), multiple=True,
              help="NameIDs to ignore. The specified nameIDs won't be changed. This option can be repeated multiple "
                   "times (for example: -ex 3 -ex 5 -ex 6).")
@add_common_options()
def find_replace(input_path, old_string, new_string, name_id, platform, fix_cff, exclude_namerecord, outputDir,
                 recalcTimestamp, overWrite):
    """Replaces a string in the `name` table and, optionally, in the `CFF` table.

    Usage:

        ftcli names find-replace C:\\Fonts -os "Black" -ns "Heavy"

    If the `-cff` option is passed, the string will be replaced also in the `CFF` table:

        ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" --cff

    To simply remove a string, use an empty string as new string:

        ftcli names find-replace MyFont-Black.otf -os "Remove Me" -ns ""

    To replace the string in a specific platform ('win' or 'mac'):

        ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -p win

    To replace the string in a specific namerecord:

        ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -n 6

    The `-p / --platform` and `-n / --name-id` options can be combined:

        ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -p win -n 6

    To exclude one or more namerecords, use the `-ex / --exclude-namerecord` option:

        ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -ex 1 -ex 6

    If a namerecord is explicitly included but also explicitly excluded, it won't be changed:

        ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -n 1 -ex 1 -ex 6

    The above command will replace the string only in nameID 6.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            fix_count = font.findReplace(old_string, new_string, fixCFF=fix_cff, nameID=name_id, platform=platform,
                                         namerecords_to_ignore=exclude_namerecord)

            if fix_count > 0:
                output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
                font.save(output_file)
                click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
            else:
                click.secho(f'{os.path.basename(f)} --> no changes made', fg='yellow')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


# lang-help
@click.group()
def langHelp():
    pass


@langHelp.command()
def lang_help():
    """Prints available languages that can be used with the `set-name` and `del-names` commands.
    """
    from fontTools.ttLib.tables._n_a_m_e import (_MAC_LANGUAGES, _WINDOWS_LANGUAGES)
    print('\n[WINDOWS LANGUAGES]')
    winlist = []
    for v in _WINDOWS_LANGUAGES.values():
        winlist.append(v)
    winlist.sort()
    print(winlist)
    print('\n[MAC LANGUAGES]')
    maclist = []
    for v in _MAC_LANGUAGES.values():
        maclist.append(v)
    maclist.sort()
    print(maclist)


# name-from-txt
@click.group()
def nameFromTxt():
    pass


@nameFromTxt.command()
@add_file_or_path_argument()
@click.option('-n', '--name-id', type=click.IntRange(0, 32767), help="nameID (Integer between 0 and 32767)")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If it's not specified, name will be written in both tables.")
@click.option('-l', '--language', default="en", show_default=True, help="language")
@click.option('-i', '--input-file', type=click.Path(exists=True, resolve_path=True), required=True,
              help="Path to the text file to read.")
@add_common_options()
def name_from_txt(input_path, name_id, platform, language, input_file, outputDir, recalcTimestamp, overWrite):
    """Reads a text file and writes its content into the specified namerecord in the `name` table.

    If the namerecord is not present, it will be created. If it already exists, will be overwritten.

    If `name_id` parameter is not specified, the first available nameID will be used.

    By default, the namerecord will be written both in platformID 1 (Macintosh) and platformID 3 (Windows) tables. Use
    `-p/--platform-id [win|mac]` option to write the namerecord only in the specified platform.

    Use the `-l/--language` option to write the namerecord in a language different from 'en'. Use `ftcli names
    lang-help` to display available languages.
    """

    windows = False if platform == "mac" else True
    mac = False if platform == "win" else True

    with open(input_file, 'r', encoding='utf-8-sig') as f:
        string = f.read()

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            font.setMultilingualName(nameID=name_id, language=language, string=string, windows=windows, mac=mac)

            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


# set-cff-names
@click.group()
def setCffNames():
    pass


@setCffNames.command()
@add_file_or_path_argument()
@click.option('--font-name', type=str, default=None, help="Sets the CFF font name.")
@click.option('--full-name', type=str, default=None, help="Sets the CFF full name.")
@click.option('--family-name', type=str, default=None, help="Sets the CFF family name.")
@click.option('--weight', type=str, default=None, help="Sets the CFF weight.")
@click.option('--copyright', 'copyright_', type=str, default=None, help="Sets the CFF copyright.")
@click.option('--notice', type=str, default=None, help="Sets the CFF notice.")
@add_common_options()
def set_cff_names(input_path, font_name, full_name, family_name, weight, copyright_, notice, outputDir,
                  recalcTimestamp, overWrite):
    """Sets names in the CFF table.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            if 'CFF ' not in font:
                click.secho(f'{f} is not a CFF font', fg='red')
                return
            font.setCFFNames(fontNames=font_name, FullName=full_name, FamilyName=family_name, Weight=weight,
                             Copyright=copyright_, Notice=notice)
            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{output_file} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


# set-name
@click.group()
def setName():
    pass


@setName.command()
@add_file_or_path_argument()
@click.option('-n', '--name-id', type=click.IntRange(0, 32767), help="nameID (Integer between 0 and 32767)")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If it's not specified, name will be written in both tables.")
@click.option('-l', '--language', default="en", show_default=True, help="language")
@click.option('-s', '--string', required=True, help='string')
@add_common_options()
def set_name(input_path, name_id, platform, language, string, outputDir, recalcTimestamp, overWrite):
    """Writes the specified namerecord in the `name` table.

    If the namerecord is not present, it will be created. If it already exists, will be overwritten.

    If `name_id` parameter is not specified, the first available nameID will be used.

    By default, the namerecord will be written both in platformID 1 (Macintosh) and platformID 3 (Windows) tables. Use
    the `-p/--platform-id [win|mac]` option to write the namerecord only in the specified platform.

    Use the `-l/--language` option to write the namerecord in a language different from 'en'. Use `ftcli names
    lang-help` to display available languages.
    """

    windows = False if platform == "mac" else True
    mac = False if platform == "win" else True

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            font.setMultilingualName(nameID=name_id, language=language, string=string, windows=windows, mac=mac)

            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


@click.group()
def win2Mac():
    pass


@win2Mac.command()
@add_file_or_path_argument()
@add_common_options()
def win_2_mac(input_path, outputDir, recalcTimestamp, overWrite):
    """Copies all namerecords from Windows table to Macintosh table.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = Font(f, recalcTimestamp=recalcTimestamp)
            font.win2mac()
            output_file = makeOutputFileName(f, outputDir=outputDir, overWrite=overWrite)
            font.save(output_file)
            click.secho(f'{os.path.basename(output_file)} --> saved', fg='green')
        except Exception as e:
            click.secho(f'ERROR: {e}', fg='red')


cli = click.CommandCollection(sources=[
    setName, nameFromTxt, delNames, setCffNames, findReplace, win2Mac, delMacNames,
    langHelp, cleanNameTable, copyNames, addPrefix, addSuffix],
    help="A set of command line tools to manipulate `name` table entries.")

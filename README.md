[![Codacy Badge](https://app.codacy.com/project/badge/Grade/40e399b0a8e04713848c34a59d9e8914)](https://app.codacy.com/gh/ftCLI/ftCLI/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# ftCLI

ftCLI is a command line interface built with [click](https://click.palletsprojects.com/en/8.0.x/) to edit fonts using
[FontTools](https://github.com/fonttools/fonttools).

Python >=3.7 <3.11 is required to install ftCLI.

The following packages will be installed during setup:

- fonttools
- afdko
- beziers
- brotli
- click
- dehinter
- pathvalidate
- rich
- skia-pathops
- ttfautohint-py
- ufo2ft
- zopfli

## Installation

    pip install font-cli

Or, to install in editable mode:

    git clone https://github.com/ftCLI/ftCLI.git

    cd ftCLI

    pip install -e .

## tl;dr

To start using ftCLI, just install, open a shell and type `ftcli --help` to list all commands.

![image](https://user-images.githubusercontent.com/83063506/229529687-c711e860-c93b-49c8-a137-1e9e37c6a0af.png)


Each level 1 command has its own help...

![image](https://user-images.githubusercontent.com/83063506/229529823-851b257d-69c3-4daa-a72c-42be96db209f.png)

... as well as each level 2 command.

![image](https://user-images.githubusercontent.com/83063506/229529954-cedc0e1d-9d15-4c6c-81be-d8923f8dc7d7.png)

Remember to use `--no-overwrite` or `-out` to avoid overwriting your fonts when experimenting.

## Arguments

- [INPUT_PATH](#inputpath)

## Common options

- [-out, --output-dir](#-out---output-dir)
- [--recalc-timestamp](#--recalc-timestamp)
- [--no-overwrite](#--no-overwrite)

## Commands list

- [**assistant**](#ftcli-assistant)

  - [ui](#ftcli-assistant-ui)
  - [commit](#ftcli-assistant-commit)
  - [init-config](#ftcli-assistant-init-config)
  - [init-data](#ftcli-assistant-init-data)

- [**cff**](#ftcli-cff)

  - [del-names](#ftcli-cff-del-names)
  - [find-replace](#ftcli-cff-find-replace)
  - [fix-version](#ftcli-cff-fix-version)
  - [set-names](#ftcli-cff-set-names)

- [**converter**](#ftcli-converter)

  - [otf2ttf](#ftcli-converter-otf2ttf)
  - [ttf2otf](#ftcli-converter-ttf2otf)
  - [ft2wf](#ftcli-converter-ft2wf)
  - [wf2ft](#ftcli-converter-wf2ft)
  - [var2static](#ftcli-converter-var2static)
  - [ttc2sfnt](#ftcli-converter-ttc2sfnt)

- [**fix**](#ftcli-fix)

  - [caret-offset](#ftcli-fix-caret-offset)
  - [decompose-transformed](#ftcli-fix-decompose-transformed)
  - [duplicate-components](#ftcli-fix-duplicate-components)
  - [italic-angle](#ftcli-fix-italic-angle)
  - [kern-table](#ftcli-fix-kern-table)
  - [monospace](#ftcli-fix-monospace)
  - [nbsp-missing](#ftcli-fix-nbsp-missing)
  - [nbsp-width](#ftcli-fix-nbsp-width)
  - [os2-ranges](#ftcli-fix-os2-ranges)
  - [strip-names](#ftcli-fix-strip-names)

- [**metrics**](#ftcli-metrics)

  - [align](#ftcli-metrics-align)
  - [copy-metrics](#ftcli-metrics-copy-metrics)
  - [set-linegap](#ftcli-metrics-set-linegap)

- [**name**](#ftcli-name)

  - [append](#ftcli-name-append)
  - [del-mac-names](#ftcli-name-del-mac-names)
  - [del-names](#ftcli-name-del-names)
  - [find-replace](#ftcli-name-find-replace)
  - [find-set-name](#ftcli-name-set-name)

- [**os2**](#ftcli-os2)

- [**post**](#ftcli-post)

- [**print**](#ftcli-print)
  - [font-info](#ftcli-print-font-info)
  - [font-names](#ftcli-print-font-names)
  - [font-fonts-list](#ftcli-print-fonts-list)
  - [os2-table](#ftcli-print-os2-table)

- [**utils**](#ftcli-utils)
  - [add-dsig](#ftcli-utils-add-dsig)
  - [cff-autohint](#ftcli-utils-cff-autohint)
  - [cff-check-outlines](#ftcli-utils-cff-check-outlines)
  - [cff-dehint](#ftcli-utils-cff-dehint)
  - [cff-desubr](#ftcli-utils-cff-desubr)
  - [cff-subr](#ftcli-utils-cff-subr)
  - [del-table](#ftcli-utils-del-table)
  - [font-organizer](#ftcli-utils-font-organizer)
  - [font-renamer](#ftcli-utils-font-renamer)
  - [ttf-autohint](#ftcli-utils-ttf-autohint)
  - [ttf-dehint](#ftcli-utils-ttf-dehint)
  - [ttf-remove-overlaps](#ftcli-utils-ttf-remove-overlaps)

## Arguments

### INPUT_PATH

With some exceptions, all ftCLI subcommands process files in the given path. The `INPUT_PATH` argument can be generally
a single font file or a folder containing one or more fonts. In case a directory is passed as INPUT_PATH, all fonts
stored in it will be processed, with the exclusion of fonts stored in subdirectories.

## Common options

The `-out, -output-dir`, `--recalc-timestamp` and `--no-overwrite` options can be used in all subcommands, unless
otherwise specified.

### -out, --output-dir

The directory where the output files are to be saved. If `output_dir` is not specified, files are saved to the same
folder. If the user passes a directory that doesn't exist, it will be automatically created.

### --recalc-timestamp

By default, original `head.modified` value is kept when a font is saved. Use this option to set `head.modified`
timestamp to current time.

### --no-overwrite

By default, modified files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name, so that Times-Bold.otf becomes TimesBold#1.otf).

### Usage examples:

`ftcli metrics align "C:\Fonts" -out "C:\Fonts\Aligned"`

`ftcli metrics copy -s "C:\Fonts\SourceFont.otf" -d "C:\Fonts\" --recalc-timestamp`

`ftcli metrics copy -s "C:\Fonts\SourceFont.otf" -d "C:\Fonts\" --no-overwrite`

## ftcli assistant

A set of tools to correctly compile the 'name' table and set proper values for usWeightClass, usWidthClass, Bold, Italic
and Oblique bits.

**Usage**:

    ftcli assistant

**Commands**:

      commit
      init-config
      init-data
      ui

The logical steps are the following:

1. Create a CSV file containing, for each font in the source path, the following data:
   - File path
   - Family name
   - usWidthClass
   - usWeightClass
   - Slope classes (Italic and/or Oblique) and Bold flag
   - Weight, Width and Slope style names
2. Review the CSV file
3. Write data from the CSV file to the target fonts: this will compile the name table and set the proper
   usWidthClass, usWeightClass Slope class and Bold values.

**Step 1** can be executed with one of the following commands:

- `ftcli assistant init-data INPUT_PATH`
- `ftcli assistant ui INPUT_PATH`

The first command will create a directory named `ftCLI_files` containing two files: `fonts_data.csv` and
`styles_mapping.json`. The second one will open the command line user interface that allows to edit both.

The `styles_mapping.json` is created at first, unless it already exists, and contains the default Style Names to pair
with usWidthClass, usWeightClass and Slope class. The default values are the following:

    {
        "italics": ["It", "Italic"],
        "obliques": ["Obl", "Oblique"],
        "weights": {
            "250": ["Th", "Thin" ],
            "275": ["XLt", "ExtraLight"],
            "300": ["Lt", "Light"],
            "350": ["Bk", "Book"],
            "400": ["Rg", "Regular"],
            "500": ["Md", "Medium"],
            "600": ["SBd", "SemiBold"],
            "700": ["Bd", "Bold"],
            "800": ["XBd", "ExtraBold"],
            "850": ["Hvy", "Heavy"],
            "900": ["Blk","Black"],
            "950": ["Ult", "Ultra"]
        },
        "widths": {
            "1": ["Cm", "Compressed"],
            "2": ["XCn", "ExtraCondensed"],
            "3": ["Cn", "Condensed"],
            "4": ["Nr", "Narrow"],
            "5": ["Nor","Normal"],
            "6": ["Wd", "Wide"],
            "7": ["Ext", "Extended"],
            "8": ["XExt", "ExtraExtended"],
            "9": ["Exp", "Expanded"]
        }
    }

After creation of `styles_mapping.json`, all valid font files found in `INPUT_PATH` are parsed to retrieve Family Name,
usWidthClass, usWeightClass, Slope Class (Upright, Italic or Oblique). The process searches for matches between the
retrieved values and the JSON data, trying to determine the proper style names. The results are written into the
`fonts_data.csv` file.

The `fonts_data.csv` contains the following columns:

- `file_name`: path to the font file
- `family_name`: the font's family name, retrieved reading the name table
- `is_bold`: True if the bold bits are set, False if they are not set. This column is present only for completeness,
  but it's value will be ignored. A font will be set as bold only and only if, while running the `ftcli assistant commit`
  command, the user will choose to use linked styles.
  (-ls / --linked styles) option while writing data from CSV to fonts
- `is_italic`: True if the italic bits are set, False if they are not set
- `is_oblique`: True if the oblique bit is set, False if it's not set
- `us_width_class`: usWidthClass value
- `us_weight_class`: usWeightClass value
- `wdt`: short literal for the Width style name
- `width`: long literal for the Width style name
- `wgt`: short literal for the Weight style name
- `weight`: long literal for the Weight style name
- `slp`: short literal for the Slope style name
- `slope`: long literal for the Slope style name
- `selected`: 0 to exclude the file while writing data from CSV to fonts, 1 to include the file

Both files can be edited manually or using the character interface.

**Step 2** can be executed, after reviewing `fonts_data.csv`, running the `ftcli assistant commit` command.

### ftcli assistant ui

Opens the character user interface to edit the `styles_mapping.json` and `fonts_data.csv` files. If one or both files
do not exist, they will be automatically created.

**Usage**

    ftcli assistant ui INPUT_PATH

The main window displays a list of fonts found in `INPUT_PATH` and allows to access the editors for
`styles_mapping.json` and `fonts_data.csv`.

The Main Window:

![image](https://user-images.githubusercontent.com/83063506/226935693-519309a4-c76c-4321-8f1d-5bc0e7a32de5.png "ftCLI assistant main window")

The Styles Mapping Editor:

![image](https://user-images.githubusercontent.com/83063506/227150344-6ffd5730-c75c-4836-a8a7-ccb1518d6414.png "Styles Mapping Editor")

The Fonts Data Editor:

![image](https://user-images.githubusercontent.com/83063506/227150698-c7c5c0c3-2374-422d-8be7-c19c8c41c69d.png "The Fonts Data Editor")

When the `fonts_data.csv` file contains the desired values, data are ready to be written to fonts using the `ftcli
assistant commit` command.

### ftcli assistant commit

Writes data from CSV to fonts.

**Usage**:

    ftcli assistant commit [OPTIONS] INPUT_PATH

**Options**:

      --width-elidable TEXT           The width word to elide when building the
                                      namerecords.  [default: Normal]
      --weight-elidable TEXT          The weight word to elide when building the
                                      namerecords.  [default: Regular]
      -ls, --linked-styles <INTEGER RANGE INTEGER RANGE>...
                                      Use this option to activate linked styles.
                                      If this option is active, linked styles must
                                      be specified. For example: -ls 400 700, or
                                      -ls 300 600.
      -x, --exclude-namerecords [1|2|3|4|5|6|16|17|18]
                                      Name IDs to skip. The specified name IDs
                                      won't be recalculated. This option can be
                                      repeated (for example: -x 3 -x 5 -x 6...).
      -swdt, --shorten-width [1|4|6|16|17]
                                      Name IDs where to use the short word for
                                      width style name (for example, 'Cn' instead
                                      of 'Condensed'). This option can be repeated
                                      (for example: -swdt 1 -swdt 5, -swdt 16...).
      -swgt, --shorten-weight [1|4|6|17]
                                      Name IDs where to use the short word for
                                      weight style name (for example, 'Md' instead
                                      of 'Medium'). This option can be repeated
                                      (for example: -swgt 1 -swgt 5 -swgt 6...).
      -kwdt, --keep-width-elidable    Doesn't remove the width elidable words (by
                                      default, "Nor" and "Normal").
      -kwgt, --keep-weight-elidable   Doesn't remove the weight elidable words (by
                                      default, "Rg" and "Regular").
      -sslp, --shorten-slope [4|6|16|17]
                                      Name IDs where to use the short word for
                                      slope style name (for example, 'It' instead
                                      of 'Italic'). This option can be repeated
                                      (for example: -sslp 3 -sslp 5 -sslp 6...).
      -sf, --super-family             Superfamily mode. This option affects name
                                      IDs 3, 6, 16 and 17 in case of families with
                                      widths different than 'Normal'. If this
                                      option is active, name ID 6 will be
                                      'FamilyName-WidthWeightSlope' instead of
                                      'FamilyNameWidth-WeightSlope'. Mac and OT
                                      family/subfamily names will be FamilyName /
                                      Width Weight Slope' instead of 'Family Name
                                      Width / Weight Slope'.
      -aui, --alt-uid                 Use alternate unique identifier. By default,
                                      nameID 3 (Unique identifier) is calculated
                                      according to the following scheme:
                                      'Version;Vendor code;PostscriptName'. The
                                      alternate unique identifier is calculated
                                      according to the following scheme:
                                      'Manufacturer: Full Font Name: Creation
                                      Year'.
      -obni, --oblique-not-italic     By default, if a font has the oblique bit
                                      set, the italic bits will be set too. Use
                                      this option to override the default
                                      behaviour (for example, when the family has
                                      both italic and oblique styles and you need
                                      to keep oblique and italic styles separate).
                                      The italic bits will be cleared when the
                                      oblique bit is set.
      --no-auto-shorten               When name id 1, 4 or 6 are longer than
                                      maximum allowed (27 characters for nameID 1,
                                      31 for nameID 4 and 29 for nameID 6), the
                                      script tries to auto shorten those names
                                      replacing long words with short words. Use
                                      this option to prevent the script from auto
                                      shortening names.
      -cff                            If this option is active, fontNames,
                                      FullName, FamilyName and Weight values in
                                      the 'CFF' table will be recalculated.
      -out, --output-dir DIRECTORY    Specify the directory where output files are
                                      to be saved. If output_dir doesn't exist,
                                      will be created. If not specified, files are
                                      saved to the same folder.
      --recalc-timestamp              Keep the original font 'modified' timestamp
                                      (head.modified) or set it to current time.
                                      By default, original timestamp is kept.
      --no-overwrite                  Overwrite existing output files or save them
                                      to a new file (numbers are appended at the
                                      end of file name). By default, files are
                                      overwritten.
      --help                          Show this message and exit.

### ftcli assistant init-config

**Usage**:

    ftcli assistant init-config [OPTIONS] INPUT_PATH

**Options**

    -q, --quiet  Suppress the overwrite confirmation message if the config.json
                 file already exists.
    --help       Show this message and exit.

If, for some reason, the user needs to create or reset the `styles_mappings.json` file to the default values, this
command will serve the purpose. Not needed if `ftcli assistant ui` is used.

### ftcli assistant init-data

Creates the CSV database file `fonts_data.csv` in the `ftCLI_files` subdirectory. Not needed if `ftcli assistant ui`
is used.

**Usage**:

    ftcli assistant init-data [OPTIONS] INPUT_PATH

**Options**:

    -s, --styles-mapping-file FILE  Use a custom styles mapping file instead of
                                    the default styles_mapping.json file located
                                    in the ftCLI_files folder.
    -q, --quiet                     Suppress the overwrite confirmation message
                                    if the fonts_data.csv and/or styles_mapping.json
                                    files already exist in the ftCLI_files folder.
    --help                          Show this message and exit.

## ftcli cff

`CFF` table editor.

**Usage:**

    ftcli cff COMMAND [ARGS]

**Commands:**

    del-names
    find-replace
    fix-version
    set-names

### ftcli cff del-names

Deletes CFF names.

**Usage**:

    ftcli cff del-names [OPTIONS] INPUT_PATH

**Options**:

    --full-name                   Deletes CFF.cff.topDictIndex[0] FullName
    --family-name                 Deletes CFF.cff.topDictIndex[0] FamilyName
    --weight                      Deletes CFF.cff.topDictIndex[0] Weight
    --version                     Deletes CFF.cff.topDictIndex[0] version
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli cff find-replace

Finds a string in the following items of CFF table topDict and replaces it with a new string: `version`, `FullName`,
`FamilyName`, `Weight`, `Copyright`, `Notice`.

**Usage**:

    ftcli cff find-replace [OPTIONS] INPUT_PATH

**Options**:

    -os, --old-string TEXT        The string to be replaced  [required]
    -ns, --new-string TEXT        The string to replace the old string with
                                  [required]
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli cff fix-version

Aligns topDict version string to the `head.fontRevision` value.

For example, if `head.fontRevision` value is 2.001, CFF topDict version value will be 2.1.

**Usage**:

    ftcli cff fix-version [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli cff set-names

Sets CFF names.

**Usage**:

    ftcli cff set-names [OPTIONS] INPUT_PATH

**Options**:

    --font-names TEXT             Sets CFF.cff.fontNames value
    --full-name TEXT              Sets CFF.cff.topDictIndex[0] FullName value
    --family-name TEXT            Sets CFF.cff.topDictIndex[0] FamilyName value
    --weight TEXT                 Sets CFF.cff.topDictIndex[0] Weight value
    --version TEXT                Sets CFF.cff.topDictIndex[0] version value
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

## ftcli converter

Font converter.

**Usage**:

    ftcli converter [OPTIONS] COMMAND [ARGS]...

**Options**:
--help Show this message and exit.

**Commands**:

    ft2wf
    otf2ttf
    ttc2sfnt
    ttf2otf
    var2static
    wf2ft

### ftcli converter ft2wf

Converts SFNT fonts (TTF or OTF) to web fonts (WOFF and/or WOFF2)

**Usage**:

    ftcli converter ft2wf [OPTIONS] INPUT_PATH

**Options**:

    -f, --flavor [woff|woff2]     By default, the script converts SFNT fonts
                                  (TrueType or OpenType) both to woff and woff2
                                  flavored web fonts. Use this option to create
                                  only woff (--flavor woff) or woff2 (--flavor
                                  woff2) files.
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli converter otf2ttf

Converts fonts from OTF to TTF format.

**Usage**:

    ftcli converter otf2ttf [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli converter ttc2sfnt

Extracts each font from a TTC file, and saves it as a TTF or OTF file.

**Usage**:

    ftcli converter ttc2sfnt [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli converter ttf2otf

Converts TTF fonts (or TrueType flavored woff/woff2 web fonts) to OTF fonts (or CFF flavored woff/woff2 web fonts).

**Usage**:

    ftcli converter ttf2otf [OPTIONS] INPUT_PATH

**Options**:

    -t, --tolerance FLOAT RANGE   Conversion tolerance (0-2.5, default 1). Low
                                  tolerance adds more points but keeps shapes.
                                  High tolerance adds few points but may change
                                  shapes.
    --safe                        Sometimes Qu2CuPen may fail or produce
                                  distorted outlines. Most of times, use of '--
                                  safe' will prevent errors by converting the
                                  source TTF font to a temporary OTF built using
                                  T2CharstringsPen, and then reconverting it to
                                  a temporary TTF font. This last one will be
                                  used for TTF to OTF conversion instead of the
                                  source TTF file. This is slower, but safest.
    --keep-glyphs                 Keeps NULL and CR glyphs from the output font
    --no-subr                     Do not subroutinize converted fonts
    --check-outlines              Performs optional outline quality checks and
                                  removes overlaps with afdko.checkoutlinesufo
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli converter var2static

Exports static instances from variable fonts.

**Usage**:

    ftcli converter var2static [OPTIONS] INPUT_PATH

**Options**:

    -s, --select-instance         By default, the script exports all named
                                  instances. Use this option to select custom
                                  axis values for a single instance.
    --no-cleanup                  By default, STAT table is dropped and axis
                                  nameIDs are deleted from name table. Use --no-
                                  cleanup to keep STAT table and prevent axis
                                  nameIDs to be deleted from name table.
    --update-name-table           Update the instantiated font's `name` table.
                                  Input font must have a STAT table with Axis
                                  Value Tables
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli converter wf2ft

Converts web fonts (WOFF and WOFF2) to SFNT fonts (TTF or OTF).

**Usage**:

    ftcli converter wf2ft [OPTIONS] INPUT_PATH

**Options**:

    -f, --flavor [woff|woff2]     By default, the script converts both woff and
                                  woff2 flavored web fonts to SFNT fonts
                                  (TrueType or OpenType). Use this option to
                                  convert only woff or woff2 flavored web fonts.
    -d, --delete-source-file      Deletes the source files after conversion.
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

## ftcli fix

A set of commands to detect and automatically fix font errors.

**Usage**:

    ftcli fix [OPTIONS] COMMAND [ARGS]...

**Options**:

    --help  Show this message and exit.

**Commands**:

    caret-offset
    decompose-transformed
    duplicate-components
    italic-angle
    kern-table
    nbsp-missing
    nbsp-width
    os2-ranges
    strip-names

### ftcli fix caret-offset

Recalculates `hhea.caretOffset` value.

**Usage**:

    ftcli fix caret-offset [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix decompose-transformed

Decomposes composite glyphs that have transformed components.

fontbakery check id: com.google.fonts/check/transformed_components

**Usage**:

    ftcli fix decompose-transformed [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix duplicate-components

Removes duplicate components which have the same x,y coordinates.

fontbakery check id: com.google.fonts/check/glyf_non_transformed_duplicate_components

**Usage**:

    ftcli fix duplicate-components [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix italic-angle

Recalculates `post.italicAngle`, `hhea.caretSlopeRise`, `hhea.caretSlopeRun` and sets/clears the italic/oblique bits
according to the calculated values. In CFF fonts, also `CFF.topDictIndex[0].ItalicAngle` is recalculated.

**Usage**:

    ftcli fix italic-angle [OPTIONS] INPUT_PATH

**Options**:

    -m, --mode INTEGER RANGE      1: sets only the italic bits and clears the oblique bit
                                  2: sets italic and oblique bits
                                  3: sets only the oblique bit and clears italic bits  [1<=x<=3]
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix kern-table

Some applications such as MS PowerPoint require kerning info on the kern
table. More specifically, they require a format 0 kern subtable from a kern
table version 0 with only glyphs defined in the cmap table.

Given this, the command deletes all kerning pairs from kern v0 subtables
where one of the two glyphs is not defined in the cmap table.

fontbakery check id: com.google.fonts/check/kern_table

**Usage**:

    ftcli fix kern-table [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix monospace

If the family is monospaced:

- post.isFixedPitch must be set to a non-zero value
- OS/2.panose.bProportion must be set to 9
- CFF.cff.TopDictIndex[0].isFixedPitch must be set to True

fontbakery check id: com.google.fonts/check/monospace

**Usage**:

    ftcli fix monospace [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix nbsp-missing

Checks if the font has a non-breaking space character, and if it doesn't, it adds one by double mapping 'space'

**Usage**:

    ftcli fix nbsp-missing [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix nbsp-width

Checks if 'nbspace' and 'space' glyphs have the same width. If not, corrects 'nbspace' width to match 'space' width.

fontbakery check id: com.google.fonts/check/whitespace_widths

**Usage**:

    ftcli fix nbsp-width [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix os2-ranges

Generates a temporary Type 1 from the font file using tx, converts that to an OpenType font using makeotf, reads the
Unicode ranges and codepage ranges from the temporary OpenType font file, and then writes those ranges to the
original font's OS/2 table.

**Usage**:

    ftcli fix os2-ranges [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli fix strip-names

Removes leading and trailing spaces from all namerecords.

fontbakery check id: com.google.fonts/check/name/trailing_spaces

**Usage**:

    ftcli fix strip-names [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.


### ftcli fix uprights

Assuming that the font is correctly set as upright (i.e.: italic oblique
bits are all clear), the script sets the following values:

- post.italicAngle = 0.0
- hhea.caretSlopeRise = 1
- hhea.caretSlopeRun = 0
- hhea.caretOffset = 0
- CFF.cff.topDictIndex[0].ItalicAngle = 0 (only if the font has a CFF table)

The font is saved only if at least one table has changed.

**Usage**:

    ftcli fix uprights [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

## ftcli hhea

Command line hhea table editor.

**Usage**:

    ftcli hhea [OPTIONS] INPUT_PATH

**Options**:

    --rise INTEGER                Sets the `caretSlopeRise` value.
    --run INTEGER                 Sets the `caretSlopeRun` value.
    --offset INTEGER              Sets the `caretOffset` value.
    --ascent INTEGER              Sets the `ascent` value.
    --descent INTEGER             Sets the `descent` value.
    --linegap INTEGER             Sets the `lineGap` value.
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

## ftcli metrics

Vertical metrics tools.

**Usage**:

    ftcli metrics [OPTIONS] COMMAND [ARGS]...

**Options**:

    --help  Show this message and exit.

**Commands**:

    align
    copy
    set-linegap

### ftcli metrics align

Aligns all fonts stored in INPUT_PATH folder to the same baseline.

To achieve this, the script finds the maximum ascender and the minimum descender values of the fonts stored in the
INPUT_PATH folder and applies those values to all fonts.

This can produce undesired effects (an exaggerated line height) when one or more fonts contain swashes, for example. In
such cases, it's better to copy the vertical metrics from a template font to one or more destination fonts using the
[`ftcli metrics copy`](#ftcli-metrics-copy-metrics) command.

See https://kltf.de/download/FontMetrics-kltf.pdf for more information.

**Usage**:

    ftcli metrics align [OPTIONS] INPUT_PATH

**Options**:

Options:

    --with-linegap                By default, SIL method
                                  (https://silnrsi.github.io/FDBP/en-
                                  US/Line_Metrics.html) is used. This means
                                  that, in OS/2 table, sTypoAscender and
                                  sTypoDescender values are set, respectively,
                                  equal to maximum real ascender and minimum
                                  real descender, and the sTypoLineGap is set to
                                  zero. Use '--with-linegap' to set
                                  sTypoAscender value to the maximum ideal
                                  ascender (calculated from letters b, f, f, h,
                                  k, l and t) and the sTypoDescender value to
                                  the minimum ideal descender (calculated from
                                  letters g, j, p, q and y). The sTypoLineGap
                                  will be calculated as follows: (real ascender
                                  + abs(real descender)) - (ideal ascender +
                                  abs(ideal descender)).
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli metrics copy-metrics

Copies vertical metrics from a source font to one or more destination fonts.

**Usage**:

    ftcli metrics copy [OPTIONS]

**Options**:

    -s, --source-file FILE      Source file. Vertical metrics from this font
                                will be applied to all destination fonts.
                                [required]
    -d, --destination PATH      Destination file or directory.  [required]
    -o, --output-dir DIRECTORY  The output directory where the output files are
                                to be created. If it doesn't exist, will be
                                created. If not specified, files are saved to
                                the same folder.
    --recalc-timestamp          By default, original head.modified value is kept
                                when a font is saved. Use this switch to set
                                head.modified timestamp to current time.
    --no-overwrite              By default, modified files are overwritten. Use
                                this switch to save them to a new file (numbers
                                are appended at the end of file name).
    --help                      Show this message and exit.

### ftcli metrics set-linegap

Modifies the line spacing metrics in one or more fonts.

This is a fork of font-line by Source Foundry: https://github.com/source-foundry/font-line

**Usage**:

    ftcli metrics set-linegap [OPTIONS] INPUT_PATH

**Options**:

    -p, --percent INTEGER RANGE     Adjust font line spacing to % of UPM value.
                                    [1<=x<=100; required]
    -mfn, --modify-family-name      Adds LG% to the font family to reflect the
                                    modified line gap.
    -o, --output-dir DIRECTORY      The output directory where the output files
                                    are to be created. If it doesn't exist, will
                                    be created. If not specified, files are
                                    saved to the same folder.
    --recalc-timestamp / --no-recalc-timestamp
                                    Keeps the original font 'modified' timestamp
                                    (head.modified) or set it to current time.
                                    By default, original timestamp is kept.
    --overwrite / --no-overwrite    Overwrites existing output files or save
                                    them to a new file (numbers are appended at
                                    the end of file name). By default, files are
                                    overwritten.
    --help                          Show this message and exit.

## ftcli name

Command line `name` table editor.

**Usage**:

    ftcli name [OPTIONS] COMMAND [ARGS]...

**Options**:

    --help  Show this message and exit.

**Commands**:

    append
    del-mac-names
    del-names
    find-replace
    set-name

### ftcli name append

Appends a prefix, or a suffix to the specified namerecords

**Usage**:

    ftcli name append [OPTIONS] INPUT_PATH

**Options**:

    -n, --name-id INTEGER         NameID where to append the prefix/suffix. This
                                  option can be repeated to prepend/append the
                                  string to multiple namerecords. For example:
                                  -n 1 -n 2 -n 16 -n 17  [required]
    -p, --platform-id [0|1|3]     Use this option to add the prefix/suffix only
                                  to the namerecords matching the provided
                                  platformID.

                                  0: Unicode
                                  1: Macintosh
                                  3: Windows
    -l, --language-string TEXT    Use this option to append the prefix/suffix
                                  only to the namerecords matching the provided
                                  language string.

                                  See epilog for a list of valid language
                                  strings.
    --prefix TEXT                 The string to be prepended to the namerecords
    --suffix TEXT                 The suffix to append to the namerecords
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli name del-mac-names

Deletes all the Macintosh namerecords from the name table, except nameIDs 1, 2, 4, 5, and 6.

According to Apple (https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html), "names with
platformID 1 were required by earlier versions of macOS. Its use on modern platforms is discouraged. Use names with
platformID 3 instead for maximum compatibility. Some legacy software, however, may still require names with
platformID 1, platformSpecificID 0".

**Usage**:

    ftcli name del-mac-names [OPTIONS] INPUT_PATH

**Options**:

    --del-all                     Deletes also nameIDs 1, 2, 4, 5 and 6.
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli name del-names

Deletes one or more namerecords.

**Usage**:

    ftcli name del-names [OPTIONS] INPUT_PATH

**Options**:

    -n, --name-id INTEGER         NameID(s) to delete.

                                  This option can be repeated to delete multiple
                                  namerecords at once. For example: -n 1 -n 2 -n
                                  6  [required]
    -p, --platform-id [0|1|3]     PlatformID of the namerecords to delete:

                                  0: Unicode
                                  1: Macintosh
                                  3: Windows

                                  If no platform is specified, namerecords will
                                  be deleted from all tables.
    -l, --language-string TEXT    Use this option to filter the namerecords to
                                  delete by language string (for example: 'it',
                                  'de', 'nl'). See epilog for a list of valid
                                  language strings.
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli name find-replace

Finds a string in the specified namerecords and replaces it with a new string

**Usage**:

    ftcli name find-replace [OPTIONS] INPUT_PATH

**Options**:

    -os, --old-string TEXT         The string to be replaced  [required]
    -ns, --new-string TEXT         The string to replace the old string with
                                   [required]
    -n, --name-id INTEGER          nameIDs where to search and replace the
                                   string. If not specified, the string will be
                                   replaced in all namerecords. This option can
                                   be repeated to perform search and replace in
                                   multiple namerecords (e.g.: -n 1 -n 4 -n 6)
    -x, --exclude-name-id INTEGER  NameID to ignore. The specified nameID won't
                                   be changed. This option can be repeated
                                   multiple times (e.g.: -ex 3 -ex 5 -ex 16).
    -p, --platform-id [1|3]        platform id [1: macintosh, 3: windows]. If no
                                   platform is specified, the string will be
                                   replaced in both tables.
    -out, --output-dir DIRECTORY   Specify the directory where output files are
                                   to be saved. If output_dir doesn't exist,
                                   will be created. If not specified, files are
                                   saved to the same folder.
    --recalc-timestamp             Keep the original font 'modified' timestamp
                                   (head.modified) or set it to current time. By
                                   default, original timestamp is kept.
    --no-overwrite                 Overwrite existing output files or save them
                                   to a new file (numbers are appended at the
                                   end of file name). By default, files are
                                   overwritten.
    --help                         Show this message and exit.

### ftcli name set-name

Adds a namerecord to one or more font files.

If the namerecord is already present, it will be overwritten.

**Usage**:

    ftcli name set-name [OPTIONS] INPUT_PATH

**Options**:

    -n, --name-id INTEGER RANGE   The nameID of the namerecord to add.
                                  [0<=x<=32767; required]
    -s, --string TEXT             String to write in the namerecord.  [required]
    -p, --platform-id [1|3]       Use this option to write the namerecord only
                                  in the specified table:

                                  1: Macintosh
                                  3: Windows

                                  If not specified, namerecord will be written
                                  in both tables.
    -l, --language-string TEXT    Use this option to write the namerecord in a
                                  language different than 'en' (e.g.: 'it',
                                  'nl', 'de').

                                  See epilog for a list of valid language
                                  strings  [default: en]
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

## ftcli os2

Command line `OS/2` table editor.

**Usage**:

    ftcli os2 [OPTIONS] INPUT_PATH

**Options**:

    -ver, --version INTEGER RANGE   Upgrades `OS/2` table version.  [1<=x<=5]
    -wgh, --weight INTEGER RANGE    Sets `usWeightClass` value.  [1<=x<=1000]
    -wdt, --width INTEGER RANGE     Sets `usWidthClass` value.  [1<=x<=9]
    -it, --italic / -no-it, --no-italic
                                    Sets or clears the ITALIC bits
                                    (`fsSelection` bit 0 and `head` table
                                    `macStyle` bit 1).
    -bd, --bold / -no-bd, --no-bold
                                    Sets or clears the BOLD bits
                                    (`OS/2.fsSelection` bit 5 and
                                    `head.macStyle` bit 0).
    -rg, --regular                  Sets REGULAR (`fsSelection` bit) 6 and
                                    clears BOLD (`fsSelection` bit 5,
                                    `head.macStyle` bit 0) and ITALIC
                                    (`fsSelection` bit 0, `head.macStyle` bit 1)
                                    bits. This is equivalent to `--no-bold --no-
                                    italic`.
    -obl, --oblique / -no-obl, --no-oblique
                                    Sets or clears the OBLIQUE bit
                                    (`fsSelection` bit 9).
    -utm, --use-typo-metrics / -no-utm, --no-use-typo-metrics
                                    Sets or clears the USE_TYPO_METRICS bit
                                    (`fsSelection` bit 7).

                                    If set, it is strongly recommended that
                                    applications use `OS/2.sTypoAscender` -
                                    `OS/2.sTypoDescender` +  `OS/2.sTypoLineGap`
                                    as the default line spacing for the font.

                                    See: https://docs.microsoft.com/en-
                                    us/typography/opentype/spec/os2#fsselection
    -wws, --wws-consistent / -no-wws, --no-wws-consistent
                                    Sets or clears the WWS bit (`fsSelection`
                                    bit 8).

                                    If the `OS/2.fsSelection` bit is set, the
                                    font has `name` table strings consistent
                                    with a weight/width/slope family without
                                    requiring use of name IDs 21 and 22.

                                    See: https://docs.microsoft.com/en-
                                    us/typography/opentype/spec/os2#fsselection

                                    Also: https://typedrawers.com/discussion/385
                                    7/fontlab-7-windows-reads-exported-font-
                                    name-differently
    -vend, --ach-vend-id TEXT       Sets the `achVendID` tag (vendor's four-
                                    character identifier).
    -el, --embed-level [0|2|4|8]    Sets/clears `fsType` bits 0-3
                                    (EMBEDDING_LEVEL).

                                    0: Installable embedding
                                    2: Restricted License embedding
                                    4: Preview & Print embedding
                                    8: Editable embedding

                                    See: https://docs.microsoft.com/en-
                                    us/typography/opentype/spec/os2#fstype
    -ns, --no-subsetting / -as, --allow-subsetting
                                    Sets or clears `fsType` bit 8
                                    (NO_SUBSETTING).

                                    When this bit is set, the font may not be
                                    subsetted prior to embedding. Other
                                    embedding restrictions specified in bits 0-3
                                    and 9 also apply.
    -beo, --bitmap-embedding-only / -no-beo, --no-bitmap-embedding-only
                                    Sets or clears `fsType` bit 9
                                    (BITMAP_EMBEDDING_ONLY).

                                    When this bit is set, only bitmaps contained
                                    in the font may be embedded. No outline data
                                    may be embedded. If there are no bitmaps
                                    available in the font, then the font is
                                    considered unembeddable and the embedding
                                    services will fail. Other embedding
                                    restrictions specified in bits 0-3 and 8
                                    also apply.
    --recalc-unicode-ranges         Recalculates the `ulUnicodeRange*` values.
    --recalc-codepage-ranges        Recalculates `ulCodePageRange1` and
                                    `ulCodePageRange2` values.
    --recalc-x-height               Recalculates `sxHeight` value.
    --recalc-cap-height             Recalculates `sCapHeight` value.
    --recalc-italic-bits            Sets or clears the italic bits in
                                    OS/2.fsSelection and in head.macStyle,
                                    according to the `italicAngle` value in
                                    `post` table. If `italicAngle` value is
                                    other than 0.0, italic bits will be set. If
                                    `italicAngle` value is 0.0, italic bits will
                                    be cleared.
    --recalc-max-context            Recalculates `usMaxContext` value.
    --import-unicodes FILE          Imports `ulUnicodeRanges*` from a source
                                    font.
    -out, --output-dir DIRECTORY    Specify the directory where output files are
                                    to be saved. If output_dir doesn't exist,
                                    will be created. If not specified, files are
                                    saved to the same folder.
    --recalc-timestamp              Keep the original font 'modified' timestamp
                                    (head.modified) or set it to current time.
                                    By default, original timestamp is kept.
    --no-overwrite                  Overwrite existing output files or save them
                                    to a new file (numbers are appended at the
                                    end of file name). By default, files are
                                    overwritten.
    --help                          Show this message and exit.

## ftcli post

Command line `post` table editor.

**Usage**:

    ftcli post [OPTIONS] INPUT_PATH

**Options**:

    --italic-angle FLOAT RANGE      Sets the `italicAngle` value.
                                    [-90.0<=x<=90.0]
    --ul-position INTEGER           Sets the `underlinePosition` value.
    --ul-thickness INTEGER          Sets the `underlineThickness` value.
    --fixed-pitch / --no-fixed-pitch
                                    Sets or clears the `isFixedPitch` value.
    -out, --output-dir DIRECTORY    Specify the directory where output files are
                                    to be saved. If output_dir doesn't exist,
                                    will be created. If not specified, files are
                                    saved to the same folder.
    --recalc-timestamp              Keep the original font 'modified' timestamp
                                    (head.modified) or set it to current time.
                                    By default, original timestamp is kept.
    --no-overwrite                  Overwrite existing output files or save them
                                    to a new file (numbers are appended at the
                                    end of file name). By default, files are
                                    overwritten.
    --help                          Show this message and exit.

## ftcli print

Prints various font's information.

**Usage**:
ftcli print [OPTIONS] COMMAND [ARGS]...

**Options**:

    --help  Show this message and exit.

**Commands**:

    font-info
    font-names
    fonts-list
    os2-table

### ftcli print font-info

Prints detailed font information.

**Usage**:

    ftcli print font-info [OPTIONS] INPUT_PATH

**Options**:

    --help  Show this message and exit.

### ftcli print font-names

Prints the `name` table and, if the font is CFF, the names in the `CFF` table topDict.

**Usage**:

    ftcli print font-names [OPTIONS] INPUT_PATH

**Options**:

    -ml, --max-lines INTEGER  Maximum number of lines to be printed for each
                              namerecord
    -m, --minimal             Prints a minimal set of namerecords, omitting the
                              ones with nameID not in 1, 2, 3, 4, 5, 6, 16, 17,
                              18,  21, 22, 25
    --help                    Show this message and exit.

### ftcli print fonts-list

Prints a list of fonts with basic information.

**Usage**:

    ftcli print fonts-list [OPTIONS] INPUT_PATH

**Options**:

    --help  Show this message and exit.

### ftcli print os2-table

Prints the `OS/2` table.

**Usage**:

    ftcli print os2-table [OPTIONS] INPUT_PATH

**Options**:

    --help  Show this message and exit.

## ftcli utils

Miscellaneous utilities.

**Usage**:

    ftcli utils [OPTIONS] COMMAND [ARGS]...

**Options**:

    --help  Show this message and exit.

**Commands**:

    add-dsig
    cff-autohint
    cff-check-outlines
    cff-dehint
    cff-desubr
    cff-subr
    font-organizer
    font-renamer
    ttf-autohint
    ttf-dehint
    ttf-remove-overlaps

### ftcli utils add-dsig

Adds a dummy DSIG table to fonts, unless the table is already present. WOFF2 flavored fonts are ignored, since encoders
must remove the DSIG table from woff2 font data.

**Usage**:

    ftcli utils add-dsig [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils cff-autohint

Autohints CFF fonts with psautohint.

**Usage**:

    ftcli utils cff-autohint [OPTIONS] INPUT_PATH

**Options**:

    --optimize / --no-optimize    Optimize the hinted font by specializing the
                                  charstrings and applying subroutines.
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils cff-check-outlines

Performs `afdko.checkoutlinesufo` outline quality checks and overlaps removal. Supports CFF fonts only.

**Usage**:

    ftcli utils cff-check-outlines [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils cff-dehint

Drops hinting from CFF fonts.

**Usage**:

    ftcli utils cff-dehint [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils cff-desubr

Desoubroutinize CFF fonts.

**Usage**:

    ftcli utils cff-desubr [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils cff-subr

Subroutinize CFF fonts.

**Usage**:

    ftcli utils cff-subr [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils del-table

Deletes the tables specified in the table_tag argument(s).

**Usage**:

    ftcli utils del-table [OPTIONS] INPUT_PATH

**Options**:

    -t, --table-tag TEXT          TableTag of the table(s) to delete. Can be
                                  repeated to delete multiple tables at once
                                  [required]
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils font-organizer

Organizes fonts by moving them into a subdirectory named after the font's family name, and eventually a subdirectory
named after the font's extension and version.

**Usage**:

    ftcli utils font-organizer [OPTIONS] INPUT_PATH

**Options**:

    --rename-source [1|2|3|4|5]  Renames the font files according to the
                                 provided source string(s). See ftcli utils
                                 font-renamer.
    -ext, --extension            Sorts fonts by extension.
    -ver, --version              Sorts fonts by version.
    --help                       Show this message and exit.

### ftcli utils font-renamer

Takes a path to a single font file or directory of font files, extracts each font's metadata according to the
`--source` parameter passed by the user, and renames the font file to match the metadata, adding the correct
extension.

**Usage**:

    ftcli utils font-renamer [OPTIONS] INPUT_PATH

**Options**:

    -s, --source [1|2|3|4|5]  The source string(s) from which to extract the new
                              file name. Default is 1 (FamilyName-StyleName),
                              used also as fallback name when 4 or 5 are passed
                              but the font is TrueType

                              1: FamilyName-StyleName
                              2: PostScript Name
                              3: Full Font Name
                              4: CFF TopDict fontNames (CFF fonts only)
                              5: CFF TopDict FullName (CFF fonts only)
    --help                    Show this message and exit.


### ftcli utils scale-upm

Change the units-per-EM of fonts.

Hinting is removed from scaled TrueType fonts to avoid bad results. You may
consider to use `ftcli utils ttf-autohint` to hint the scaled fonts. In
addition, CFF scaled fonts are not subroutinized. Subroutines can be applied
using the `ftcli utils cff-subr` command.

**Usage**:

    ftcli utils scale-upm [OPTIONS] INPUT_PATH

**Options**:

    -upm INTEGER                  New UPM value  [default: 1000]
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.


### ftcli utils ttf-autohint

Autohints TrueType fonts using ttfautohint-py.

**Usage**:

    ftcli utils ttf-autohint [OPTIONS] INPUT_PATH

**Options**:

    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils ttf-dehint

Drops hinting from TrueType fonts.

This is a CLI for dehinter by Source Foundry: https://github.com/source-foundry/dehinter

**Usage**:

    ftcli utils ttf-dehint [OPTIONS] INPUT_PATH

**Options**:

    --keep-cvar                   keep cvar table
    --keep-cvt                    keep cvt table
    --keep-fpgm                   keep fpgm table
    --keep-hdmx                   keep hdmx table
    --keep-ltsh                   keep LTSH table
    --keep-prep                   keep prep table
    --keep-ttfa                   keep ttfa table
    --keep-vdmx                   keep vdmx table
    --keep-glyf                   do not modify glyf table
    --keep-gasp                   do not modify gasp table
    --keep-maxp                   do not modify maxp table
    --keep-head                   do not modify head table
    --verbose                     display standard output
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

### ftcli utils ttf-remove-overlaps

Simplify glyphs in TrueType fonts by merging overlapping contours.

**Usage**:

    ftcli utils ttf-remove-overlaps [OPTIONS] INPUT_PATH

**Options**:

    --ignore-errors               Ignore errors while removing overlaps.
    -out, --output-dir DIRECTORY  Specify the directory where output files are
                                  to be saved. If output_dir doesn't exist, will
                                  be created. If not specified, files are saved
                                  to the same folder.
    --recalc-timestamp            Keep the original font 'modified' timestamp
                                  (head.modified) or set it to current time. By
                                  default, original timestamp is kept.
    --no-overwrite                Overwrite existing output files or save them
                                  to a new file (numbers are appended at the end
                                  of file name). By default, files are
                                  overwritten.
    --help                        Show this message and exit.

**To Sergiev. May you rest in peace.**

# ftCLI

ftCLI is a command line interface built with [click](https://click.palletsprojects.com/en/8.0.x/) to edit fonts using
[FontTools](https://github.com/fonttools/fonttools).

Python >=3.7 <3.11 is required to install ftCLI.

The following packages will be installed during setup:

* fonttools
* afdko
* beziers
* brotli
* click
* dehinter
* pathvalidate
* rich
* skia-pathops
* ttfautohint-py
* ufo2ft
* zopfli
 
## Installation

```
git clone https://github.com/ftCLI/ftCLI.git

cd ftCLI

pip install -e .
```

## Arguments

* [INPUT_PATH](#input_path)

## Common options

* [-out, --output-dir](#-out---output-dir)
* [--recalc-timestamp](#--recalc-timestamp)
* [--no-overwrite](#--no-overwrite)

## Commands list

* [**assistant**](#ftcli-assistant)
  * [edit-cfg](#ftcli-assistant-edit-cfg)
  * [init-cfg](#ftcli-assistant-init-cfg)
  * [init-csv](#ftcli-assistant-init-csv)
  * [recalc-csv](#ftcli-assistant-recalc-csv)
  * [recalc-names](#ftcli-assistant-recalc-names)

* [**cff**](#ftcli-cff)
    * [find-replace](#ftcli-cff-find-replace)
    * [fix-version](#ftcli-cff-fix-version)
  
* [**converter**](#ftcli-converter)
    * [otf2ttf](#ftcli-converter-otf2ttf)
    * [ttf2otf](#ftcli-converter-ttf2otf)
    * [ft2wf](#ftcli-converter-ft2wf)
    * [wf2ft](#ftcli-converter-wf2ft)
    * [var2static](#ftcli-converter-var2static)
    * [ttf2sfnt](#ftcli-converter-ttc2sfnt)
    
* [**name**](#ftcli-names)
    * [add-prefix](#ftcli-names-add-prefix)
    * [add-suffix](#ftcli-names-add-suffix)
    * [clean-nametable](#ftcli-names-clean-name-table)
    * [copy-names](#ftcli-names-copy-names)
    * [del-mac-names](#ftcli-names-del-mac-names)
    * [del-names](#ftcli-names-del-names)
    * [find-replace](#ftcli-names-find-replace)
    * [lang-help](#ftcli-names-lang-help)
    * [name-from-txt](#ftcli-names-name-from-txt)
    * [set-name](#ftcli-names-set-name)
    * [set-cff-names](#ftcli-names-set-cff-names)
    * [win-2-mac](#ftcli-names-win-2-mac)

* [**os2**](#ftcli-os2)

* [**print**](#ftcli-print)
    * [ft-info](#ftcli-print-ft-info)
    * [ft-list](#ftcli-print-ft-list)
    * [ft-name](#ftcli-print-ft-name)
    * [ft-names](#ftcli-print-ft-names)
    * [tbl-head](#ftcli-print-tbl-head)
    * [tbl-os2](#ftcli-print-tbl-os2)
    
* [**utils**](#ftcli-utils)
  * [add-dsig](#ftcli-utils-add-dsig)
  * [add-features](#ftcli-utils-add-features)
  * [dehinter](#ftcli-utils-dehinter)
  * [del-table](#ftcli-utils-del-table)
  * [font-organizer](#ftcli-utils-font-organizer)
  * [font-renamer](#ftcli-utils-font-renamer)
  * [recalc-italic-bits](#ftcli-utils-recalc-italic-bits)
  * [remove-overlaps](#ftcli-utils-remove-overlaps)
  * [ttc-extractor](#ftcli-utils-ttc-extractor)


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

`ftcli metrics align "C:\Fonts" --output-dir "C:\Fonts\Aligned"`

`ftcli metrics copy -s "C:\Fonts\SourceFont.otf" -d "C:\Fonts\" --recalc-timestamp`

`ftcli metrics copy -s "C:\Fonts\SourceFont.otf" -d "C:\Fonts\" --no-overwrite`

## ftcli assistant

A set of tools to correctly compile the 'name' table and set proper values for usWeightClass, usWidthClass, bold, italic
and oblique bits.

![image](https://user-images.githubusercontent.com/83063506/226935693-519309a4-c76c-4321-8f1d-5bc0e7a32de5.png "ftCLI assistant main window")

The process creates a JSON configuration file and a CSV file that will be used to fix the fonts. Both files can be
automatically created and eventually edited manually or using the integrated command line editor. Once everything is
correctly set in the CSV file, the values inside it can be written to fonts.

### 1) The JSON configuration file.

The 'styles_mapping.json' file contains the desired style names to pair with each usWidthClass and usWeightClass values
of the family, as well as the desired italic and oblique literals:

    {
        "italics": ["It", "Italic"],
        
        "obliques": ["Obl", "Oblique"],
        
        "weights": {
            "250": ["Th", "Thin"],
            "275": ["ExLt", "ExtraLight"],
            ...
            "400": ["Rg", "Regular"],
            ...
            800: ["XBd", "ExtraBold"],
            900: ["Blk", "Black"]
        },
            
        "widths": {
            "1": ["Cm", "Compressed"],
            "2": ["ExCn", "ExtraCondensed"],
            ...
            "5": ["Nor", "Normal"],
            ...
            "8": ["ExExtd", "ExtraExtended"],
            "9": ["Exp", "Expanded"]
        }
    }

Unless you have previously created a configuration file and want to reuse it, you need to create a standard
configuration file and eventually customize it.

    ftcli assistant reset-cfg INPUT_PATH

The above command will create a file named 'styles_mapping.json' in the INPUT_PATH folder (or parent folder if
INPUT_PATH is a file).

Once created the configuration file, you may be in need to edit it according to your needs.

    ftcli assistant ui INPUT_PATH

Values contained in the configuration file will be used to fill the data.csv file in the next steps.

### 2) The CSV data file.

The final data.csv file will contain the desired style names, family name, italic and oblique bits, usWidthClass and
usWeightClass values. Once properly filled, the values contained in this file will be written to the fonts.

It contains 13 columns:

    file_name, family_name, is_bold, is_italic, is_oblique, uswidthclass, wdt, width, usweightclass, wgt, weight, slp,
    slope.

**family_name:** the column is filled reading nameID 16, or nameID 1 if 16 is not present.

**is_italic:** if OS/2.fsSelection bit 0 and head.macStyle bit 1 are set, the value is 1, otherwise 0.

**is_bold:** if OS/2.fsSelection bit 5 and head.macStyle bit 0 are set, the value is 1, otherwise 0.

This column is present only for completeness, but it's value will be ignored. A font will be set as bold only
and only if, while running the ftcli assistant recalc-names command, the user will choose to use linked styles
(-ls / --linked styles) option:

    ftcli assistant recalc-names "C:\Fonts" -ls 400 700

**wdt** and **width**: these columns contain the short and long literals for the width style names (for example: Cn;
Condensed).

**wgt** and **weight**: these columns contain the short and long literals for the weight style names (for example: Lt, Light).

**slp** and **slope**: these columns contain the short and long literals for the slope style names (for example: It,
Italic).

The user will choose the namerecords where to write long or short literals. For example:

    ftcli assistant recalc-names "C:\Fonts" -swdt 1 -swdt 4 -swdt 6 -swgt 1 -swgt 4 -swgt 6 -sslp 4 -sslp 6

The **fonts_data.csv** file can be created using the following command:

    ftcli assistant init-csv INPUT_PATH

At this point, the CSV file will contain a representation of the actual state of the fonts (the family_name column will
contain values of nameID 16, or nameID 1 if 16 is not present). It can be edited manually, using the 'ftcli assistant
edit-csv' command and also automatically recalculated using the 'ftcli assistant recalc-csv' command.

The 'ftcli assistant recalc-csv' command will recalculate style names, italic bits, width and weight style names
according to the values contained in the JSON configuration file.

When the 'data.csv' file contains the desired values, these values can be applied to fonts running the 'ftcli assistant
recalc-names' command (see 'ftcli assistant recalc-names --help' for more information).

### ftcli assistant edit-cfg
Command line editor for JSON configuration files.

**Usage:**

    ftcli  edit-cfg [OPTIONS] CONFIG_FILE

**Example:**

    ftcli assistant edit-cfg "C:\Fonts\config.json"

It is strongly recommended using this tool to edit the JSON configuration files. It prevents malformed JSON errors and
errors due to wrong values (for example, an out of range usWeightClass, or a string where's an integer is expected).

### ftcli assistant ui
Usage:

    ftcli assistant ui INPUT_PATH

Command line editor for 'fonts_data.csv' files.

This tool is not intended to replace a code editor for CSV files, but can help to make small edits without leaving the
command line. For complex projects, it's strongly recommended using a code editor like Visual Studio Code or even Excel.

### ftcli assistant init-cfg
Usage:

    ftcli assistant init-cfg [OPTIONS] INPUT_PATH
    
Creates a JSON configuration file containing the default values in the specified INPUT_PATH folder.

Options:

    -q, --quiet

Suppress overwrite confirmation message if the config.json file already exists.

### ftcli assistant init-csv
Usage:

    ftcli  init-csv [OPTIONS] INPUT_PATH

Creates or resets the CSV database file (data.csv).

Example 1:

    ftcli assistant init-csv "C:\Fonts\"

The above command will create the 'data.csv' file in C:\Fonts\ (and a configuration file with default values if it does
not exist).

Example 2:

    ftcli assistant init-csv "C:\Fonts\Font.otf"

The above command will create the 'data.csv' in the INPUT_PATH folder (or parent folder, if INPUT_PATH is a file).

data.csv file contains:

* the file names;
* the usWidthClass, usWeightClass, bold italic and oblique bits values of all font files found in INPUT_PATH;
* tries to guess the family name reading the name table. It also contains weight and widths literals, retrieved parsing
  the config.json file.

It can be edited manually or using the 'ftcli assistant edit-csv INPUT_PATH' command.

Options:

    -c, --config-file PATH

Use a custom configuration file instead of the default config.json file located in the same folder of INPUT_PATH.

    -q, --quiet

Suppress overwrite confirmation message if the data.csv and/or config.json files already exist.

### ftcli assistant recalc-csv
Usage:

    ftcli  recalc-csv [OPTIONS] INPUT_PATH

Recalculates the CSV database file (data.csv).

Options:

    -c, --config-file PATH

Use a custom configuration file instead of the default config.json file located in the same folder of INPUT_PATH.

    -f, --family-name TEXT

The desired family name. This string will be used to recalculate the CSV lines.

    -s, --source-string [fname|1_1_2|1_4|1_6|1_16_17|1_18|3_1_2|3_4|3_6|3_16_17|cff_1|cff_2]

The source string be used to recalculate the CSV lines can be the file name, a namerecord, a combination of namerecords
or values stored in the 'CFF' table.

For example, -s '1_1_2' will read a combination of namerecords 1 and 2 in the Mac table.  [default: fname]

    -q, --quiet

Suppress overwrite confirmation message if the data.csv file already exists.

#### ftcli assistant recalc-names
Usage:

    ftcli assistant recalc-names [OPTIONS] INPUT_PATH

Recalculates namerecords according to the values stored in the data.csv file.

Options:

    -c, --config-file PATH

Use a custom configuration file instead of the default config.json file located in the same folder of INPUT_PATH.

    -ls, --linked-styles <INTEGER RANGE INTEGER RANGE>

Use this option to activate linked styles. If this option is active, linked styles must be specified. For example:
-ls 400 700, or -ls 300 600.
  
    -ex, --exclude-namerecord [1|2|3|4|5|6|16|17|18]

Name IDs to skip. The specified name IDs won't be recalculated. This option can be repeated(example: -ex 3 -ex 5 ...).
    
    -swdt, --shorten-width [1|2|3|4|5|6|16|17|18]

Name IDs where to use the short word for width style name (example: 'Cond' instead of 'Condensed').This option can be
repeated (example: -swdt 3 -swdt 5 -swdt 6...).
    
    -swgt, --shorten-weight [1|2|3|4|5|6|16|17|18]
                                  
Name IDs where to use the short word for weight style name (example: 'Md' instead of 'Medium').This option can be
repeated (example: -swgt 3 -swgt 5 -swgt 6...).
  
    -sslp, --shorten-slope [1|2|3|4|5|6|16|17|18]

Name IDs where to use the short word for slope style name (example: 'It' instead of 'Italic').This option can be
repeated (example: -sslp 3 -sslp 5 -sslp 6...).

    -sf, --super-family

Superfamily mode. This option affects name IDs 3, 6, 16 and 17 in case of families with widths different from 'Normal'.
If this option is active, name ID 6 will be 'FamilyName-WidthWeightSlope' instead of 'FamilyNameWidth-WeightSlope'.
Mac and OT family/subfamily names will be FamilyName / Width Weight Slope' instead of 'Family Name Width / Weight Slope'.

    -aui, --alt-uid

Use alternate unique identifier. By default, nameID 3 (Unique identifier) is calculated according to the following
scheme: 'Version;Vendor code;PostscriptName'. The alternate unique identifier is calculated according to the following
scheme: 'Manufacturer:Full Font Name:Creation Year'

    -ri, --regular-italic
    
Keep '-Regular' in nameID 6.

    -kr, --keep-regular

Keep the 'Regular' word in all nameIDs

    -offn, --old-full-font-name

Full font name in Microsoft name table is generally a combination of name IDs 1 and 2 or 16 and 17.With this option
active, it will be equal to nameID 6 (PostScriptName).

    -cff, --fix-cff

fontNames, FullName, FamilyName and Weight values in the 'CFF' table will be recalculated.

    -obni, --oblique-not-italic

By default, if a font has the oblique bit set, the italic bits will be set too. Use this option to override the default
behaviour (for example, when the family has both italic and oblique styles, and you don't want to set only the oblique
bit). The italic bits will be cleared when the oblique bit is set.

    -o, --output-dir DIRECTORY

Specify the output directory where the output files are to be saved. If output_directory doesn't exist, will be created.
If not specified, files are saved to the same folder.

    --recalc-timestamp / --no-recalc-timestamp

Keep the original font 'modified' timestamp (head.modified) or set it to current time. By default, original timestamp
is kept.

    --overwrite / --no-overwrite

Overwrite existing output files or save them to a new file (numbers are appended at the end of filename). By default,
files are overwritten.

## ftcli cff

`CFF` table editor.

### ftcli cff find-replace

Finds a string in the following items of CFF table topDict and replaces it with a new string: `version`, `FullName`, 
`FamilyName`, `Weight`, `Copyright`, `Notice`.

```
Usage: ftcli cff find-replace [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli cff fix-version

Aligns topDict version string to the `head.fontRevision` value.

For example, if `head.fontRevision` value is 2.001, CFF topDict version value will
be 2.1.
```
Usage: ftcli cff fix-version [OPTIONS] INPUT_PATH

Options:
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
```

## ftcli converter

Font converter.

### ftcli converter ft2wf

Converts SFNT fonts (TTF or OTF) to web fonts (WOFF and WOFF2)

```
Usage: ftcli converter ft2wf [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli converter otf2ttf

Converts fonts from OTF to TTF format.

```
Usage: ftcli converter otf2ttf [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli converter ttc2sfnt

Extracts each font from a TTC file, and saves it as a TTF or OTF file.

```
Usage: ftcli converter ttc2sfnt [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli converter ttf2otf

Converts TTF fonts (or TrueType flavored woff/woff2 web fonts) to OTF fonts.
```
Usage: ftcli converter ttf2otf [OPTIONS] INPUT_PATH

Options:
  --no-optimize                 To convert the outlines from TrueType to CFF,
                                we use T2CharStringPen. This is not very
                                efficient, as the conversion ends up with a
                                CFF table containing charstrings that have
                                much more points than needed. To prevent this,
                                the script tries to get more simplified
                                charstrings using makeotf (default). Use
                                `--no-optimize` to change the default
                                behaviour.
  --purge-glyphs                Removes NULL and CR glyphs by subsetting the
                                font
  --check-outlines              Performs optional outline quality checks and
                                removes overlaps with afdko.checkoutlinesufo
  --autohint                    Auto hints the font with psautohint
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
```

### ftcli converter var2static

Exports static instances from variable fonts.

```
Usage: ftcli converter var2static [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli converter wf2ft

Converts web fonts (WOFF and WOFF2) to SFNT fonts (TTF or OTF)

```
Usage: ftcli converter wf2ft [OPTIONS] INPUT_PATH

Options:
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
```


## ftcli fix

A set of commands to detect and fix various errors.

### ftcli fix decompose-transformed

Decomposes composite glyphs that have transformed components.

fontbakery check id: com.google.fonts/check/transformed_components

```
Usage: ftcli fix decompose-transformed [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli fix duplicate-components

Removes duplicate components which have the same x,y coordinates.

fontbakery check id: com.google.fonts/check/glyf_non_transformed_duplicate_components

```
Usage: ftcli fix duplicate-components [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli fix italic-angle

Assuming that the italic bits are correctly set/clear, checks if the following values are properly set:

`[post].italicAngle`: **0.0**, if the font is upright, **calculated value** if the font is italic or oblique

`[hhea].caretSlopeRise`: **1** if the font is upright, `[head].unitsPerEm` if the font is italic or oblique

`[hhea].caretSlopeRun`: **0** if the font is upright, **calculated value** if the font is italic or oblique

`[hhea].caretOffset`: **0** if the font is upright, **leave unchanged** if the font is italic or oblique

`[CFF].cff.topDictIndex[0].ItalicAngle`: **0** if the font is upright, **calculated value** if the font is italic or
oblique (CFF fonts only)

The font is saved only if at least one of the above tables has changed.

```
Usage: ftcli fix italic-angle [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli fix kern-table

Some applications such as MS PowerPoint require kerning info on the kern table. More specifically, they require a
format 0 kern subtable from a kern table version 0 with only glyphs defined in the cmap table.

Given this, the command deletes all kerning pairs from kern v0 subtables where one of the two glyphs is not defined
in the cmap table.

fontbakery check id: com.google.fonts/check/kern_table

```
Usage: ftcli fix kern-table [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli fix missing-nbsp

Checks if the font has a non-breaking space character and, if it doesn't, adds one by double mapping 'space'.

```
Usage: ftcli fix missing-nbsp [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli fix nbsp-width

Checks if 'nbspace' and 'space' glyphs have the same width. If not, corrects 'nbspace' width to match 'space' width.

fontbakery check id: com.google.fonts/check/whitespace_widths

```
Usage: ftcli fix nbsp-width [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli fix os2-ranges

Generates a temporary Type 1 from the font file using tx, converts that to an OpenType font using makeotf, reads the
Unicode ranges and codepage ranges from the temporary OpenType font file, and then writes those ranges to the
original font's OS/2 table.

```
Usage: ftcli fix os2-ranges [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli fix strip-names

Removes leading and trailing spaces from all namerecords.

fontbakery check id: com.google.fonts/check/name/trailing_spaces

```
Usage: ftcli fix strip-names [OPTIONS] INPUT_PATH

Options:
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
```

## ftcli metrics

Vertical metrics tools.

```
Usage: ftcli metrics COMMAND [ARGS]...

Commands:
  align
  copy
  set-linegap
```

### ftcli metrics align
Aligns all fonts stored in INPUT_PATH folder to the same baseline.

To achieve this, the script finds the maximum ascender and the minimum descender values of the fonts stored in the
INPUT_PATH folder and applies those values to all fonts.

This can produce undesired effects (an exaggerated line height) when one or more fonts contain swashes, for example. In
such cases, it's better to copy the vertical metrics from a template font to one or more destination fonts using the
[`ftcli metrics copy`](#ftcli-metrics-copy) command.

See https://kltf.de/download/FontMetrics-kltf.pdf for more information.

```
Usage: ftcli metrics align [OPTIONS] INPUT_PATH

Options:
  -sil, --sil-method          Use SIL method:
                              https://silnrsi.github.io/FDBP/en-
                              US/Line_Metrics.html
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

```

### ftcli metrics copy
Copies vertical metrics from a source font to one or more destination fonts.

```
Usage: ftcli metrics copy [OPTIONS]

Options:
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
```

### ftcli metrics set-linegap
Modifies the line spacing metrics in one or more fonts.

This is a fork of font-line by Source Foundry: https://github.com/source-foundry/font-line

```
Usage: ftcli metrics set-linegap [OPTIONS] INPUT_PATH

Options:
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
```

## ftcli names
A set command line tools to manipulate `name` table entries.

    ftcli names [OPTIONS] COMMAND [ARGS]

```
Commands:
  add-prefix        Adds a prefix to the specified namerecords.
  add-suffix        Adds a suffix to the specified namerecords.
  clean-name-table  Deletes all namerecords from the `name` table.
  copy-names        Copies the `name` table from a source font to destination font.
  del-mac-names     Deletes all namerecords where platformID is equal to 1.
  del-names         Deletes the specified namerecord(s) from the name table.
  find-replace      Replaces a string in the `name` table and, optionally, in the `CFF` table.
  lang-help         Prints available languages that can be used with the `set-name` and `del-names` commands.
  name-from-txt     Reads a text file and writes its content into the specified namerecord in the `name` table.
  set-cff-names     Sets names in the CFF table.
  set-name          Writes the specified namerecord in the `name` table.
  win-2-mac         Copies all namerecords from Windows table to Macintosh table.
```

### ftcli names add-prefix
Adds a prefix to the specified namerecords.

    ftcli names add-prefix [OPTIONS] INPUT_PATH

```
Options:
  --prefix TEXT                The prefix string.  [required]
  -n, --name-id INTEGER RANGE  nameID where to add the prefix. This option can
                               be repeated multiple times (for example: -n 3
                               -n 5-n 6).  [0<=x<=32767; required]
  -p, --platform [win|mac]     platform [win, mac]. If no platform is
                               specified, the prefix will be added in both
                               tables.
  -o, --output-dir DIRECTORY   Specify the directory where output files are to
                               be saved. If output_dir doesn't exist, will be
                               created. If not specified, files are saved to
                               the same folder.
  --recalc-timestamp           Keep the original font 'modified' timestamp
                               (head.modified) or set it to current time. By
                               default, original timestamp is kept.
  --no-overwrite               Overwrite existing output files or save them to
                               a new file (numbers are appended at the end of
                               file name). By default, files are overwritten.
```

### ftcli names add-suffix
Adds a suffix to the specified namerecords.

    ftcli names add-suffix [OPTIONS] INPUT_PATH

```
Options:
  --suffix TEXT                The suffix string  [required]
  -n, --name-id INTEGER RANGE  nameID where to add the suffix. This option can
                               be repeated multiple times (for example: -n 3
                               -n 5 -n 6).  [0<=x<=32767; required]
  -p, --platform [win|mac]     platform [win, mac]. If no platform is
                               specified, the suffix will be added in both
                               tables.
  -o, --output-dir DIRECTORY   Specify the directory where output files are to
                               be saved. If output_dir doesn't exist, will be
                               created. If not specified, files are saved to
                               the same folder.
  --recalc-timestamp           Keep the original font 'modified' timestamp
                               (head.modified) or set it to current time. By
                               default, original timestamp is kept.
  --no-overwrite               Overwrite existing output files or save them to
                               a new file (numbers are appended at the end of
                               file name). By default, files are overwritten.
```

### ftcli names clean-name-table
Deletes all namerecords from the `name` table.

Use `-ex / --exclude-namerecord` (can be repeated multiple times) to preserve the specified namerecords.

    ftcli names clean-nametable [OPTIONS] INPUT_PATH

```
Options:
  -ex, --exclude-namerecord INTEGER
                                  NameIDs to skip. The specified nameIDs won't
                                  be deleted. This option can be repeated
                                  multiple times (for example: -ex 3 -ex 5 -ex
                                  6).
  -o, --output-dir DIRECTORY      Specify the directory where output files are
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
```

### ftcli names copy-names
Copies the `name` table from a source font to destination font.

    ftcli names copy-names [OPTIONS]

```
Options:
  -s, --source_font FILE      Path to the source font.  [required]
  -d, --dest_font FILE        Path to the destination font.  [required]
  -o, --output-dir DIRECTORY  Specify the directory where output files are to
                              be saved. If output_dir doesn't exist, will be
                              created. If not specified, files are saved to
                              the same folder.
  --recalc-timestamp          Keep the original font 'modified' timestamp
                              (head.modified) or set it to current time. By
                              default, original timestamp is kept.
  --no-overwrite              Overwrite existing output files or save them to
                              a new file (numbers are appended at the end of
                              file name). By default, files are overwritten.
```

### ftcli names del-mac-names
Deletes all namerecords where platformID is equal to 1.

According to Apple (https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html), _"names with
platformID 1 were required by earlier versions of macOS. Its use on modern platforms is discouraged. Use names with
platformID 3 instead for maximum compatibility. Some legacy software, however, may still require names with platformID
1, platformSpecificID 0"_.

Use the `-ex / --exclude-namerecord` option to prevent certain namerecords to be deleted:

    ftcli names del-mac-names INPUT_PATH -ex 1

The `-ex / --exclude-namerecord` option can be repeated to exclude from deletion more than one namerecord:

    ftcli names del-mac-names INPUT_PATH -ex 1 -ex 3 -ex 6

`INPUT_PATH` can be a single font file or a folder containing fonts.

    ftcli names del-mac-names [OPTIONS] INPUT_PATH

```
Options:
  -ex, --exclude-namerecord INTEGER RANGE
                                  NameIDs to ignore. The specified nameIDs
                                  won't be deleted. This option can be
                                  repeated multiple times (for example: -ex 3
                                  -ex 5 -ex 6).  [0<=x<=32767]
  -o, --output-dir DIRECTORY      Specify the directory where output files are
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
```

### ftcli names del-names
Deletes the specified namerecord(s) from the name table.

Use the `-l/--language` option to delete a namerecord in a language different from 'en'. Use `ftcli names lang-help` to
display available languages.

Use `-l ALL` to delete the name ID from all languages.

The `-n/--name-id` option can be repeated to delete multiple name records at once. For example:

    ftcli names del-names C:\Fonts -n 1 -n 2 -n 6

The above command will delete nameIDs 1, 2 and 6.

    ftcli names del-names [OPTIONS] INPUT_PATH

```
Options:
  -n, --name-id INTEGER       nameID (Integer)  [required]
  -p, --platform [win|mac]    platform [win, mac]. If no platform is
                              specified, the namerecord will be deleted from
                              both tables.
  -l, --language TEXT         Specify the name ID language (eg: 'de'), or use
                              'ALL' to delete the name ID from all languages.
                              [default: en]
  -o, --output-dir DIRECTORY  Specify the directory where output files are to
                              be saved. If output_dir doesn't exist, will be
                              created. If not specified, files are saved to
                              the same folder.
  --recalc-timestamp          Keep the original font 'modified' timestamp
                              (head.modified) or set it to current time. By
                              default, original timestamp is kept.
  --no-overwrite              Overwrite existing output files or save them to
                              a new file (numbers are appended at the end of
                              file name). By default, files are overwritten.
```

### ftcli names find-replace
Replaces a string in the name table with a new string.

If the `-cff` option is passed, the string will be replaced also in the `CFF` table:

    ftcli names find-replace MyFont-Black.otf --os "Black" --ns "Heavy" --cff

To simply remove a string, use an empty string as new string:

    ftcli names find-replace MyFont-Black.otf --os "RemoveMe" --ns ""

To replace the string in a specific platform ('win' or 'mac'):

    ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -p win

To replace the string in a specific namerecord:

    ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -n 6

The `-p / --platform` and `-n / --name-id` options can be combined:

    ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -p win
    -n 6

To exclude one or more namerecords, use the `-ex / --exclude-namerecord` option:

    ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -ex 1 -ex 6

If a namerecord is explicitly included but also explicitly excluded, it won't be changed:

    ftcli names find-replace MyFont-Black.otf -os "Black" -ns "Heavy" -n 1 -ex 1 -ex 6

The above command will replace the string only in nameID 6 in both platforms.

    ftcli names find-replace [OPTIONS] INPUT_PATH

```
Options:
  -os, --old-string TEXT          old string  [required]
  -ns, --new-string TEXT          new string  [required]
  -n, --name-id INTEGER RANGE     nameID (Integer between 0 and 32767). If not
                                  specified, the string will be replaced in
                                  allnamerecords.  [0<=x<=32767]
  -p, --platform [win|mac]        platform [win, mac]. If no platform is
                                  specified, the string will be replaced in
                                  both tables.
  -cff, --fix-cff                 Replaces the string in the CFF table.
  -ex, --exclude-namerecord INTEGER RANGE
                                  NameIDs to ignore. The specified nameIDs
                                  won't be changed. This option can be
                                  repeated multiple times (for example: -ex 3
                                  -ex 5 -ex 6).  [0<=x<=32767]
  -o, --output-dir DIRECTORY      Specify the directory where output files are
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
```

### ftcli names lang-help
Prints available languages that can be used with the `set-name` and `del-names` commands.

    ftcli names lang-help

The command will produce the following output:
```
[WINDOWS LANGUAGES]
['aeb', 'af', 'am', 'ar', 'ar-AE', 'ar-BH', 'ar-DZ', 'ar-IQ', 'ar-JO', 'ar-KW', 'ar-LB', 'ar-LY', 'ar-OM', 'ar-QA',
'ar-SA', 'ar-SY', 'ar-YE', 'arn', 'ary', 'as', 'az', 'az-Cyrl', 'ba', 'be', 'bg', 'bn', 'bn-IN', 'bo', 'br', 'bs',
'bs-Cyrl', 'ca', 'co', 'cs', 'cy', 'da', 'de', 'de-AT', 'de-CH', 'de-LI', 'de-LU', 'dsb', 'dv', 'el', 'en', 'en-029',
'en-AU', 'en-BZ', 'en-CA', 'en-GB', 'en-IE', 'en-IN', 'en-JM', 'en-MY', 'en-NZ', 'en-PH', 'en-SG', 'en-TT', 'en-ZA',
'en-ZW', 'es', 'es', 'es-AR', 'es-BO', 'es-CL', 'es-CO', 'es-CR', 'es-DO', 'es-EC', 'es-GT', 'es-HN', 'es-MX', 'es-NI',
'es-PA', 'es-PE', 'es-PR', 'es-PY', 'es-SV', 'es-US', 'es-UY', 'es-VE', 'et', 'eu', 'fi', 'fil', 'fo', 'fr', 'fr-BE',
'fr-CA', 'fr-CH', 'fr-LU', 'fr-MC', 'fy', 'ga', 'gl', 'gsw', 'gu', 'ha', 'he', 'hi', 'hr', 'hr-BA', 'hsb', 'hu', 'hy',
'id', 'ig', 'ii', 'is', 'it', 'it-CH', 'iu', 'iu-Latn', 'ja', 'ka', 'kk', 'kl', 'km', 'kn', 'ko', 'kok', 'ky', 'lb',
'lo', 'lt', 'lv', 'mi', 'mk', 'ml', 'mn', 'mn-CN', 'moh', 'mr', 'ms', 'ms-BN', 'mt', 'nb', 'ne', 'nl', 'nl-BE', 'nn',
'nso', 'oc', 'or', 'pa', 'pl', 'prs', 'ps', 'pt', 'pt-PT', 'qu', 'qu-BO', 'qu-EC', 'quc', 'rm', 'ro', 'ru', 'rw', 'sa',
'sah', 'se', 'se-FI', 'se-SE', 'si', 'sk', 'sl', 'sma-NO', 'smj', 'smj-NO', 'smn', 'sms', 'sms', 'sq', 'sr',
'sr-Cyrl-BA', 'sr-Latn', 'sr-Latn-BA', 'sv', 'sv-FI', 'sw', 'syr', 'ta', 'te', 'tg', 'th', 'tk', 'tn', 'tr', 'tt',
'tzm', 'ug', 'uk', 'ur', 'uz', 'uz-Cyrl', 'vi', 'wo', 'xh', 'yo', 'zh', 'zh-HK', 'zh-MO', 'zh-SG', 'zh-TW', 'zu']

[MAC LANGUAGES]
['af', 'am', 'ar', 'as', 'ay', 'az', 'az-Arab', 'az-Cyrl', 'be', 'bg', 'bn', 'bo', 'br', 'ca', 'cy', 'cz', 'da', 'de',
'dz', 'el', 'el-polyton', 'en', 'eo', 'es', 'es', 'eu', 'fa', 'fi', 'fo', 'fr', 'ga', 'ga', 'gd', 'gl', 'gn', 'gu',
'gv', 'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'iu', 'ja', 'jv', 'ka', 'kk', 'kl', 'km', 'kn', 'ko', 'ks', 'ku',
'ky', 'la', 'lo', 'lt', 'lv', 'mg', 'mk', 'ml', 'mn', 'mn-CN', 'mo', 'mr', 'ms', 'ms-Arab', 'mt', 'my', 'ne', 'nl',
'nl-BE', 'nn', 'no', 'ny', 'om', 'or', 'pa', 'pl', 'ps', 'pt', 'qu', 'rn', 'ro', 'ru', 'rw', 'sa', 'sd', 'se', 'si',
'sk', 'sl', 'so', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'to', 'tr', 'tt', 'ug', 'uk',
'ur', 'uz', 'vi', 'yi', 'zh', 'zh-Hant']
```

### ftcli names name-from-txt
Reads a text file and writes its content into the specified namerecord in the name table.

If the namerecord is not present, it will be created. If it already exists, will be overwritten.

If `name_id` parameter is not specified, the first available nameID will be used.

By default, the namerecord will be written both in platformID 1 (Macintosh) and platformID 3 (Windows) tables. Use 
`-p/--platform-id [win|mac]` option to write the namerecord only in the specified platform.

Use the `-l/--language` option to write the namerecord in a language different from 'en'. Use 
[`ftcli names langhelp`](#ftcli-names-lang-help) to display available languages.

    ftcli names name-from-txt [OPTIONS] INPUT_PATH

```
Options:
  -n, --name-id INTEGER RANGE  nameID (Integer between 0 and 32767)
                               [0<=x<=32767]
  -p, --platform [win|mac]     platform [win, mac]. If it's not specified,
                               name will be written in both tables.
  -l, --language TEXT          language  [default: en]
  -i, --input-file PATH        Path to the text file to read.  [required]
  -o, --output-dir DIRECTORY   Specify the directory where output files are to
                               be saved. If output_dir doesn't exist, will be
                               created. If not specified, files are saved to
                               the same folder.
  --recalc-timestamp           Keep the original font 'modified' timestamp
                               (head.modified) or set it to current time. By
                               default, original timestamp is kept.
  --no-overwrite               Overwrite existing output files or save them to
                               a new file (numbers are appended at the end of
                               file name). By default, files are overwritten.
  --help                       Show this message and exit.
```

### ftcli names set-cff-names
Set names in the CFF table.

    ftcli names set-cff-names [OPTIONS] INPUT_PATH

```
Options:
  --font-name TEXT            Sets the CFF font name.
  --full-name TEXT            Sets the CFF full name.
  --family-name TEXT          Sets the CFF family name.
  --weight TEXT               Sets the CFF weight.
  --copyright TEXT            Sets the CFF copyright.
  --notice TEXT               Sets the CFF notice.
  -o, --output-dir DIRECTORY  Specify the directory where output files are to
                              be saved. If output_dir doesn't exist, will be
                              created. If not specified, files are saved to
                              the same folder.
  --recalc-timestamp          Keep the original font 'modified' timestamp
                              (head.modified) or set it to current time. By
                              default, original timestamp is kept.
  --no-overwrite              Overwrite existing output files or save them to
                              a new file (numbers are appended at the end of
                              file name). By default, files are overwritten.
```

### ftcli names set-name
Writes the specified namerecord in the `name` table.

If the namerecord is not present, it will be created. If it already exists, will be overwritten.

If `name_id` parameter is not specified, the first available nameID will be used.

By default, the namerecord will be written both in platformID 1 (Macintosh)and platformID 3 (Windows) tables. Use the
`-p/--platform-id [win|mac]` option to write the namerecord only in the specified platform.

Use the `-l/--language` option to write the namerecord in a language different from 'en'. Use 
[`ftcli names langhelp`](#ftcli-names-lang-help) to display available languages.

    ftcli names set-name [OPTIONS] INPUT_PATH

```
Options:
  -n, --name-id INTEGER RANGE  nameID (Integer between 0 and 32767)
                               [0<=x<=32767]
  -p, --platform [win|mac]     platform [win, mac]. If it's not specified,
                               name will be written in both tables.
  -l, --language TEXT          language  [default: en]
  -s, --string TEXT            string  [required]
  -o, --output-dir DIRECTORY   Specify the directory where output files are to
                               be saved. If output_dir doesn't exist, will be
                               created. If not specified, files are saved to
                               the same folder.
  --recalc-timestamp           Keep the original font 'modified' timestamp
                               (head.modified) or set it to current time. By
                               default, original timestamp is kept.
  --no-overwrite               Overwrite existing output files or save them to
                               a new file (numbers are appended at the end of
                               file name). By default, files are overwritten.
```

### ftcli names win-2-mac
Copies all namerecords from Windows table to Macintosh table.

    ftcli names win-2-mac [OPTIONS] INPUT_PATH

```
Options:
  -o, --output-dir DIRECTORY  Specify the directory where output files are to
                              be saved. If output_dir doesn't exist, will be
                              created. If not specified, files are saved to
                              the same folder.
  --recalc-timestamp          Keep the original font 'modified' timestamp
                              (head.modified) or set it to current time. By
                              default, original timestamp is kept.
  --no-overwrite              Overwrite existing output files or save them to
                              a new file (numbers are appended at the end of
                              file name). By default, files are overwritten.
```

## ftcli os2
Command line `OS/2` table editor.

```
Usage: ftcli os2 [OPTIONS] INPUT_PATH

Options:
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
  --recalc-us-max-context         Recalculates `usMaxContext` value.
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
```

## ftcli print
Prints various font's information.

### ftcli print ft-info
Prints detailed font information.

```
Usage: ftcli print ft-info [OPTIONS] INPUT_PATH

Options:
  --help  Show this message and exit.
```
**Usage example**

    ftcli print ft-info IBMPlexMono-Bold.otf

Prints the following output:

```
CURRENT FILE: D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono\IBMPlexMono-Bold.otf

-------------------------------------------------------------------------------------------------------
  BASIC INFORMATION
-------------------------------------------------------------------------------------------------------
  Flavor            : PostScript
  Glyphs number     : 1031
  Date created      : Fri Aug 13 10:46:23 2021
  Date modified     : Fri Aug 13 08:46:27 2021
  Version           : 2.003
  Vendor code       : IBM
  Unique identifier : 2.3;IBM ;IBMPlexMono-Bold
  usWidthClass      : 5
  usWeightClass     : 700
  Font is bold      : True
  Font is italic    : False
  Font is oblique   : False
  WWS consistent    : True
  Italic angle      : 0.0
  Embedding         : 0 (Installable embedding)

-------------------------------------------------------------------------------------------------------
  FONT METRICS
-------------------------------------------------------------------------------------------------------

  [OS/2]
    sTypoAscender   : 780
    sTypoDescender  : -220
    sTypoLineGap    : 300
    usWinAscent     : 1025
    usWinDescent    : 275

  [hhea]
    ascent          : 1025
    descent         : -275
    lineGap         : 0

  [head]
    unitsPerEm      : 1000
    xMin            : -307
    yMin            : -350
    xMax            : 637
    yMax            : 1150
    Font BBox       : (-307, -350) (637, 1150)

-------------------------------------------------------------------------------------------------------
  FONT TABLES: 15
-------------------------------------------------------------------------------------------------------
  GlyphOrder, head, hhea, maxp, OS/2, name, cmap, post, CFF, GDEF, GPOS, GSUB, hmtx, meta, DSIG

-------------------------------------------------------------------------------------------------------
  FONT FEATURES: 16
-------------------------------------------------------------------------------------------------------
  aalt, ccmp, dnom, frac, numr, ordn, salt, sinf, ss01, ss02, ss03, ss04, ss05, sups, zero, mark
-------------------------------------------------------------------------------------------------------
```

### ftcli print ft-list
Prints a list of fonts with basic information.
```
Usage: ftcli print ft-list [OPTIONS] INPUT_PATH

Options:
  --help  Show this message and exit.
```

**Usage example**

    ftcli print ft-list "D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono"

Prints the following output

```
+----------------------------------+--------------+---------------+--------+----------+-----------+
| File Name                        | usWidthClass | usWeightClass | isBold | isItalic | isOblique |
+----------------------------------+--------------+---------------+--------+----------+-----------+
| IBMPlexMono-Bold.otf             |            5 |           700 |      1 |        0 |         0 |
| IBMPlexMono-BoldItalic.otf       |            5 |           700 |      1 |        1 |         0 |
| IBMPlexMono-ExtraLight.otf       |            5 |           200 |      0 |        0 |         0 |
| IBMPlexMono-ExtraLightItalic.otf |            5 |           200 |      0 |        1 |         0 |
| IBMPlexMono-Italic.otf           |            5 |           400 |      0 |        1 |         0 |
| IBMPlexMono-Light.otf            |            5 |           300 |      0 |        0 |         0 |
| IBMPlexMono-LightItalic.otf      |            5 |           300 |      0 |        1 |         0 |
| IBMPlexMono-Medium.otf           |            5 |           500 |      0 |        0 |         0 |
| IBMPlexMono-MediumItalic.otf     |            5 |           500 |      0 |        1 |         0 |
| IBMPlexMono-Regular.otf          |            5 |           400 |      0 |        0 |         0 |
| IBMPlexMono-SemiBold.otf         |            5 |           600 |      0 |        0 |         0 |
| IBMPlexMono-SemiBoldItalic.otf   |            5 |           600 |      0 |        1 |         0 |
| IBMPlexMono-Text.otf             |            5 |           450 |      0 |        0 |         0 |
| IBMPlexMono-TextItalic.otf       |            5 |           450 |      0 |        1 |         0 |
| IBMPlexMono-Thin.otf             |            5 |           100 |      0 |        0 |         0 |
| IBMPlexMono-ThinItalic.otf       |            5 |           100 |      0 |        1 |         0 |
+----------------------------------+--------------+---------------+--------+----------+-----------+

 Widths  : 5
 Weights : 100, 200, 300, 400, 450, 500, 600, 700
```

### ftcli print ft-name
Prints a single namerecord.
```
Use the -ml, --max-lines option to limit the printed line numbers to the
desired value.

Usage: ftcli print ft-name [OPTIONS] INPUT_PATH

Options:
  -n, --name-id INTEGER RANGE  nameID (Integer between 0 and 32767)
                               [0<=x<=32767; required]
  -ml, --max-lines INTEGER     Maximum number of lines to be printed.
  --help                       Show this message and exit.
```

**Usage example**

    ftcli print ft-name -n 6 "D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono"

Prints the following output:

```
------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-Bold.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-Bold
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-Bold

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-BoldItalic.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-BoldItalic
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-BoldItalic

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-ExtraLight.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-ExtLt
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-ExtLt

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-ExtraLightItalic.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-ExtLtItalic
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-ExtLtItalic

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-Italic.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-Italic
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-Italic

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-Light.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-Light
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-Light

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-LightItalic.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-LightItalic
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-LightItalic

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-Medium.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-Medm
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-Medm

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-MediumItalic.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-MedmItalic
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-MedmItalic

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-Regular.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono
platform: (3, 1, 1033),  nameID6 : IBMPlexMono

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-SemiBold.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-SmBld
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-SmBld

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-SemiBoldItalic.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-SmBldItalic
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-SmBldItalic

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-Text.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-Text
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-Text

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-TextItalic.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-TextItalic
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-TextItalic

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-Thin.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-Thin
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-Thin

------------------------------------------------------------------------------------------
FILE NAME: IBMPlexMono-ThinItalic.otf
------------------------------------------------------------------------------------------
platform: (1, 0, 0),  nameID6 : IBMPlexMono-ThinItalic
platform: (3, 1, 1033),  nameID6 : IBMPlexMono-ThinItalic
```

### ftcli print ft-names
Prints the `name` table and `CFF` names (if present).

Use the `-ml / --max-lines` option to limit the printed line numbers, and the `-min / --minimal` one to print a minimal
set of namerecords.

```
Usage: ftcli print ft-names [OPTIONS] INPUT_PATH

Options:
  -ml, --max-lines INTEGER  Maximum number of lines to be printed for each
                            namerecord
  -min, --minimal           Prints only nameIDs 1, 2, 3, 4, 5, 6, 16, 17, 18,
                            21 and 22.
  --help                    Show this message and exit.
```

**Usage example**

    ftcli print ft-names "D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono\IBMPlexMono-ExtraLightItalic.otf"

Prints the following output:

```
CURRENT FILE: D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono\IBMPlexMono-ExtraLightItalic.otf

-------------------------------------------------------------------------------------------------------
 NAME TABLE
-------------------------------------------------------------------------------------------------------
 platformID: 1 (Macintosh) | platEncID: 0 (Roman) | langID: 0 (en)
-------------------------------------------------------------------------------------------------------
    0 : Copyright Notice       : Copyright 2017 IBM Corp. All rights reserved.
    1 : Family name            : IBM Plex Mono ExtLt
    2 : Subfamily name         : Italic
    3 : Unique identifier      : 2.3;IBM ;IBMPlexMono-ExtLtItalic
    4 : Full font name         : IBM Plex Mono ExtLt Italic
    5 : Version string         : Version 2.3
    6 : PostScript name        : IBMPlexMono-ExtLtItalic
    7 : Trademark              : IBM Plex® is a trademark of IBM Corp, registered in many jurisdictions
                                 worldwide.
    8 : Manufacturer Name      : Bold Monday
    9 : Designer               : Mike Abbink, Paul van der Laan, Pieter van Rosmalen
   11 : URL Vendor             : http://www.boldmonday.com
   12 : URL Designer           : http://www.ibm.com
   13 : License Description    : This Font Software is licensed under the SIL Open Font License,
                                 Version 1.1. This license is available with a FAQ at:
                                 http://scripts.sil.org/OFL
   14 : License Info URL       : http://scripts.sil.org/OFL
   16 : Typographic Family     : IBM Plex Mono
   17 : Typographic Subfamily  : ExtraLight Italic
  256 : 256                    : alternate lowercase a
  257 : 257                    : simple lowercase g
  258 : 258                    : slashed number zero
  259 : 259                    : plain number zero
  260 : 260                    : alternate lowercase eszett
-------------------------------------------------------------------------------------------------------
 platformID: 3 (Windows) | platEncID: 1 (Unicode) | langID: 1033 (en)
-------------------------------------------------------------------------------------------------------
    0 : Copyright Notice       : Copyright 2017 IBM Corp. All rights reserved.
    1 : Family name            : IBM Plex Mono ExtLt
    2 : Subfamily name         : Italic
    3 : Unique identifier      : 2.3;IBM ;IBMPlexMono-ExtLtItalic
    4 : Full font name         : IBM Plex Mono ExtLt Italic
    5 : Version string         : Version 2.3
    6 : PostScript name        : IBMPlexMono-ExtLtItalic
    7 : Trademark              : IBM Plex® is a trademark of IBM Corp, registered in many jurisdictions
                                 worldwide.
    8 : Manufacturer Name      : Bold Monday
    9 : Designer               : Mike Abbink, Paul van der Laan, Pieter van Rosmalen
   11 : URL Vendor             : http://www.boldmonday.com
   12 : URL Designer           : http://www.ibm.com
   13 : License Description    : This Font Software is licensed under the SIL Open Font License,
                                 Version 1.1. This license is available with a FAQ at:
                                 http://scripts.sil.org/OFL
   14 : License Info URL       : http://scripts.sil.org/OFL
   16 : Typographic Family     : IBM Plex Mono
   17 : Typographic Subfamily  : ExtraLight Italic
   19 : Sample text            : How razorback-jumping frogs can level six piqued gymnasts!
  256 : 256                    : alternate lowercase a
  257 : 257                    : simple lowercase g
  258 : 258                    : slashed number zero
  259 : 259                    : plain number zero
  260 : 260                    : alternate lowercase eszett
-------------------------------------------------------------------------------------------------------
 CFF NAMES
-------------------------------------------------------------------------------------------------------
 fontNames                    : ['IBMPlexMono-ExtLtItalic']
 version                      : 2.3
 Notice                       : We are all, by any practical definition of the words, foolproof and
                                 incapable of error.
 Copyright                    : Copyright 2017 IBM Corp. All rights reserved.
 FullName                     : IBM Plex Mono ExtLt Italic
 FamilyName                   : IBM Plex Mono
 Weight                       : ExtraLight
-------------------------------------------------------------------------------------------------------
```

### ftcli print tbl-head
Prints the 'head' table.

```
Usage: ftcli print tbl-head [OPTIONS] INPUT_PATH

Options:
  --help  Show this message and exit.
```

**Usage example**

    ftcli print tbl-head "D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono\IBMPlexMono-BoldItalic.otf"

Prints the following output:

```
CURRENT FILE: D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono\IBMPlexMono-BoldItalic.otf
-------------------------------------------------------------------------------------------------------
tableTag head
-------------------------------------------------------------------------------------------------------

    <tableVersion value="1.0"/>
    <fontRevision value="2.00299072265625"/>
    <checkSumAdjustment value="0xd80c0ca4"/>
    <magicNumber value="0x5f0f3cf5"/>
    <flags value="3"/>
    <unitsPerEm value="1000"/>
    <created value="Fri Aug 13 10:46:23 2021"/>
    <modified value="Fri Aug 13 08:46:27 2021"/>
    <xMin value="-256"/>
    <yMin value="-350"/>
    <xMax value="713"/>
    <yMax value="1149"/>
    <macStyle value="3"/>
    <lowestRecPPEM value="3"/>
    <fontDirectionHint value="2"/>
    <indexToLocFormat value="0"/>
    <glyphDataFormat value="0"/>

-------------------------------------------------------------------------------------------------------
```

### ftcli print tbl-os2
Prints the 'OS/2' table.

```
Usage: ftcli print tbl-os2 [OPTIONS] INPUT_PATH

Options:
  --help  Show this message and exit.
```

**Usage example**

    ftcli print tbl-os2 "D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono\IBMPlexMono-BoldItalic.otf"

Prints the following output:

```
CURRENT FILE: D:\Fonts\IBM Plex\OpenType\IBM-Plex-Mono\IBMPlexMono-BoldItalic.otf
-------------------------------------------------------------------------------------------------------
tableTag OS/2
-------------------------------------------------------------------------------------------------------

    <version value="4"/>
    <xAvgCharWidth value="600"/>
    <usWeightClass value="700"/>
    <usWidthClass value="5"/>
    <fsType value="00000000 00000000"/>
    <ySubscriptXSize value="650"/>
    <ySubscriptYSize value="600"/>
    <ySubscriptXOffset value="-13"/>
    <ySubscriptYOffset value="75"/>
    <ySuperscriptXSize value="650"/>
    <ySuperscriptYSize value="600"/>
    <ySuperscriptXOffset value="59"/>
    <ySuperscriptYOffset value="350"/>
    <yStrikeoutSize value="100"/>
    <yStrikeoutPosition value="309"/>
    <sFamilyClass value="2057"/>
    <panose>
        <bFamilyType value="2"/>
        <bSerifStyle value="11"/>
        <bWeight value="8"/>
        <bProportion value="9"/>
        <bContrast value="5"/>
        <bStrokeVariation value="2"/>
        <bArmStyle value="3"/>
        <bLetterForm value="0"/>
        <bMidline value="2"/>
        <bXHeight value="3"/>
    </panose>
    <ulUnicodeRange1 value="10100000 00000000 00000010 01101111"/>
    <ulUnicodeRange2 value="01000000 00000000 00111000 00111011"/>
    <ulUnicodeRange3 value="00000000 00000000 00000000 00000000"/>
    <ulUnicodeRange4 value="00000000 00000000 00000000 00000000"/>
    <achVendID value="IBM "/>
    <fsSelection value="00000001 00100001"/>
    <usFirstCharIndex value="32"/>
    <usLastCharIndex value="64258"/>
    <sTypoAscender value="780"/>
    <sTypoDescender value="-220"/>
    <sTypoLineGap value="300"/>
    <usWinAscent value="1025"/>
    <usWinDescent value="275"/>
    <ulCodePageRange1 value="01100000 00000000 00000001 10010111"/>
    <ulCodePageRange2 value="00000000 00000000 00000000 00000000"/>
    <sxHeight value="516"/>
    <sCapHeight value="698"/>
    <usDefaultChar value="0"/>
    <usBreakChar value="32"/>
    <usMaxContext value="3"/>

-------------------------------------------------------------------------------------------------------
```

## ftcli utils
Miscellaneous utilities.

### ftcli utils add-dsig
Adds a dummy DSIG to the font, if it's not present.

```
Usage: ftcli utils add-dsig [OPTIONS] INPUT_PATH

Options:
  -o, --output-dir DIRECTORY  The output directory where the output files are
                              to be created. If it doesn't exist, will be
                         add_dsig     created. If not specified, files are saved to
                              the same folder.
  --recalc-timestamp          By default, original head.modified value is kept
                              when a font is saved. Use this switch to set
                              head.modified timestamp to current time.
  --no-overwrite              By default, modified files are overwritten. Use
                              this switch to save them to a new file (numbers
                              are appended at the end of file name).
  --help                      Show this message and exit.
```

### ftcli utils add-features
Import features form a fea file.

```
Usage: ftcli utils add-features [OPTIONS] INPUT_PATH

Options:
  -fea, --feature-file FILE       Path to the feature file.  [required]
  -t, --tables [BASE|GDEF|GPOS|GSUB|OS/2|head|hhea|name|vhea|STAT]
                                  Specify the table(s) to be built.
  -o, --output-dir DIRECTORY      The output directory where the output files
                                  are to be created. If it doesn't exist, will
                                  be created. If not specified, files are
                                  saved to the same folder.
  --recalc-timestamp              By default, original head.modified value is
                                  kept when a font is saved. Use this switch
                                  to set head.modified timestamp to current
                                  time.
  --no-overwrite                  By default, modified files are overwritten.
                                  Use this switch to save them to a new file
                                  (numbers are appended at the end of file
                                  name).
  --help                          Show this message and exit.
```

### ftcli utils dehinter
Drops hinting from all glyphs.

Currently, this only works with TrueType fonts with 'glyf' table.

This is a CLI for [dehinter](https://github.com/source-foundry/dehinter) by Source Foundry.

```
Usage: ftcli utils dehinter [OPTIONS] INPUT_PATH

Options:
  --keep-cvar                 keep cvar table
  --keep-cvt                  keep cvt table
  --keep-fpgm                 keep fpgm table
  --keep-hdmx                 keep hdmx table
  --keep-ltsh                 keep LTSH table
  --keep-prep                 keep prep table
  --keep-ttfa                 keep ttfa table
  --keep-vdmx                 keep vdmx table
  --keep-glyf                 do not modify glyf table
  --keep-gasp                 do not modify gasp table
  --keep-maxp                 do not modify maxp table
  --keep-head                 do not modify head table
  --verbose                   display standard output
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
```

### ftcli utils del-table
Deletes the specified table from the font.

```
Usage: ftcli utils del-table [OPTIONS] INPUT_PATH

Options:
  -t, --table TEXT                [required]
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
```

### ftcli utils font-organizer
Renames font files according to PostScript name and sorts them by foundry  and family names.

```
Usage: ftcli utils font-organizer [OPTIONS] INPUT_PATH

  Usage: ftcli utils font-organizer INPUT_PATH

  INPUT_PATH can be a single font file or a directory containing fonts
  (subdirectories are not processed by choice).

  Fonts are renamed according to PostScript name ('name' table nameID 6) and
  sorted by Manufacturer Name (nameID 8). If nameID 8 is not present, the
  script will try to read nameID 9 (Designer) and if also name ID 9 is not
  present, the 4 characters achVendID stored in 'OS/2' table is used.

  Family name is read from nameID 16, or nameID 1 where nameID 16 is not
  present.

  If two files have identical foundry name, family name and PostScript name, a
  suffix with a number (#1, #2, etc.) is added at the end of filename to avoid
  overwriting an existing file.
```

### ftcli utils font-renamer
Renames font files according to the provided source string.

```
Usage: ftcli utils font-renamer [OPTIONS] INPUT_PATH

Options:
  -s, --source-string [1_1_2|1_4|1_6|1_16_17|1_18|3_1_2|3_4|3_6|3_16_17|cff_1|cff_2]
                                  The source string is read from a namerecord
                                  or from a combination of two namerecords,
                                  and the font file is renamed according to
                                  it.

                                  The first number in the sequence is the
                                  platformID, while the following numbers
                                  represent the nameID(s) numbers.

                                  For example:

                                  -s 1_1_2: reads the strings contained in
                                  PlatformID 1 (Macintosh) nameID 1 and nameID
                                  2 values and concatenates them.

                                  -s 3_6: reads the platformID 3 (Windows)
                                  nameID 6 (PostScript name).

                                  If the font is CFF flavored, the cff_1 or
                                  cff_2 options can be used.
  --help                          Show this message and exit.
```

### ftcli utils recalc-italic-bits
Sets or clears the italic bits according to the `italicAngle` value in `post` table.

If the `italicAngle` value is 0.0, the italic bits are cleared. If the value is not 0.0, the italic bits are set.

```
Usage: ftcli utils recalc-italic-bits [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli utils remove-overlaps
Simplify glyphs in TTFont by merging overlapping contours.

Overlapping components are first decomposed to simple contours, then merged.

Currently, this only works with TrueType fonts with 'glyf' table.

Note that removing overlaps invalidates the hinting. Hinting is dropped from all glyphs whether overlaps are
removed from a given one, as it would look weird if only some glyphs are left (un)hinted.

```
Usage: ftcli utils remove-overlaps [OPTIONS] INPUT_PATH

Options:
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
```

### ftcli utils ttc-extractor
Extracts .ttc fonts to otf/ttf fonts.

```
Usage: ftcli utils ttc-extractor [OPTIONS] INPUT_PATH

Options:
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
```

**To Sergiev. May you rest in peace.**
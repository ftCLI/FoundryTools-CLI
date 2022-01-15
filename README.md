# ftCLI

ftCLI is a command line interface built with [click](https://click.palletsprojects.com/en/8.0.x/) to edit fonts using [FontTools](https://github.com/fonttools/fonttools).

Python 3.8 or later is required to install ftCLI.

The following packages will be installed during setup:

* fonttools
* click
* colorama
* dehinter
* font-line
* brotli
* skia-pathops
* zopfli
 
## Installation
    pip install -e .
 
## Commands list
* assistant
  * edit-cfg
  * edit-csv
  * init-cfg
  * init-csv
  * recalc-csv
  * recalc-names


* metrics
    * align
    * copy
    * set-linegap


* names
    * del-mac-names
    * del-name
    * win-2-mac
    * find-replaceace
    * lang-help
    * set-name
    * set-cff-name


* os2


* print
    * ft-info
    * ft-list
    * ft-name
    * ft-names
    * tbl-head
    * tbl-os2


* utils
  * add-dsig
  * font-renamer
  * remove-hinting
  * remove-overlaps
  * ttc-extractor


* webfonts
    * compress
    * decompress
    * makecss


### assistant
A set of tools to correctly compile the name table and set proper values for usWeightClass, usWidthClass, bold, italic
and oblique bits.

The process creates a JSON configuration file and a CSV file that will be used to fix the fonts. Both files can be
automatically created and eventually edited manually or using the integrated command line editor. Once everything is
correctly set in the CSV file, the values inside it can be written to fonts.

#### 1) The JSON configuration file.

The 'config.json' file contains the desired style names to pair with each usWidthClass and usWeightClass values of the
family, as well as the desired italic and oblique literals:

    {
        "italics": ["It", "Italic"],
        
        "obliques": ["Obl", "Oblique"],
        
        "weights": {
            "250": ["Th", "Thin"],
            "275": ["ExLt", "ExtraLight"],
            ...
        },
            
        "widths": {
            "1": ["Cm", "Compressed"],
            "2": ["ExCn", "ExtraCondensed"],
            ...
        }
    }

Unless you have previously created a configuration file and want to reuse it, you need to create a standard
configuration file and eventually customize it.

    ftcli assistant init-cfg INPUT_PATH

The above command will create a file named 'config.json' in the INPUT_PATH folder (or parent folder if INPUT_PATH is a
file).

Once created the configuration file, you may be in need to edit it according to your needs.

    ftcli assistant edit-cfg CONFIG_FILE

Values contained in the configuration file will be used to fill the data.csv file in the next steps.

#### 2) The CSV data file.

The final data.csv file will contain the desired style names, family name, italic and oblique bits, usWidthClass and
usWeightClass values. Once properly filled, the values contained in this file will be written to the fonts.

It contains 13 columns:

file_name, family_name, is_bold, is_italic, is_oblique, uswidthclass, wdt, width, usweightclass, wgt, weight, slp,
slope.

The 'is_bold' column is present only for completeness, but it's values will be ignored. A font will be set as bold only
and only if, during the names recalculation, the user will choose to use linked styles (-ls / --linked styles option).

The 'wdt' and 'width' columns contain the short and long literals for the width style names (for example: Cn;
Condensed).

The 'wgt' and 'weight' columns contain the short and long literals for the weight style names (for example: Lt, Light).

The 'slp' and 'slope' columns contain the short and long literals for the slope style names (for example: It, Italic).

The user will choose the namerecords where to write long or short literals.

The 'data.csv' file can be created using the following command:

    ftcli assistant init-csv INPUT_PATH

At this point, the CSV file will contain a representation of the actual state of the fonts (the family_name column will
contain values of nameID 16, or nameID 1 if 16 is not present). It can be edited manually, using the 'ftcli assistant
edit-csv' command and also automatically recalculated using the 'ftcli assistant recalc-csv' command.

The 'ftcli assistant recalc-csv' command will recalculate style names, italic bits, width and weight style names
according to the values contained in the JSON configuration file.

When the 'data.csv' file contains the desired values, these values can be applied to fonts running the 'ftcli assistant
recalc-names' command (see 'ftcli assistant recalc-names --help' for more information).

#### edit-cfg
Command line editor for JSON configuration files.

Usage:

    ftcli  edit-cfg [OPTIONS] CONFIG_FILE

Example:

    ftcli assistant edit-cfg "C:\Fonts\config.json"

It is strongly recommended using this tool to edit the JSON configuration files. It prevents malformed JSON errors and
errors due to wrong values (for example, an out of range usWeightClass, or a string where's an integer is expected).

#### edit-csv
Usage:

    ftcli assistant edit-csv [OPTIONS] INPUT_PATH

Command line editor for 'data.csv' files.

This tool is not intended to replace a code editor for CSV files, but can help to make small edits without leaving the
command line. For complex projects, it's strongly recommended using a code editor like Visual Studio Code or even Excel.

Options:

    -c, --config-file PATH

Use a custom configuration file instead of the default config.json file located in the same folder of INPUT_PATH.

#### init-cfg
Usage:

    ftcli assistant init-cfg [OPTIONS] INPUT_PATH
    
Creates a JSON configuration file containing the default values in the specified INPUT_PATH folder.

Options:

    -q, --quiet

Suppress overwrite confirmation message if the config.json file already exists.

#### init-csv
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

#### recalc-csv
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

#### recalc-names
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

### ftcli os2
A command line tool to edit OS/2 table.

**Usage:**

    ftcli cli-tool [OPTIONS] INPUT_PATH


**Usage examples:**

    ftcli os2 "C:\Fonts\" -el 4 -utm -o "C:\Fonts\Fixed fonts\"
    ftcli os2 "C:\Fonts\MyFont-BoldItalic.otf" -b -i --wg 700 --no-overwrite


#### Options:

##### -v, --version
Updates OS/2.version value. Version can only be incremented at the moment.

When upgrading from version 1, sxHeight, sCapHeight, usDefaultChar, usBreakChar and usMaxContext will be recalculated.
When upgrading from version 0, also ulCodePageRange1 and ulCodePageRange2 will be recalculated.

**Usage:**

    ftcli os2 -v/--version [1|2|3|4|5] INPUT_PATH

**Example:**

    ftcli os2 -v 4 "C:\Fonts\"

##### -wg,  --weight
Sets the OS/2.usWeightClass value. This parameter must be an integer between 1 and 1000.

**Usage:**

    ftcli os2 -wg/--weight [1-1000] INPUT_PATH

**Example:**

    ftcli os2 -wg 700 "C:\Fonts\MyFont-Bold.otf"

##### -wd,  --width
Sets the OS/2.usWidthClass value. This parameter must be an integer between 1 and 9.

**Usage:**

    ftcli os2 -wd/--width [1-9] INPUT_PATH

**Example:**

    ftcli os2 -wd 3 "C:\Fonts\MyFontCondensed-Bold.otf"

##### -el, --embed-level
Sets embedding level (OS/2.fsType bits 0-3).

**Usage:**

    ftcli os2 -el/--embed-level [0|2|4|8] INPUT_PATH

**Example:**

    ftcli os2 -el 2 "C:\Fonts"

Allowed values are 0, 2, 4 or 8:

0: Installable embedding

2: Restricted License embedding

4: Preview & Print embedding

8: Editable embedding

See: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype for more information.

##### -ns, --no-subsetting
Set or clears OS/2.fsType bit 8 (no subsetting).

When this bit is set to 1, the font may not be subsetted prior to
embedding. Other embedding restrictions specified in bits 0 to 3 and bit 9 also apply.

**Usage:**

    ftcli os2 -ns/--no-subsetting [0|1] INPUT_PATH

**Example:**

    ftcli os2 -ns 1 "C:\Fonts\"

##### -beo, --bitmap-embedding-only
Sets or clears fsType bit 9 (Bitmap embedding only).

When this bit is set, only bitmaps contained in the font may be embedded. No outline data may be embedded. If there are
no bitmaps available in the font, then the font is considered unembeddable and the embedding services will fail. Other
embedding restrictions specified in bits 0-3 and 8 also apply.

**Usage:**

    ftcli os2 -beo/--bitmap-embedding-only INPUT_PATH

**Example**

    ftcli os2 -beo "C:\Fonts"

##### -i, --italic / -ni, --no-italic
Sets or clears the italic bits (fsSelection bit 0 and head.macStyle bit 1).

**Usage:**

    ftcli os2 -i/--italic INPUT_PATH
    ftcli os2 -ni/--no-italic INPUT_PATH

**Examples:**

    ftcli os2 -i "C:\MyFont-Italic.otf"
    ftcli os2 -ni "C:\MyFont-Regular.otf"

##### -b, --bold / -nb, --no-bold
Sets or clears the bold bits (fsSelection bit 5 and head.macStyle bit 0).

**Usage:**

    ftcli os2 -b/--bold INPUT_PATH
    ftcli os2 -nb/--no-bold INPUT_PATH

**Examples:**

    ftcli os2 -b "C:\MyFont-Bold.otf"
    ftcli os2 -nb "C:\MyFont-Regular.otf"

##### -r, --regular
Sets fsSelection bit 6 and clears bold (fsSelection bit 5, head.macStyle bit 0) and italic (fsSelection bit 0, 
head.macStyle bit 1) bits. This is equivalent to -nb -ni and can't be used in conjunction with -b or -i.

**Usage:**

    ftcli os2 -r/--regular INPUT_PATH

**Examples:**

    ftcli os2 -r "C:\MyFont-Regular.otf"

##### -utm, --use-typo-metrics
Sets or clears the USE_TYPO_METRICS bit (fsSelection bit 7).

If set, it is strongly recommended that applications use OS/2.sTypoAscender - OS/2.sTypoDescender + OS/2.sTypoLineGap
as the default line spacing for this font.

See https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection for more information.

**Usage:**

    ftcli os2 -utm/--use-type-metrics value INPUT_PATH

**Examples:**

    ftcli os2 -utm 1 "C:\Fonts\"

##### -wws, --wws-consistent
If the OS/2.fsSelection bit is set, the font has 'name' table strings consistent with a weight/width/slope family
without requiring use of name IDs 21 and 22.

See https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection form more information.

See also https://typedrawers.com/discussion/3857/fontlab-7-windows-reads-exported-font-name-differently.

**Usage:**

    ftcli os2 -wws/--wws-consistent value INPUT_PATH

**Examples:**

    ftcli os2 -wws 1 "C:\Fonts\MyFont-BlackItalic.otf"
    ftcli os2 -wws 0 "C:\Fonts\MyFont-BlackItalicDisplay.otf"

##### -ob, --oblique
Sets or clears the oblique bit (fsSelection bit 9).

If bit 9 is set, then this font is to be considered an “oblique” style by processes which make a distinction between
oblique and italic styles, such as Cascading Style Sheets font matching. For example, a font created by algorithmically
slanting an upright face will set this bit.

If a font has a version 4 or later OS/2 table and this bit is not set, then this font is not to be considered an
“oblique” style. For example, a font that has a classic italic design will not set this bit.

This bit, unlike the ITALIC bit (bit 0), is not related to style-linking in applications that assume a four-member
font-family model comprised of regular, italic, bold and bold italic. It may be set or unset independently of the ITALIC
bit. In most cases, if OBLIQUE is set, then ITALIC will also be set, though this is not required.

See https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection for more information.

**Usage:**

    ftcli os2 -ob/--oblique value INPUT_PATH

**Examples:**

    ftcli os2 -ob 1 "C:\Fonts\MyFont-Oblique.otf"
    ftcli os2 -ob 0 "C:\Fonts\MyFont-Regular.otf"

##### -ach, --ach-vend-id'
Sets the achVendID tag (vendor's four-character identifier).

**Usage:**

    ftcli os2 -ach/--ach-vend-id string INPUT_PATH

**Example:**

    ftcli os2 -ach MyFo "C:\Fonts"

##### --recalc-unicode-ranges
Recalculates the ulUnicodeRanges 1-4 values.

**Usage:**

    ftcli os2 --recalc-unicode-ranges INPUT_PATH

**Example:**

    ftcli os2 --recalc-unicode-ranges "C:\Fonts\"

##### --recalc-codepage-ranges
Recalculates the ulCodePageRanges 1-2 values.

**Usage:**

    ftcli os2 --recalc-codepage-ranges INPUT_PATH

**Example:**

    ftcli os2 --recalc-codepage-ranges "C:\Fonts\"

##### --recalc-us-max-context
Recalculates usMaxContext value.

**Usage:**

    ftcli os2 --recalc-us-max-context INPUT_PATH

**Example:**

    ftcli os2 --recalc-us-max-context "C:\Fonts\"

##### -o, -output-dir
The output directory where the output files are to be created. If it doesn't exist, will be created. If not specified,
files are saved to the same folder.

**Usage example:**

    ftcli os2 -el 2 -utm "C:\Fonts" -o "C:\Fonts\Fixed"

##### --recalc-timestamp
By default, original head.modified value is kept when a font is saved. Use this switch to set head.modified timestamp
to current time.

**Usage example:**

    ftcli os2 -el 2 -utm "C:\Fonts" -o --recalc-timestamp

##### --no-overwrite
By default, modified files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name).

**Usage example:**

    ftcli os2 -el 2 -utm "C:\Fonts" --no-overwrite

### metrics
Usage:

    ftcli font-metrics [OPTIONS] COMMAND [ARGS]...

Aligns all the fonts to the same baseline.

The 'ftcli font-metrics align' command calculates the maximum ascenders and descenders of a set of fonts and applies them to all fonts in that set.

The 'ftcli font-metrics copy' command copies vertical metrics from a source font to one or more destination fonts.

Commands:

    align

Aligns all fonts in INPUT_PATH to the same baseline.

    copy
    
Copies vertical metrics from a source font to one or more destination fonts.

### names

Usage:

    ftcli font-names [OPTIONS] COMMAND [ARGS]...

A command line tool to add, delete and edit namerecords.

Commands:

    del-mac-names

Deletes all namerecords in platformID 1.
    
    del-name

Deletes the specified nemerecord from the name table.

    find-replace

Replaces a string in the name table with a new string.

    lang-help
  
Prints available languages that can be used with the...
    
    set-name

Writes the specified namerecord in the name table.

    win-2-mac

Copies namerecords from Windows table to Macintosh table.

### font-renamer
Renames font files according to the provided source.

### remove-overlaps
Simplify glyphs in TTFont by merging overlapping...

### ttc-extractor
Extracts .ttc fonts.

### print
Prints various font's information.

### webfonts
Web fonts related tools.



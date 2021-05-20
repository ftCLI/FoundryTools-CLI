# ftCLI
ftCLI is a command line interface built with [click](https://click.palletsprojects.com/en/8.0.x/) to edit fonts using [FontTools](https://github.com/fonttools/fonttools).

Python 3.8 or later is required to install ftCLI.

The following packages will be installed during setup:

* fonttools
* click
* colorama
* brotli
* skia-pathops
* zopfli
 
## Installation
    pip install -e .
 
## Usage

### automator
A set of tools to correctly compile the name table and set proper values for usWeightClass, usWidthClass, bold, italic and oblique bits.

The process creates a JSON configuration file and a CSV file that will be used to fix the fonts. Both files can be automatically created and eventually edited manually or using the integrated command line editor. Once everything is correctly set in the CSV file, the values inside it can be written to the fonts.

1) The JSON configuration file.

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

    ftcli automator init-cfg INPUT_PATH

The above command will create a file named 'config.json' in the INPUT_PATH folder (or parent folder if INPUT_PATH is a
file).

Once created the configuration file, you may be in need to edit it according to your needs.

    ftcli automator edit-cfg CONFIG_FILE

Values contained in the configuration file will be used to fill the data.csv file in the next steps.

2) The CSV data file.

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

    ftcli automator init-csv INPUT_PATH

At this point, the CSV file will contain a representation of the actual state of the fonts (the family_name column will
contain values of nameID 16, or nameID 1 if 16 is not present). It can be edited manually, using the 'ftcli automator
edit-csv' command and also automatically recalculated using the 'ftcli automator recalc-csv' command.

The 'ftcli automator recalc-csv' command will recalculate style names, italic bits, width and weight style names
according to the values contained in the JSON configuration file.

When the 'data.csv' file contains the desired values, these values can be applied to fonts running the 'ftcli automator
recalc-names' command (see 'ftcli automator recalc-names --help' for more information).

#### edit-cfg
Command line editor for JSON configuration files.

Usage:

    ftcli  edit-cfg [OPTIONS] CONFIG_FILE

Example:

    ftcli automator edit-cfg "C:\Fonts\config.json"

It is strongly recommended to use this tool to edit the JSON configuration files. It prevents malformed JSON errors and errors due to wrong values (for example, an out of range usWeightClass, or a string where's an integer is expected).

#### edit-csv
Usage:

    ftcli  edit-csv [OPTIONS] INPUT_PATH

Command line editor for 'data.csv' files.

This tool is not intended to replace a code editor for CSV files, but can help to make small edits without leaving the command line. For complex projects, it's strongly recommended to use a code editor like Visual Studio Code or even Excel.

Options:

-c, --config-file PATH

Use a custom configuration file instead of the default config.json file located in the same folderof INPUT_PATH.

#### init-cfg
Usage:

    ftcli automator init-cfg [OPTIONS] INPUT_PATH
    
Creates a JSON configuration file containing the default values in the specified INPUT_PATH folder.

Options:

-q, --quiet

Suppress the overwrite confirmation message if the config.json file already exists.

#### init-csv
Usage:

    ftcli  init-csv [OPTIONS] INPUT_PATH

Creates or resets the CSV database file (data.csv).

Example 1:

    ftcli automator init-csv "C:\Fonts\"

The above command will create the 'data.csv' file in C:\Fonts\ (and a configuration file with default values if it does not exist).

Example 2:

    ftcli automator init-csv "C:\Fonts\Font.otf"

The above command will create the 'data.csv' in the INPUT_PATH folder (or parent folder, if INPUT_PATH is a file).

data.csv file contains:

* the file names;
* the usWidthClass, usWeightClass, bold italic and oblique bits values of all font files found in INPUT_PATH;
* tries to guess the family name reading the name table. It also contains weight and widths literals, retrieved parsing the config.json file.

It can be edited manually or using the 'ftcli automator edit-csv INPUT_PATH' command.

Options:

-c, --config-file PATH

Use a custom configuration file instead of the default config.json file located in the same folderof INPUT_PATH.

-q, --quiet

Suppress the overwrite confirmation message if the data.csv and/or config.json files alreadyexist.

#### recalc-csv


#### recalc-names



### cli-tool
Command line font editor.

### font-metrics
Aligns all the fonts to the same baseline.

###font-names
A command line tool to add, delete and edit namerecords.

### font-renamer
Renames font files according to the provided source...

### remove-overlaps
Simplify glyphs in TTFont by merging overlapping...

### ttc-extractor
Extracts .ttc fonts.

### viewer
Prints various font's information.

### wf-tools
Web fonts related tools.



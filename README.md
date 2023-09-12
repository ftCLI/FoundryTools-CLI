# FoundryTools-CLI
FoundryTools-CLI, former known as ftCLI, is a collection of command line tools written in Python to inspect, manipulate
and convert fonts. It takes advantage of the capabilities made available by other tools such as:

* [FontTools](https://github.com/fonttools/fonttools)
* [AFDKO](https://github.com/adobe-type-tools/afdko)
* [skia-pathops](https://github.com/fonttools/skia-pathops)
* [cffsubr](https://github.com/adobe-type-tools/cffsubr)
* [ttfautohint-py](https://github.com/fonttools/ttfautohint-py)
* [dehinter](https://github.com/source-foundry/dehinter)

The command line interface is built with [click](https://github.com/pallets/click/) and tables are rendered by
[rich](https://github.com/Textualize/rich).

Even if not directly imported to keep the footprint as small as possible, portions of code have been copied from
[fontbakery](https://github.com/googlefonts/fontbakery) and [font-line](https://github.com/source-foundry/font-line).

## Installation
FoundryTools-CLI requires Python 3.9 or later.

**Note for Windows users**: installation on Python 3.11 is strongly discouraged because AFDKO doesn't support it, and
an attempt of installation would probably fail. Since macOS users successfully installed FoundryTools-CLI on Python
3.11, requirements have been loosened up.

**IMPORTANT**: If you have Python 2.x installed in your system, you may have to use `python3` (instead of `python`) in
the commands below.

### pip
FoundryTools-CLI releases are available on the Python Package Index (PyPI), so it can be installed with
[pip](https://pip.pypa.io/):

    python -m pip install foundrytools-cli

### Editable mode
If you would like to contribute to the development, you can clone the repository from GitHub, install the package in
'editable' mode and modify the source code in place. We strongly recommend using a virtual environment.

    # clone the repository:
    git clone https://github.com/ftCLI/foundrytools-cli.git
    cd foundrytools-cli

    # create new virtual environment named e.g. ftcli-venv, or whatever you prefer:
    python -m venv ftcli-venv
    
    # to activate the virtual environmtnet in macOS and Linux, do:
    . ftcli-venv/bin/activate
    
    # to activate the virtual environment in Windows, do:
    ftcli-venv\Scripts\activate.bat
    
    # install in 'editable' mode
    python -m pip install -e .


## Documentation
FoundryTools-CLI is a Terminal app where commands are logically organized into subcommands.

Please refer to the [user documentation](https://ftcli.github.io/FoundryTools-CLI/).

## License
FoundryTools-CLI is available under the [MIT license](LICENSE)

## Credits
To Sergiev. May You rest in peace.




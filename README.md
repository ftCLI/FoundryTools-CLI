# FoundryTools-CLI

FoundryTools-CLI is a command line interface for the FoundryTools library, which
provides a set of tools for working with font files. It is designed to be used
from the command line, allowing users to perform various operations on font
files without the need for a graphical user interface.

The CLI provides a range of commands for manipulating font files, including
converting between different font formats, extracting and modifying font
metadata, and performing various font-related operations. It is built on top of
the FoundryTools library, which provides a comprehensive set of tools for
working with font files in Python.

The CLI is designed to be easy to use and provides a consistent interface for
working with different font formats. It is suitable for both developers and
font designers who need to perform various operations on font files from the
command line. The CLI is also extensible, allowing users to add their own
commands and functionality as needed.

![image](https://github.com/user-attachments/assets/f1389440-8b94-463f-b9c8-29c0c37dfced)

The command line interface is built with [click](https://github.com/pallets/click/) and tables are
rendered by [rich](https://github.com/Textualize/rich).

## Installation

FoundryTools-CLI requires Python 3.9 or later.

**IMPORTANT**: If you have Python 2.x installed in your system, you may have to use `python3`
(instead of `python`) in the commands below.

### pip

FoundryTools-CLI releases are available on the Python Package Index (PyPI), so it can be installed
with [pip](https://pip.pypa.io/):

```
python -m pip install foundrytools-cli
```

### Editable mode

If you would like to contribute to the development, you can clone the repository from GitHub,
install the package in 'editable' mode and modify the source code in place. We strongly recommend
using a virtual environment.

```
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
```

## Documentation

FoundryTools-CLI is a Terminal app where commands are logically organized into subcommands.

Please refer to the [user documentation](https://foundrytools-cli.readthedocs.io/).

## License

FoundryTools-CLI is available under the [MIT license](LICENSE)

## Credits

To Sergiev. May You rest in peace.

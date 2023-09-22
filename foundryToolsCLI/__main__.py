import sys
from pathlib import Path

from loguru import logger

import click

this_directory = Path(__file__).parent
plugin_folder = this_directory.joinpath("CLI")


class FoundryToolsCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for file in plugin_folder.iterdir():
            if file.name.endswith(".py") and file.name.startswith("ftcli_"):
                rv.append(file.name[6:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, cmd_name):
        try:
            mod = __import__(f"foundryToolsCLI.CLI.ftcli_{cmd_name}", None, None, ["cli"])
        except ImportError as e:
            logger.error(e)
            return

        return mod.cli


main = FoundryToolsCLI(help="FoundryTools Command Line Interface.")


if __name__ == "__main__":
    sys.exit(main())

from fontTools.ttLib.tables._f_v_a_r import Axis, NamedInstance
from foundrytools import Font
from rich.console import Console
from rich.table import Table

__all__ = ["main"]


def main(font: Font) -> None:
    """
    Prints the variable font instances in a table format.
    """
    console = Console()

    table = Table(
        title="\nftCLI - Variable Font Instances Viewer",
        show_header=True,
        header_style="bold cyan",
        title_style="bold green",
    )

    axes: list[Axis] = font.t_fvar.table.axes
    instances: list[NamedInstance] = font.t_fvar.table.instances

    table.add_section()
    table.add_column("#")
    for axis in axes:
        table.add_column(axis.axisTag)
    table.add_column("postscriptNameID")
    table.add_column("subfamilyNameID")

    for count, instance in enumerate(instances, start=1):
        subfamily_name = (
            f"{instance.subfamilyNameID}: "
            f"{font.t_name.table.getDebugName(instance.subfamilyNameID)}"
        )
        postscript_name = (
            f"{instance.postscriptNameID}: "
            f"{font.t_name.table.getDebugName(instance.postscriptNameID)}"
        )
        table.add_row(
            str(count),
            *[str(v) for k, v in instance.coordinates.items() if k in [a.axisTag for a in axes]],
            postscript_name,
            subfamily_name,
        )
    console.print(table)

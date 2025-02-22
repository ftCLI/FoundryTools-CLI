import os
from pathlib import Path
from textwrap import TextWrapper
from typing import Any, Callable, Optional, Union

import click


class BaseCommand(click.Command):
    """
    Base command for all commands in the CLI.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        shared_options = [
            click.Argument(
                ["input_path"],
                type=click.Path(exists=True, resolve_path=True, path_type=Path),
            ),
            click.Option(
                ["-r", "--recursive"],
                is_flag=True,
                default=False,
                help="""
                Recursively find font files both in input directory and its subdirectories.

                Only applicable if ``INPUT_PATH`` is a directory.
                """,
            ),
            click.Option(
                ["-out", "--output-dir"],
                type=click.Path(path_type=Path, file_okay=False, writable=True),
                callback=output_dir_callback,
                help="""
                The directory where output files are to be saved.

                If not specified, files will be saved to the same folder.

                If the output directory doesn't exist, it will be created, as well as any missing
                parent directories.
                """,
            ),
            click.Option(
                ["-no-ow", "--no-overwrite", "overwrite"],
                is_flag=True,
                default=True,
                help="""
                Do not overwrite existing files on save.

                If a file with the same name as the output file already exists, the command will
                suffix the filename with a number (``#1``, ``#2``, etc.).

                By default, existing files are overwritten.
                """,
            ),
            click.Option(
                ["-no-rbb", "--no-recalc-bboxes", "recalc_bboxes"],
                is_flag=True,
                default=True,
                help="""
                Do not recalculate the font's bounding boxes on save.

                By default, ``glyf``, ``CFF ``, ``head`` bounding box values and ``hhea``/``vhea``
                min/max values are recalculated on save. Also, the glyphs are compiled on importing,
                which saves memory consumption and time.
                """,
            ),
            click.Option(
                ["-no-rtb", "--no-reorder-tables", "reorder_tables"],
                is_flag=True,
                default=True,
                help="""
                Do not reorder the font's tables on save.

                By default, tables are sorted by tag on save (recommended by the OpenType
                specification).
                """,
            ),
            click.Option(
                ["-rts", "--recalc-timestamp"],
                is_flag=True,
                default=False,
                help="""
                Set the ``modified`` timestamp in the ``head`` table on save.

                By default, the original ``modified`` timestamp is kept.
                """,
            ),
        ]
        kwargs.setdefault("params", []).extend(shared_options)
        kwargs.setdefault("no_args_is_help", True)
        kwargs.setdefault("context_settings", {"help_option_names": ["-h", "--help"]})
        super().__init__(*args, **kwargs)


def make_options(options: list[Callable]) -> Callable:
    """
    Add options to a click command.

    :param options: A list of click options
    :type options: list[Callable]
    :return: A decorator that adds the options to a click command
    :rtype: Callable
    """

    def _add_options(func: Callable) -> Callable:
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def choice_to_int_callback(
    ctx: click.Context, _: click.Parameter, value: Union[str, tuple[str, ...]]
) -> Optional[Union[int, tuple[int, ...]]]:
    """
    Callback for click options that accept a choice. Converts the choice to an integer or a tuple
    of integers.

    If the value is None or the click context is resilient, returns None. If the parameter is
    multiple, converts a click choice tuple of strings to a tuple of integers. Otherwise, converts
    a click choice string to an integer.

    :param ctx: click Context
    :type ctx: click.Context
    :param _: click Parameter
    :type _: click.Parameter
    :param value: The value to convert
    :type value: Union[str, tuple[str, ...]]
    :return: The converted value
    :rtype: Optional[Union[int, tuple[int, ...]]]
    """

    # we do not check if the values can be converted to integers here because the click.Choice
    # should be correctly built.

    def _to_int(val: str) -> int:
        return int(val)

    if not value or ctx.resilient_parsing:
        return None
    if isinstance(value, tuple):
        return tuple(_to_int(v) for v in value)
    return _to_int(value)


def tuple_to_set_callback(
    ctx: click.Context, _: click.Parameter, value: tuple[Any, ...]
) -> set[Any]:
    """
    Callback for click options that accept a tuple. Converts the tuple to a set.

    If the value is None or the click context is resilient, returns None. Otherwise, converts the
    tuple to a set.

    :param ctx: click Context
    :type ctx: click.Context
    :param _: click Parameter
    :type _: click.Parameter
    :param value: The value to convert
    :type value: tuple[Any, ...]
    :return: The converted value
    :rtype: set[Any]
    """

    if not value or ctx.resilient_parsing:
        return set()
    return set(value)


def output_dir_callback(
    ctx: click.Context, _: click.Parameter, value: Optional[Path]
) -> Optional[Path]:
    """
    Callback for ``--output-dir option``.

    Tries to create the output directory if it doesn't exist. Checks if the output directory is
    writable. Returns a Path object. If the callback fails, raises a click.BadParameter exception.

    :param ctx: click Context
    :type ctx: click.Context
    :param _: click Parameter
    :type _: click.Parameter
    :param value: The value to convert
    :type value: Optional[Path]
    :return: The converted value
    :rtype: Optional[Path]
    """

    # if the value is None or the click context is resilient, return None
    if not value or ctx.resilient_parsing:
        return None
    # try to create the output directory if it doesn't exist
    try:
        value.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise click.BadParameter(f"Could not create output directory: {e}") from e
    # check if the output directory is writable
    if not os.access(value, os.W_OK):
        raise click.BadParameter(f"Output directory is not writable: {value}")
    return value


def ensure_at_least_one_param(ctx: click.Context) -> None:
    """
    Checks if any attributes are provided to set, except for the ignored ones.

    If no attributes are provided, raises a click.UsageError exception.

    :param ctx: click Context
    :type ctx: click.Context
    :raises click.UsageError: If no attributes are provided to set
    """
    ignored = [
        "input_path",
        "output_dir",
        "recursive",
        "recalc_timestamp",
        "reorder_tables",
        "recalc_bboxes",
        "overwrite",
    ]

    if all(value is None for key, value in ctx.params.items() if key not in ignored):
        raise click.UsageError("No attributes provided to set.")


def wrap_string(
    string: str, width: int, initial_indent: int, indent: int, max_lines: Optional[int] = None
) -> str:
    """
    Wraps a string to a specified width.
    """
    wrapped_string = TextWrapper(
        width=width,
        initial_indent=" " * initial_indent,
        subsequent_indent=" " * indent,
        max_lines=max_lines,
        break_on_hyphens=False,
        break_long_words=True,
    ).fill(string)
    return wrapped_string

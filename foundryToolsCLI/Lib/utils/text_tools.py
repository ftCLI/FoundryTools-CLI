from textwrap import TextWrapper
from typing import Optional


def wrap_string(
    string: str, width: int, initial_indent: int, indent: int, max_lines: Optional[int] = None
) -> str:
    """
    It wraps a string to a given width, with a given indentation

    :param string: The string to wrap
    :type string: str
    :param width: The maximum width of the wrapped lines
    :type width: int
    :param initial_indent: The number of spaces to add to the beginning of each line
    :type initial_indent: int
    :param indent: The number of spaces to add to the left margin of subsequent lines
    :type indent: int
    :param max_lines: The maximum number of lines to return. If the string is longer than this, it will be truncated
    :type max_lines: int
    :return: A string that has been wrapped to the specified width.
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

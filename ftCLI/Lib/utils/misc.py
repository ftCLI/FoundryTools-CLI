from textwrap import TextWrapper


def is_nth_bit_set(x: int, n: int):
    """
    If the nth bit of an integer x is set, return True, otherwise return False

    :param x: The number whose nth bit we want to check
    :type x: int
    :param n: The bit position to check
    :type n: int
    :return: Returns True if the nth bit of x is set, and False otherwise.
    """
    if x & (1 << n):
        return True
    return False


def set_nth_bit(x: int, n: int):
    """
    It takes an integer x and sets the nth bit of x to 1

    :param x: The number whose nth bit you want to set
    :type x: int
    :param n: the bit we want to set
    :type n: int
    :return: The number x with the nth bit set to 1.
    """
    return x | 1 << n


def unset_nth_bit(x: int, n: int):
    """
    It takes an integer x and clears the nth bit, setting its value to 0

    :param x: The number whose nth bit we want to clear
    :type x: int
    :param n: the nth bit to clear
    :type n: int
    :return: The number x with the nth bit set to 0.
    """
    return x & ~(1 << n)


def wrap_string(string: str, width: int, initial_indent: int, indent: int, max_lines: int = None) -> str:
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


# Functions copied from ufo2ft 2.31.1


def int_list_to_num(intList, start, length):
    all_integers = []
    binary = ""
    for i in range(start, start + length):
        if i in intList:
            b = "1"
        else:
            b = "0"
        binary = b + binary
        if not (i + 1) % 8:
            all_integers.append(binary)
            binary = ""
    if binary:
        all_integers.append(binary)
    all_integers.reverse()
    all_integers = " ".join(all_integers)
    return binary2num(all_integers)


def binary2num(binary):
    binary = strjoin(binary.split())
    num = 0
    for digit in binary:
        num = num << 1
        if digit != "0":
            num = num | 0x1
    return num


def strjoin(iterable, joiner=""):
    return tostr(joiner).join(iterable)


def tostr(s, encoding="ascii", errors="strict"):
    if not isinstance(s, str):
        return s.decode(encoding, errors)
    else:
        return s


def calc_code_page_ranges(unicodes):
    """Given a set of Unicode codepoints (integers), calculate the
    corresponding OS/2 CodePage range bits.
    This is a direct translation of FontForge implementation:
    https://github.com/fontforge/fontforge/blob/7b2c074/fontforge/tottf.c#L3158
    """
    codepageRanges = set()

    chars = [chr(u) for u in unicodes]

    hasAscii = set(range(0x20, 0x7E)).issubset(unicodes)
    hasLineart = "┤" in chars

    for char in chars:
        if char == "Þ" and hasAscii:
            codepageRanges.add(0)  # Latin 1
        elif char == "Ľ" and hasAscii:
            codepageRanges.add(1)  # Latin 2: Eastern Europe
            if hasLineart:
                codepageRanges.add(58)  # Latin 2
        elif char == "Б":
            codepageRanges.add(2)  # Cyrillic
            if "Ѕ" in chars and hasLineart:
                codepageRanges.add(57)  # IBM Cyrillic
            if "╜" in chars and hasLineart:
                codepageRanges.add(49)  # MS-DOS Russian
        elif char == "Ά":
            codepageRanges.add(3)  # Greek
            if hasLineart and "½" in chars:
                codepageRanges.add(48)  # IBM Greek
            if hasLineart and "√" in chars:
                codepageRanges.add(60)  # Greek, former 437 G
        elif char == "İ" and hasAscii:
            codepageRanges.add(4)  # Turkish
            if hasLineart:
                codepageRanges.add(56)  # IBM turkish
        elif char == "א":
            codepageRanges.add(5)  # Hebrew
            if hasLineart and "√" in chars:
                codepageRanges.add(53)  # Hebrew
        elif char == "ر":
            codepageRanges.add(6)  # Arabic
            if "√" in chars:
                codepageRanges.add(51)  # Arabic
            if hasLineart:
                codepageRanges.add(61)  # Arabic; ASMO 708
        elif char == "ŗ" and hasAscii:
            codepageRanges.add(7)  # Windows Baltic
            if hasLineart:
                codepageRanges.add(59)  # MS-DOS Baltic
        elif char == "₫" and hasAscii:
            codepageRanges.add(8)  # Vietnamese
        elif char == "ๅ":
            codepageRanges.add(16)  # Thai
        elif char == "エ":
            codepageRanges.add(17)  # JIS/Japan
        elif char == "ㄅ":
            codepageRanges.add(18)  # Chinese: Simplified chars
        elif char == "ㄱ":
            codepageRanges.add(19)  # Korean wansung
        elif char == "央":
            codepageRanges.add(20)  # Chinese: Traditional chars
        elif char == "곴":
            codepageRanges.add(21)  # Korean Johab
        elif char == "♥" and hasAscii:
            codepageRanges.add(30)  # OEM Character Set
        # Symbol bit has a special meaning (check the spec), we need
        # to confirm if this is wanted by default.
        # elif chr(0xF000) <= char <= chr(0xF0FF):
        #    codepageRanges.add(31)          # Symbol Character Set
        elif char == "þ" and hasAscii and hasLineart:
            codepageRanges.add(54)  # MS-DOS Icelandic
        elif char == "╚" and hasAscii:
            codepageRanges.add(62)  # WE/Latin 1
            codepageRanges.add(63)  # US
        elif hasAscii and hasLineart and "√" in chars:
            if char == "Å":
                codepageRanges.add(50)  # MS-DOS Nordic
            elif char == "é":
                codepageRanges.add(52)  # MS-DOS Canadian French
            elif char == "õ":
                codepageRanges.add(55)  # MS-DOS Portuguese

    if hasAscii and "‰" in chars and "∑" in chars:
        codepageRanges.add(29)  # Macintosh Character Set (US Roman)

    # when no codepage ranges can be enabled, fall back to enabling bit 0
    # (Latin 1) so that the font works in MS Word:
    # https://github.com/googlei18n/fontmake/issues/468
    if not codepageRanges:
        codepageRanges.add(0)

    return codepageRanges

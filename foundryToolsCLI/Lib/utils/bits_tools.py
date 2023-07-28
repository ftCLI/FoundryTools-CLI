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

from fontTools.misc.textTools import num2binary
from fontTools.ttLib.tables.O_S_2f_2 import table_O_S_2f_2

from ftCLI.Lib.utils.misc import is_nth_bit_set, set_nth_bit, unset_nth_bit


class TableOS2(table_O_S_2f_2):
    def __init__(self, tag=None):
        super().__init__(tag)

    def set_weight_class(self, value: int) -> None:
        """
        Sets the usWeightClass value

        :param value: Integer in range 1-1000
        :type value: int
        """
        if value not in range(1, 1001):
            print("usWeighClass value must be an integer between 1 and 1000.")
            return
        setattr(self, "usWeightClass", value)

    def set_width_class(self, value: int) -> None:
        """
        Sets the usWidthClass value

        :param value: Integer in range 1-9
        :type value: int
        """
        if value not in range(1, 10):
            print("usWidthClass value must be an integer between 1 and 9.")
            return
        setattr(self, "usWidthClass", value)

    def set_ach_vend_id(self, value: str) -> None:
        """
        Sets the achVendID tag (vendor's four-character identifier).

        :param value: The string to be set. If longer than 4 characters, will be truncated
        :type value: str
        """
        if len(value) > 4:
            print("achVendID string was longer than 4 characters and has been truncated.")
        value = value[0:4].ljust(4)
        setattr(self, "achVendID", value)

    def is_italic_bit_set(self) -> bool:
        """
        > Returns True if the fsSelection bit 0 (ITALIC) is set, otherwise False

        :return: A boolean value.
        """
        return is_nth_bit_set(self.fsSelection, 0)

    def set_italic_bit(self) -> None:
        """
        Sets fsSelection bit 0 (ITALIC)
        """
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 0))

    def clear_italic_bit(self) -> None:
        """
        Clears fsSelection bit 0 (ITALIC)
        """
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 0))

    def is_bold_bit_set(self) -> bool:
        """
        > Returns True if the fsSelection bit 5 (BOLD) is set, otherwise False

        :return: A boolean value.
        """
        return is_nth_bit_set(self.fsSelection, 5)

    def set_bold_bit(self) -> None:
        """
        Sets fsSelection bit 5 (BOLD)
        """
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 5))

    def clear_bold_bit(self) -> None:
        """
        Clears fsSelection bit 5 (BOLD)
        """
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 5))

    def is_regular_bit_set(self) -> bool:
        """
        > Returns True if the fsSelection bit 6 (REGULAR) is set, otherwise False

        :return: A boolean value.
        """
        return is_nth_bit_set(self.fsSelection, 6)

    def set_regular_bit(self) -> None:
        """
        Sets fsSelection bit 6 (REGULAR)
        """
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 6))

    def clear_regular_bit(self) -> None:
        """
        Clears fsSelection bit 6 (REGULAR)
        """
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 6))

    def is_use_typo_metrics_bit_set(self) -> bool:
        """
        > Returns True if the fsSelection bit 7 (USE_TYPO_METRICS) is set, otherwise False

        :return: A boolean value.
        """
        return is_nth_bit_set(self.fsSelection, 7)

    def set_use_typo_metrics_bit(self) -> None:
        """
        Sets fsSelection bit 7 (USE_TYPO_METRICS) if OS/2 table version is greater than 3
        """
        if self.version >= 4:
            setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 7))
        else:
            print("fsSelection bit 7 is only defined in OS/2 version 4 and up.")
            return

    def clear_use_typo_metrics_bit(self) -> None:
        """
        Clears fsSelection bit 7 (USE_TYPO_METRICS)
        """
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 7))

    # WWS bit (OS/2.fsSelection bit 8)

    def is_wws_bit_set(self) -> bool:
        """
        > Returns True if the fsSelection bit 8 (WWS) is set, otherwise False

        :return: A boolean value.
        """
        return is_nth_bit_set(self.fsSelection, 8)

    def set_wws_bit(self) -> None:
        """
        Sets fsSelection bit 8 (WWS) if OS/2 table version is greater than 3
        """
        if self.version >= 4:
            setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 8))
        else:
            print("WARNING: fsSelection bit 8 is only defined in OS/2 version 4 and up.")
            return

    def clear_wws_bit(self) -> None:
        """
        Clears fsSelection bit 8 (WWS)
        """
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 8))

    def is_oblique_bit_set(self) -> bool:
        """
        > Returns True if the fsSelection bit 9 (OBLIQUE) is set, otherwise False

        :return: A boolean value.
        """
        return is_nth_bit_set(self.fsSelection, 9)

    def set_oblique_bit(self) -> None:
        """
        Sets fsSelection bit 9 (OBLIQUE) if OS/2 table version is greater than 3
        """
        if self.version >= 4:
            setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 9))
        else:
            print("WARNING: fsSelection bit 9 is only defined in OS/2 version 4 and up.")
            return

    def clear_oblique_bit(self):
        """
        Clears fsSelection bit 9 (OBLIQUE)
        """
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 9))

    # Embed level (OS/2.fsType bits 0-3)

    def set_embed_level(self, value: int) -> None:
        """
        Sets the embedding level (fsType bits 0-3) of the font

        :param value: The embedding level you want to set
        :type value: int
        """
        if value == 0:
            for b in (0, 1, 2, 3):
                setattr(self, "fsType", unset_nth_bit(self.fsType, b))
        elif value == 2:
            for b in (0, 2, 3):
                setattr(self, "fsType", unset_nth_bit(self.fsType, b))
            setattr(self, "fsType", set_nth_bit(self.fsType, 1))
        elif value == 4:
            for b in (0, 1, 3):
                setattr(self, "fsType", unset_nth_bit(self.fsType, b))
            setattr(self, "fsType", set_nth_bit(self.fsType, 2))
        elif value == 8:
            for b in (0, 1, 2):
                setattr(self, "fsType", unset_nth_bit(self.fsType, b))
            setattr(self, "fsType", set_nth_bit(self.fsType, 3))
        else:
            return

    def get_embed_level(self) -> int:
        """
        Converts the fsType value to a binary string, then takes the last 8 bits of that string, converts it to an
        integer, and returns it

        :return: The embedding level of the font.
        """
        return int(num2binary(self.fsType, 16)[9:17], 2)

    # No subsetting bit (OS/2.fsType bit 8)
    def is_no_subsetting_bit_set(self) -> bool:
        """
        > Returns True if the fsType bit 8 (NO_SUBSETTING) is set, otherwise False

        :return: A boolean value.
        """
        return is_nth_bit_set(self.fsType, 8)

    def set_no_subsetting_bit(self) -> None:
        """
        Sets fsType bit 8 (NO_SUBSETTING)
        """
        setattr(self, "fsType", set_nth_bit(self.fsType, 8))

    def clear_no_subsetting_bit(self) -> None:
        """
        Clears fsType bit 8 (NO_SUBSETTING)
        """
        setattr(self, "fsType", unset_nth_bit(self.fsType, 8))

    # Bitmap embedding only bit (OS/2.fsType bit 9)

    def is_bitmap_embed_only_bit_set(self) -> bool:
        """
        > Returns True if the fsType bit 9 (BITMAP_EMBEDDING_ONLY) is set, otherwise False

        :return: A boolean value.
        """
        return is_nth_bit_set(self.fsType, 9)

    def set_bitmap_embed_only_bit(self) -> None:
        """
        Sets fsType bit 9 (BITMAP_EMBEDDING_ONLY)
        """
        setattr(self, "fsType", set_nth_bit(self.fsType, 9))

    def clear_bitmap_embed_only_bit(self) -> None:
        """
        Clears fsType bit 9 (BITMAP_EMBEDDING_ONLY)
        """
        setattr(self, "fsType", unset_nth_bit(self.fsType, 9))

    def set_cap_height(self, cap_height: int) -> None:
        """
        Sets the sCapHeight value

        :param cap_height: Integer
        """
        if self.version >= 2:
            setattr(self, "sCapHeight", cap_height)

    def set_x_height(self, x_height: int) -> None:
        """
        Sets the sxHeight value

        :param x_height: Integer
        """
        if self.version >= 2:
            setattr(self, "sxHeight", x_height)

    def set_max_context(self, max_context: int) -> None:
        """
        Sets the usMaxContext value

        :param max_context: Integer
        """
        if self.version >= 2:
            setattr(self, "usMaxContext", max_context)

    def set_codepage_ranges(self, codepage_ranges) -> None:
        """
        Sets the ulCodePageRange1 and ulCodePageRange2 attributes if the OS/2 table version is greater than 1.

        :param codepage_ranges: A list of two integers. Each integer is a bitfield of the supported codepages
        """
        if self.version >= 1:
            setattr(self, "ulCodePageRange1", codepage_ranges[0])
            setattr(self, "ulCodePageRange2", codepage_ranges[1])

    def to_dict(self) -> dict:
        """
        Converts the OS/2 table to a dictionary

        :return: A dictionary of the OS/2 table.
        """
        os2_to_dict = {}
        for k, v in self.__dict__.items():
            if k in (
                "ulUnicodeRange1",
                "ulUnicodeRange2",
                "ulUnicodeRange3",
                "ulUnicodeRange4",
                "ulCodePageRange1",
                "ulCodePageRange2",
            ):
                value = num2binary(v)
            elif k in ("fsSelection", "fsType"):
                value = num2binary(v, 16)
            elif k == "panose":
                value = ", ".join([str(i) for i in v.__dict__.values()])
            else:
                value = str(v)
            os2_to_dict[k] = value

        return os2_to_dict

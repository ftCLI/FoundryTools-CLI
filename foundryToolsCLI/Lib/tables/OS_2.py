import typing as t

from fontTools.misc.textTools import num2binary
from fontTools.ttLib import registerCustomTableClass
from fontTools.ttLib.tables.O_S_2f_2 import table_O_S_2f_2

from foundryToolsCLI.Lib.constants import PANOSE_STRUCT
from foundryToolsCLI.Lib.utils.bits_tools import is_nth_bit_set, set_nth_bit, unset_nth_bit

registerCustomTableClass("OS/2", "foundryToolsCLI.Lib.tables.OS_2", "TableOS2")


class TableOS2(table_O_S_2f_2):
    def get_weight_class(self) -> int:
        """
        Returns the usWeightClass value
        """
        return getattr(self, "usWeightClass")

    def set_weight_class(self, value: int) -> None:
        """
        Sets the usWeightClass value

        :param value: Integer in range 1-1000
        :type value: int
        """
        if value not in range(1, 1001):
            return
        setattr(self, "usWeightClass", value)

    def get_width_class(self):
        """
        Returns the usWidthClass value
        """
        return getattr(self, "usWidthClass")

    def set_width_class(self, value: int) -> None:
        """
        Sets the usWidthClass value

        :param value: Integer in range 1-9
        :type value: int
        """
        if value not in range(1, 10):
            return
        setattr(self, "usWidthClass", value)

    def get_vend_id(self) -> str:
        """
        Returns the four characters Vendor Code

        :return: a string representing the Vendor identifier
        """
        return getattr(self, "achVendID")

    def set_vend_id(self, value: str) -> None:
        """
        Sets the achVendID value

        :param value: the four characters Vendor identifier
        :return: None
        """
        setattr(self, "achVendID", value.ljust(4, " ")[0:4])

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
        if self.version < 4:
            print("fsSelection bit 7 is only defined in OS/2 version 4 and up.")
            return
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 7))

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

    def set_wws_consistent_bit(self) -> None:
        """
        Sets fsSelection bit 8 (WWS) if OS/2 table version is greater than 3
        """
        if self.version < 4:
            print("WARNING: fsSelection bit 8 is only defined in OS/2 version 4 and up.")
            return
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 8))

    def clear_wws_consistent_bit(self) -> None:
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
        if self.version < 4:
            print("WARNING: fsSelection bit 9 is only defined in OS/2 version 4 and up.")
            return
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 9))

    def clear_oblique_bit(self):
        """
        Clears fsSelection bit 9 (OBLIQUE)
        """
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 9))

    def is_underscore_bit_set(self) -> bool:
        return is_nth_bit_set(self.fsSelection, 1)

    def set_underscore_bit(self) -> None:
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 1))

    def clear_underscore_bit(self) -> None:
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 1))

    def is_negative_bit_set(self) -> bool:
        return is_nth_bit_set(self.fsSelection, 2)

    def set_negative_bit(self) -> None:
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 2))

    def clear_negative_bit(self) -> None:
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 2))

    def is_outlined_bit_set(self) -> bool:
        return is_nth_bit_set(self.fsSelection, 3)

    def set_outlined_bit(self) -> None:
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 3))

    def clear_outlined_bit(self) -> None:
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 3))

    def is_strikeout_bit_set(self) -> bool:
        return is_nth_bit_set(self.fsSelection, 4)

    def set_strikeout_bit(self) -> None:
        setattr(self, "fsSelection", set_nth_bit(self.fsSelection, 4))

    def clear_strikeout_bit(self) -> None:
        setattr(self, "fsSelection", unset_nth_bit(self.fsSelection, 4))

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
        if self.version < 2:
            return
        setattr(self, "sCapHeight", cap_height)

    def set_x_height(self, x_height: int) -> None:
        """
        Sets the sxHeight value

        :param x_height: Integer
        """
        if self.version < 2:
            return
        setattr(self, "sxHeight", x_height)

    def set_max_context(self, max_context: int) -> None:
        """
        Sets the usMaxContext value

        :param max_context: Integer
        """
        if self.version < 2:
            return
        setattr(self, "usMaxContext", max_context)

    def set_default_char(self, default_char: int) -> None:
        """
        Sets the usDefaultChar value

        :param default_char: Integer
        """
        if self.version < 2:
            return
        setattr(self, "usDefaultChar", default_char)

    def set_break_char(self, break_char: int) -> None:
        """
        Sets the usBreakChar value

        :param break_char: Integer
        """
        if self.version < 2:
            return
        setattr(self, "usBreakChar", break_char)

    def set_codepage_ranges(self, codepage_ranges) -> None:
        """
        Sets the ulCodePageRange1 and ulCodePageRange2 attributes if the OS/2 table version is greater than 1.

        :param codepage_ranges: two bitfields of the supported codepages
        """
        if self.version < 1:
            return
        setattr(self, "ulCodePageRange1", codepage_ranges[0])
        setattr(self, "ulCodePageRange2", codepage_ranges[1])

    def get_codepage_ranges(self) -> t.Optional[t.Tuple[int, int]]:
        if self.version < 1:
            return None
        return getattr(self, "ulCodePageRange1"), getattr(self, "ulCodePageRange2")

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

    def panose_to_dict(self) -> dict:
        panose_dict = {}

        panose_family_type: int = self.panose.bFamilyType
        panose_data = PANOSE_STRUCT["bFamilyType"].get(panose_family_type)
        family_description: str = panose_data["description"]
        panose_dict.update(
            {"bFamilyType": f"Family Type: {panose_family_type} - {family_description}"}
        )

        family_sub_digits = panose_data["sub_digits"]
        for k in family_sub_digits.keys():
            sub_digit_description = family_sub_digits[k]["description"]
            sub_digit_value = getattr(self.panose, k)
            sub_digit_value_description = family_sub_digits[k]["values"].get(sub_digit_value)
            panose_dict.update(
                {k: f"{sub_digit_description}: {sub_digit_value} - {sub_digit_value_description}"}
            )

        return panose_dict

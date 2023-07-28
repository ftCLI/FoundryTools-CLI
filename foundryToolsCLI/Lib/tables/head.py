from fontTools.ttLib import registerCustomTableClass
from fontTools.ttLib.tables._h_e_a_d import table__h_e_a_d

from foundryToolsCLI.Lib.utils.bits_tools import is_nth_bit_set, set_nth_bit, unset_nth_bit

registerCustomTableClass("head", "foundryToolsCLI.Lib.tables.head", "TableHead")


class TableHead(table__h_e_a_d):
    def get_font_revision(self) -> float:
        """
        Returns the 'fontRevision' value in 'head' table

        :return: a float representing the font revision
        """
        return getattr(self, "fontRevision")

    def set_font_revision(self, value: float) -> None:
        """
        Sets 'fontRevision' value in 'head' table

        :param value: a float representing the font revision
        """
        setattr(self, "fontRevision", value)

    def is_bold_bit_set(self):
        return is_nth_bit_set(getattr(self, "macStyle"), 0)

    def set_bold_bit(self):
        setattr(self, "macStyle", set_nth_bit(getattr(self, "macStyle"), 0))

    def clear_bold_bit(self):
        setattr(self, "macStyle", unset_nth_bit(getattr(self, "macStyle"), 0))

    def is_italic_bit_set(self):
        return is_nth_bit_set(getattr(self, "macStyle"), 1)

    def set_italic_bit(self):
        setattr(self, "macStyle", set_nth_bit(getattr(self, "macStyle"), 1))

    def clear_italic_bit(self):
        setattr(self, "macStyle", unset_nth_bit(getattr(self, "macStyle"), 1))

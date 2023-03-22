from fontTools.ttLib.tables._h_e_a_d import table__h_e_a_d

from ftCLI.Lib.utils.misc import is_nth_bit_set, set_nth_bit, unset_nth_bit


class TableHead(table__h_e_a_d):
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

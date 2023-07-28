from fontTools.ttLib import registerCustomTableClass
from fontTools.ttLib.tables._p_o_s_t import table__p_o_s_t

registerCustomTableClass("post", "foundryToolsCLI.Lib.tables.post", "TablePost")


class TablePost(table__p_o_s_t):
    def set_italic_angle(self, value: float):
        setattr(self, "italicAngle", value)

    def set_underline_position(self, value: int):
        setattr(self, "underlinePosition", value)

    def set_underline_thickness(self, value: int):
        setattr(self, "underlineThickness", value)

    def set_fixed_pitch(self, value: bool):
        setattr(self, "isFixedPitch", int(value))

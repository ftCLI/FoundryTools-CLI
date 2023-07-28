from fontTools.ttLib import registerCustomTableClass
from fontTools.ttLib.tables._h_h_e_a import table__h_h_e_a

registerCustomTableClass("hhea", "foundryToolsCLI.Lib.tables.hhea", "TableHhea")


class TableHhea(table__h_h_e_a):
    def set_caret_slope_rise(self, value: int):
        setattr(self, "caretSlopeRise", value)

    def set_caret_slope_run(self, value: int):
        setattr(self, "caretSlopeRun", value)

    def set_caret_offset(self, value: int):
        setattr(self, "caretOffset", value)

    def set_ascent(self, value: int):
        setattr(self, "ascent", value)

    def set_descent(self, value: int):
        setattr(self, "descent", value)

    def set_linegap(self, value: int):
        setattr(self, "lineGap", value)

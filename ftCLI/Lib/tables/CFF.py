from fontTools.ttLib.tables.C_F_F_ import table_C_F_F_


class TableCFF(table_C_F_F_):
    def __init__(self, tag=None):
        super().__init__(tag)

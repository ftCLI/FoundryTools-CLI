from fontTools.subset import Subsetter


class BaseSubsetter(Subsetter):
    def __init__(self, glyph_ids: list):
        super().__init__()
        self.glyph_ids = glyph_ids
        self.options.drop_tables = []
        self.options.passthrough_tables = True
        self.options.name_IDs = "*"
        self.options.name_legacy = True
        self.options.name_languages = "*"
        self.options.layout_features = "*"
        self.options.hinting = False
        self.options.notdef_glyph = True
        self.options.notdef_outline = True
        self.glyph_ids_requested = self.glyph_ids

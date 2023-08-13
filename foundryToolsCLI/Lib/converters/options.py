class Options(object):
    def __init__(self):
        self.recalc_timestamp = False
        self.output_dir = None
        self.overwrite = True


class WebToSFNTOptions(Options):
    def __init__(self):
        super().__init__()
        self.woff = True
        self.woff2 = True


class SFNTToWebOptions(Options):
    def __init__(self):
        super().__init__()
        self.woff = True
        self.woff2 = True


class CFFToTrueTypeOptions(Options):
    def __init__(self):
        super().__init__()
        self.max_err = 1.0
        self.post_format = 2.0
        self.reverse_direction = True


class Var2StaticOptions(Options):
    def __init__(self):
        super().__init__()
        self.cleanup = True
        self.update_name_table = True


class TrueTypeToCFFOptions(Options):
    def __init__(self):
        super().__init__()
        self.tolerance: float = 1.0
        self.subroutinize = True
        self.scale_upm = False
        self.verbose = True


class TTCollectionToSFNTOptions(Options):
    def __init__(self):
        super().__init__()

from ftCLI.Lib.Font import Font


class WebToSFNT(object):
    def __init__(self, font: Font):
        self.font = font

    def run(self) -> Font:
        self.font.flavor = None
        return self.font

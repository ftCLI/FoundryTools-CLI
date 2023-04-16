from ftCLI.Lib.Font import Font


class SFNTToWeb(object):
    def __init__(self, font: Font, flavor: str):
        self.font = font
        self.flavor = flavor

    def run(self) -> Font:
        self.font.flavor = self.flavor
        return self.font

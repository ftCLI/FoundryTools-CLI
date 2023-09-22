from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.converters.options import SFNTToWebOptions
from foundryToolsCLI.Lib.utils.logger import logger, Logs


class FT2WFRunner(object):
    def __init__(self):
        super().__init__()
        self.options = SFNTToWebOptions()

    def run(self, fonts: list[Font]) -> None:
        converted_files_count = 0

        for font in fonts:
            try:
                if font.flavor is not None:
                    continue

                file = Path(font.reader.file.name)
                logger.opt(colors=True).info(Logs.converting_file, file=file)

                if self.options.woff:
                    converter = SFNTToWeb(font=font, flavor="woff")
                    web_font = converter.run()
                    extension = web_font.get_real_extension()
                    output_file = Path(
                        makeOutputFileName(
                            file,
                            extension=extension,
                            outputDir=self.options.output_dir,
                            overWrite=self.options.overwrite,
                        )
                    )
                    web_font.save(output_file, reorderTables=False)
                    logger.success(Logs.file_saved, file=output_file)
                    converted_files_count += 1

                if self.options.woff2:
                    converter = SFNTToWeb(font=font, flavor="woff2")
                    web_font = converter.run()
                    extension = web_font.get_real_extension()
                    output_file = Path(
                        makeOutputFileName(
                            file,
                            extension=extension,
                            outputDir=self.options.output_dir,
                            overWrite=self.options.overwrite,
                        )
                    )
                    web_font.save(output_file, reorderTables=False)
                    logger.success(Logs.file_saved, file=output_file)

            except Exception as e:
                logger.exception(e)
            finally:
                font.close()


class SFNTToWeb(object):
    def __init__(self, font: Font, flavor: str):
        self.font = font
        self.flavor = flavor

    def run(self) -> Font:
        self.font.flavor = self.flavor
        return self.font

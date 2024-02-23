from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.converters.options import WebToSFNTOptions
from foundryToolsCLI.Lib.utils.logger import logger, Logs


class WF2FTRunner(object):
    def __init__(self):
        super().__init__()
        self.options = WebToSFNTOptions()

    def run(self, fonts: list[Font]) -> None:
        for font in fonts:
            try:
                file = Path(font.reader.file.name)
                logger.opt(colors=True).info(Logs.converting_file, file=file)

                if not font.flavor:
                    continue
                if not self.options.woff:
                    if font.flavor == "woff":
                        continue
                if not self.options.woff2:
                    if font.flavor == "woff2":
                        continue

                font.flavor = None
                new_extension = font.get_real_extension()
                output_file = Path(
                    makeOutputFileName(
                        file,
                        extension=new_extension,
                        outputDir=self.options.output_dir,
                        overWrite=self.options.overwrite,
                    )
                )

                font.save(output_file, reorderTables=False)
                logger.success(Logs.file_saved, file=output_file)

            except Exception as e:
                logger.exception(e)
            finally:
                font.close()

from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTCollection

from foundryToolsCLI.Lib.utils.logger import logger, Logs
from foundryToolsCLI.Lib.converters.options import TTCollectionToSFNTOptions


class TTC2SFNTRunner(object):
    def __init__(self):
        super().__init__()
        self.options = TTCollectionToSFNTOptions()

    def run(self, tt_collections: list[TTCollection]) -> None:
        for ttc in tt_collections:
            try:
                for font in ttc.fonts:
                    font.recalcTimestamp = self.options.recalc_timestamp
                    file_name = font["name"].getDebugName(6)
                    extension = ".otf" if font.sfntVersion == "OTTO" else ".ttf"
                    logger.opt(colors=True).info(Logs.current_file, file=file_name + extension)
                    output_file = Path(
                        makeOutputFileName(
                            file_name,
                            outputDir=self.options.output_dir,
                            extension=extension,
                            overWrite=self.options.overwrite,
                        )
                    )

                    font.save(output_file)
                    logger.success(Logs.file_saved, file=output_file)
                    font.close()

            except Exception as e:
                logger.exception(e)
            finally:
                ttc.close()

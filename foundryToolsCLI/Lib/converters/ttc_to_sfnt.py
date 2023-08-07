import time
from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTCollection

from foundryToolsCLI.Lib.converters.options import TTCollectionToSFNTOptions
from foundryToolsCLI.Lib.utils.click_tools import generic_info_message, file_saved_message, generic_error_message


class TTC2SFNTRunner(object):
    def __init__(self):
        super().__init__()
        self.options = TTCollectionToSFNTOptions()

    def run(self, tt_collections: list[TTCollection]) -> None:
        extracted_files = 0
        start_time = time.time()

        for count, ttc in enumerate(tt_collections, start=1):
            t = time.time()
            try:
                print()
                generic_info_message(f"Converting file {count} of {len(tt_collections)}")

                for font in ttc.fonts:
                    font.recalcTimestamp = self.options.recalc_timestamp
                    file_name = font["name"].getDebugName(6)
                    extension = ".otf" if font.sfntVersion == "OTTO" else ".ttf"
                    output_file = Path(
                        makeOutputFileName(
                            file_name,
                            outputDir=self.options.output_dir,
                            extension=extension,
                            overWrite=self.options.overwrite,
                        )
                    )

                    font.save(output_file)
                    font.close()
                    generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")
                    file_saved_message(output_file)
                    extracted_files += 1

            except Exception as e:
                generic_error_message(e)
            finally:
                ttc.close()

        print()
        generic_info_message(f"Total TTC files : {len(tt_collections)}")
        generic_info_message(f"Extracted files : {extracted_files}")
        generic_info_message(f"Elapsed time    : {round(time.time() - start_time, 3)} seconds")

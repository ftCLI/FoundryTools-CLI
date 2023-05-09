import os.path
import time

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTCollection

from ftCLI.Lib.converters.options import TTCollectionToSFNTOptions
from ftCLI.Lib.utils.click_tools import generic_info_message, file_saved_message, generic_error_message


class JobRunner_ttc2sfnt(object):
    def __init__(self):
        super().__init__()
        self.options = TTCollectionToSFNTOptions()

    def run(self, files) -> None:
        count = 0
        extracted_files = 0
        start_time = time.time()

        for file in files:
            count += 1
            t = time.time()

            try:
                print()
                generic_info_message(f"Converting file {count} of {len(files)}: {os.path.basename(file)}")

                ttc = TTCollection(file)
                for font in ttc.fonts:
                    font.recalcTimestamp = self.options.recalc_timestamp
                    file_name = font["name"].getDebugName(6)
                    extension = ".otf" if font.sfntVersion == "OTTO" else ".ttf"
                    output_file = makeOutputFileName(
                        file_name,
                        outputDir=self.options.output_dir,
                        extension=extension,
                        overWrite=self.options.overwrite,
                    )
                    font.save(output_file)
                    generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")
                    file_saved_message(output_file)
                    extracted_files += 1

            except Exception as e:
                generic_error_message(e)

        print()
        generic_info_message(f"Total TTC files   : {len(files)}")
        generic_info_message(f"Extracted files   : {extracted_files}")
        generic_info_message(f"Elapsed time      : {round(time.time() - start_time, 3)} seconds")

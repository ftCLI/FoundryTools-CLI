import os
import time

from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.converters.options import WebToSFNTOptions
from ftCLI.Lib.Font import Font
from ftCLI.Lib.utils.click_tools import generic_info_message, generic_error_message, file_saved_message


class JobRunner_wf2ft(object):
    def __init__(self):
        super().__init__()
        self.options = WebToSFNTOptions()

    def run(self, files) -> None:
        count = 0
        converted_files_count = 0
        start_time = time.time()

        for file in files:
            t = time.time()
            count += 1

            try:
                print()
                generic_info_message(f"Converting file {count} of {len(files)}: {os.path.basename(file)}")
                font = Font(file, recalcTimestamp=self.options.recalc_timestamp)

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
                output_file = makeOutputFileName(
                    file,
                    extension=new_extension,
                    outputDir=self.options.output_dir,
                    overWrite=self.options.overwrite,
                )

                font.save(output_file)
                generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")
                file_saved_message(output_file)
                converted_files_count += 1

            except Exception as e:
                generic_error_message(e)

        print()
        generic_info_message(f"Total files       : {len(files)}")
        generic_info_message(f"Converted files   : {converted_files_count}")
        generic_info_message(f"Elapsed time      : {round(time.time() - start_time, 3)} seconds")

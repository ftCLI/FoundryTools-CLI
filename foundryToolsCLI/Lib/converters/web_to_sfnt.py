import time
from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.converters.options import WebToSFNTOptions
from foundryToolsCLI.Lib.utils.click_tools import generic_info_message, generic_error_message, file_saved_message


class WF2FTRunner(object):
    def __init__(self):
        super().__init__()
        self.options = WebToSFNTOptions()

    def run(self, fonts: list[Font]) -> None:
        converted_files_count = 0
        start_time = time.time()

        for count, font in enumerate(fonts, start=1):
            t = time.time()

            try:
                file = Path(font.reader.file.name)
                print()
                generic_info_message(f"Converting file {count} of {len(fonts)}: {file.name}")

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

                font.save(output_file)
                generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")
                file_saved_message(output_file)
                converted_files_count += 1

            except Exception as e:
                generic_error_message(e)
            finally:
                font.close()

        print()
        generic_info_message(f"Total files     : {len(fonts)}")
        generic_info_message(f"Converted files : {converted_files_count}")
        generic_info_message(f"Elapsed time    : {round(time.time() - start_time, 3)} seconds")

import os
import time

from fontTools.misc.cliTools import makeOutputFileName

from ftCLI.Lib.Font import Font
from ftCLI.Lib.converters.options import SFNTToWebOptions
from ftCLI.Lib.utils.click_tools import generic_info_message, file_saved_message, generic_error_message


class JobRunner_ft2wf(object):
    def __init__(self):
        super().__init__()
        self.options = SFNTToWebOptions()

    def run(self, files) -> None:
        count = 0
        for file in files:
            t = time.time()
            count += 1
            print()
            generic_info_message(f"Converting file {count} of {len(files)}: {os.path.basename(file)}")

            try:
                font = Font(file, recalcTimestamp=self.options.recalc_timestamp)

                if font.flavor is not None:
                    continue

                if self.options.woff:
                    converter = SFNTToWeb(font=font, flavor="woff")
                    web_font = converter.run()
                    extension = web_font.get_real_extension()
                    output_file = makeOutputFileName(
                        file, extension=extension, outputDir=self.options.output_dir, overWrite=self.options.overwrite
                    )
                    web_font.save(output_file, reorderTables=False)
                    file_saved_message(output_file)
                    generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")

                if self.options.woff2:
                    converter = SFNTToWeb(font=font, flavor="woff2")
                    web_font = converter.run()
                    extension = web_font.get_real_extension()
                    output_file = makeOutputFileName(
                        file, extension=extension, outputDir=self.options.output_dir, overWrite=self.options.overwrite
                    )
                    web_font.save(output_file, reorderTables=False)
                    file_saved_message(output_file)
                    generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")

            except Exception as e:
                generic_error_message(e)


class SFNTToWeb(object):
    def __init__(self, font: Font, flavor: str):
        self.font = font
        self.flavor = flavor

    def run(self) -> Font:
        self.font.flavor = self.flavor
        return self.font

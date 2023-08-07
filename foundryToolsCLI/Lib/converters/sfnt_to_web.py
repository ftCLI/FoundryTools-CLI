import time
from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.converters.options import SFNTToWebOptions
from foundryToolsCLI.Lib.utils.click_tools import generic_info_message, file_saved_message, generic_error_message


class FT2WFRunner(object):
    def __init__(self):
        super().__init__()
        self.options = SFNTToWebOptions()

    def run(self, fonts: list[Font]) -> None:
        converted_files_count = 0
        start_time = time.time()

        for count, font in enumerate(fonts, start=1):
            t = time.time()

            try:
                if font.flavor is not None:
                    continue

                file = Path(font.reader.file.name)
                print()
                generic_info_message(f"Converting file {count} of {len(fonts)}: {file.name}")

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
                    file_saved_message(output_file)
                    generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")
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
                    file_saved_message(output_file)
                    generic_info_message(f"Elapsed time: {round(time.time() - t, 3)} seconds")
                    converted_files_count += 1

            except Exception as e:
                generic_error_message(e)
            finally:
                font.close()

        print()
        generic_info_message(f"Total files     : {len(fonts)}")
        generic_info_message(f"Converted files : {converted_files_count}")
        generic_info_message(f"Elapsed time    : {round(time.time() - start_time, 3)} seconds")


class SFNTToWeb(object):
    def __init__(self, font: Font, flavor: str):
        self.font = font
        self.flavor = flavor

    def run(self) -> Font:
        self.font.flavor = self.flavor
        return self.font

from unittest import TestCase
import pathlib

from foundryToolsCLI.Lib.utils.cli_tools import (
    get_fonts_in_path,
    get_variable_fonts_in_path,
    get_style_mapping_path,
    get_fonts_data_path,
    get_project_files_path,
    get_output_dir,
    initial_check_pass
)

CWD = pathlib.Path.cwd()
INPUT_PATH = pathlib.Path.joinpath(CWD, "data")


class Test(TestCase):
    def test_get_fonts_in_path(self):
        fonts = get_fonts_in_path(input_path=INPUT_PATH)
        self.assertEqual(len(fonts), 5)
        fonts = get_fonts_in_path(input_path=INPUT_PATH, allow_static=False)
        self.assertEqual(len(fonts), 1)
        fonts = get_fonts_in_path(input_path=INPUT_PATH, allow_variable=False)
        self.assertEqual(len(fonts), 4)
        fonts = get_fonts_in_path(input_path=INPUT_PATH, allow_sfnt=False)
        self.assertEqual(len(fonts), 2)
        fonts = get_fonts_in_path(input_path=INPUT_PATH, allow_web_font=False)
        self.assertEqual(len(fonts), 3)
        fonts = get_fonts_in_path(input_path=INPUT_PATH, allow_cff=False)
        self.assertEqual(len(fonts), 4)
        fonts = get_fonts_in_path(input_path=INPUT_PATH, allow_ttf=False)
        self.assertEqual(len(fonts), 1)
        fonts = get_fonts_in_path(input_path=INPUT_PATH, allow_extensions=[".ttf", ".otf"])
        self.assertEqual(len(fonts), 3)
        fonts = get_fonts_in_path(input_path=INPUT_PATH, allow_extensions=[".woff"])
        self.assertEqual(len(fonts), 1)

    def test_get_variable_fonts_in_path(self):
        variable_fonts = get_variable_fonts_in_path(input_path=INPUT_PATH)
        self.assertEqual(len(variable_fonts), 1)

    def test_get_style_mapping_path(self):
        styles_mapping_path = get_style_mapping_path(input_path=INPUT_PATH)
        expected = pathlib.Path.joinpath(INPUT_PATH, "ftCLI_files", "styles_mapping.json")
        self.assertEqual(styles_mapping_path, expected)

    def test_get_fonts_data_path(self):
        fonts_data_path = get_fonts_data_path(input_path=INPUT_PATH)
        expected = pathlib.Path.joinpath(INPUT_PATH, "ftCLI_files", "fonts_data.csv")
        self.assertEqual(fonts_data_path, expected)

    def test_get_project_files_path(self):
        project_files_path = get_project_files_path(input_path=INPUT_PATH)
        expected = pathlib.Path.joinpath(INPUT_PATH, "ftCLI_files")
        self.assertEqual(project_files_path, expected)

    def test_get_output_dir(self):
        output_dir = get_output_dir(input_path=INPUT_PATH, output_dir=None)
        self.assertEqual(output_dir, INPUT_PATH)
        output_dir = get_output_dir(input_path=INPUT_PATH, output_dir=CWD)
        self.assertEqual(output_dir, CWD)

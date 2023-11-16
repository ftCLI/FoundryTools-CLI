import pathlib
import unittest

from fontTools.ttLib import newTable

from foundryToolsCLI.Lib.Font import Font
from foundryToolsCLI.Lib.tables.OS_2 import TableOS2


class TableOS2Test(unittest.TestCase):
    def test_set_weight_class(self):
        table: TableOS2 = newTable("OS/2")
        value = 700
        table.set_weight_class(value)
        self.assertEqual(table.get_weight_class(), value)
        table.set_weight_class(0)  # too low value
        self.assertEqual(table.get_weight_class(), value)
        table.set_weight_class(1001)  # too high value
        self.assertEqual(table.get_weight_class(), value)

    def test_set_width_class(self):
        table: TableOS2 = newTable("OS/2")
        value = 5
        table.set_width_class(value)
        self.assertEqual(table.get_width_class(), value)
        table.set_width_class(-1)  # too low value
        self.assertEqual(table.get_width_class(), value)
        table.set_width_class(10)  # too high value
        self.assertEqual(table.get_width_class(), value)

    def test_set_vend_id(self):
        table: TableOS2 = newTable("OS/2")
        value = "1234"
        table.set_vend_id(value)
        self.assertEqual(table.get_vend_id(), value)
        table.set_vend_id(f"{value}5678")
        self.assertEqual(table.get_vend_id(), value)
        value = "123"
        table.set_vend_id(value)
        self.assertEqual(table.get_vend_id(), "123 ")

    def test_flags(self):
        source_file = pathlib.Path.joinpath(
            pathlib.Path.cwd(), "data", "IBMPlexSerif-BoldItalic.ttf"
        )
        font = Font(source_file)
        table: TableOS2 = font["OS/2"]

        self.assertTrue(font.is_bold)
        self.assertTrue(font.is_italic)
        self.assertFalse(font.is_regular)

        font.set_bold_flag(False)
        self.assertFalse(font.is_bold)
        self.assertTrue(font.is_italic)
        self.assertFalse(font.is_regular)

        font.set_italic_flag(False)
        self.assertFalse(font.is_bold)
        self.assertFalse(font.is_italic)
        self.assertTrue(font.is_regular)

        font.set_bold_flag(True)
        font.set_italic_flag(True)
        font.set_regular_flag(True)
        self.assertFalse(font.is_bold)
        self.assertFalse(font.is_italic)
        self.assertTrue(font.is_regular)

        font.set_oblique_flag(True)
        self.assertTrue(font.is_oblique)
        self.assertTrue(font.is_regular)

        table.set_use_typo_metrics_bit()
        self.assertEqual(table.is_use_typo_metrics_bit_set(), True)
        table.clear_use_typo_metrics_bit()
        self.assertEqual(table.is_use_typo_metrics_bit_set(), False)

        table.set_wws_consistent_bit()
        self.assertEqual(table.is_wws_bit_set(), True)
        table.clear_wws_consistent_bit()
        self.assertEqual(table.is_wws_bit_set(), False)

        table.set_oblique_bit()
        self.assertEqual(table.is_oblique_bit_set(), True)
        table.clear_oblique_bit()
        self.assertEqual(table.is_oblique_bit_set(), False)

        table.set_underscore_bit()
        self.assertEqual(table.is_underscore_bit_set(), True)
        table.clear_underscore_bit()
        self.assertEqual(table.is_underscore_bit_set(), False)

        table.set_negative_bit()
        self.assertEqual(table.is_negative_bit_set(), True)
        table.clear_negative_bit()
        self.assertEqual(table.is_negative_bit_set(), False)

        table.set_outlined_bit()
        self.assertEqual(table.is_outlined_bit_set(), True)
        table.clear_outlined_bit()
        self.assertEqual(table.is_outlined_bit_set(), False)

        table.set_strikeout_bit()
        self.assertEqual(table.is_strikeout_bit_set(), True)
        table.clear_strikeout_bit()
        self.assertEqual(table.is_strikeout_bit_set(), False)

        table.set_no_subsetting_bit()
        self.assertEqual(table.is_no_subsetting_bit_set(), True)
        table.clear_no_subsetting_bit()
        self.assertEqual(table.is_no_subsetting_bit_set(), False)

        table.set_bitmap_embed_only_bit()
        self.assertEqual(table.is_bitmap_embed_only_bit_set(), True)
        table.clear_bitmap_embed_only_bit()
        self.assertEqual(table.is_bitmap_embed_only_bit_set(), False)

    def test_embed_level(self):
        source_file = pathlib.Path.joinpath(
            pathlib.Path.cwd(), "data", "IBMPlexSerif-BoldItalic.ttf"
        )
        font = Font(source_file)
        table: TableOS2 = font["OS/2"]

        embed_level = table.get_embed_level()
        table.set_embed_level(3)
        self.assertEqual(table.get_embed_level(), embed_level)

        for i in (0, 2, 4, 8):
            table.set_embed_level(i)
            self.assertEqual(table.get_embed_level(), i)

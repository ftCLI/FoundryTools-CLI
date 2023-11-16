from fontTools.ttLib import registerCustomTableClass
from fontTools.ttLib.tables.C_F_F_ import table_C_F_F_

registerCustomTableClass("CFF ", "foundryToolsCLI.Lib.tables.CFF_", "TableCFF")


class TableCFF(table_C_F_F_):
    def get_font_version(self) -> str:
        """
        Returns the cff.topDictIndex[0].version value

        :return: a string representing the cff.topDictIndex[0].version
        """
        return self.cff.topDictIndex[0].version

    def set_font_version(self, value: str) -> None:
        """
        Sets the cff.topDictIndex[0].version value

        :param value: a string representing the new cff.topDictIndex[0].version
        """
        setattr(self.cff.topDictIndex[0], "version", value)

    def del_top_dict_names(self, names: list[str]) -> None:
        """
        Deletes names from topDictIndex[0]

        :param names: a list of names
        """
        top_dict = self.cff.topDictIndex[0]
        for name in names:
            try:
                del top_dict.rawDict[name]
            except KeyError:
                pass

    def set_top_dict_names(self, names: dict[str, str]) -> None:
        top_dict = self.cff.topDictIndex[0]
        if "fontNames" in names.keys():
            self.cff.fontNames = [names.get("fontNames")]
            del names["fontNames"]
        for attr_name, attr_value in names.items():
            setattr(top_dict, attr_name, attr_value)

    def top_dict_find_replace(self, old_string: str, new_string: str) -> None:
        cff_font_names = self.cff.fontNames[0]
        self.cff.fontNames = [
            cff_font_names.replace(old_string, new_string).replace("  ", " ").strip()
        ]
        top_dict = self.cff.topDictIndex[0]
        attr_list = [
            "version",
            "FullName",
            "FamilyName",
            "Weight",
            "Copyright",
            "Notice",
        ]
        for attr_name in attr_list:
            try:
                old_value = str(getattr(top_dict, attr_name))
                new_value = old_value.replace(old_string, new_string).replace("  ", " ").strip()
                setattr(top_dict, attr_name, new_value)
            except AttributeError:
                pass

    def get_fb_ps_name(self) -> str:
        """
        Returns the psName to pass to FontBuilder

        :return: a string representing the font's ps name
        """
        return self.cff.fontNames[0]

    def get_fb_font_info(self) -> dict:
        """
        Returns the fontInfo dict to pass to FontBuilder

        :return: the font info dict
        """
        font_info = {
            key: value
            for key, value in self.cff.topDictIndex[0].rawDict.items()
            if key not in ("FontBBox", "charset", "Encoding", "Private", "CharStrings")
        }
        return font_info

    def get_fb_private_dict(self) -> dict:
        """
        Returns the font privateDict to pass to FontBuilder

        :return: the font info dict
        """
        private_dict = {
            key: value
            for key, value in self.cff.topDictIndex[0].Private.rawDict.items()
            if key not in ("Subrs", "defaultWidthX", "nominalWidthX")
        }
        return private_dict

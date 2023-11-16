from fontTools.ttLib import registerCustomTableClass
from fontTools.ttLib.tables._n_a_m_e import (
    table__n_a_m_e,
    NameRecord,
    _MAC_LANGUAGE_CODES,
    _WINDOWS_LANGUAGE_CODES,
)

registerCustomTableClass("name", "foundryToolsCLI.Lib.tables.name", "TableName")


class TableName(table__n_a_m_e):
    def add_name(
        self,
        font,
        string,
        name_id: int = None,
        platform_id: int = None,
        language_string: str = "en",
    ) -> None:
        """
        Adds a NameRecord to the `name` table. If the NameRecord already exists, it will be overwritten.

        :param font: the font object
        :param string: The string to be written to the NameRecord
        :param name_id: The name ID of the NameRecord to be added
        :type name_id: int
        :param platform_id: 1 = Macintosh, 3 = Windows
        :type platform_id: int
        :param language_string: The language of the string, defaults to en
        :type language_string: str (optional)
        """

        # Remove the NameRecord before writing it to avoid duplicates
        self.del_names(name_ids=[name_id], platform_id=platform_id, language_string=language_string)

        if platform_id == 1:
            mac, windows = True, False
        elif platform_id == 3:
            mac, windows = False, True
        else:
            mac, windows = True, True

        names = {language_string: string}

        self.addMultilingualName(names, ttFont=font, nameID=name_id, windows=windows, mac=mac)

    def del_names(self, name_ids, platform_id=None, language_string=None) -> None:
        """
        Deletes all name records that match the given name_ids, optionally filtering by platform_id and/or
        language_string.

        :param name_ids: A list of name IDs to delete
        :param platform_id: The platform ID of the name records to delete
        :param language_string: The language of the name records to delete
        """

        names = self.filter_namerecords(
            name_ids=name_ids, platform_id=platform_id, lang_string=language_string
        )

        for name in names:
            self.removeNames(name.nameID, name.platformID, name.platEncID, name.langID)

    def filter_namerecords(
        self, name_ids=None, platform_id=None, plat_enc_id=None, lang_id=None, lang_string=None
    ) -> list[NameRecord]:
        """
        It takes a list of name records, and returns a list of name records that match the given criteria

        :param name_ids: A list of name IDs to filter by
        :param platform_id: The platform ID of the name record
        :param plat_enc_id: The platform-specific encoding ID
        :param lang_id: The language ID of the name record
        :param lang_string: The string to search for in the name records
        :return: A list of name records.
        """
        filtered_names = self.names
        if name_ids is not None:
            filtered_names = [name for name in filtered_names if name.nameID in name_ids]
        if platform_id is not None:
            filtered_names = [name for name in filtered_names if name.platformID == platform_id]
        if plat_enc_id is not None:
            filtered_names = [name for name in filtered_names if name.platEncID == plat_enc_id]
        if lang_id is not None:
            filtered_names = [name for name in filtered_names if name.langID == lang_id]
        if lang_string is not None:
            mac_lang_id = _MAC_LANGUAGE_CODES.get(lang_string.lower())
            win_lang_id = _WINDOWS_LANGUAGE_CODES.get(lang_string.lower())
            filtered_names = [
                name for name in filtered_names if name.langID in (mac_lang_id, win_lang_id)
            ]
        return filtered_names

    def find_replace(
        self,
        old_string: str,
        new_string: str,
        name_ids_to_include: tuple = (),
        name_ids_to_skip: tuple = (),
        platform_id: int = None,
    ):
        """
        This function will find and replace a string in the specified namerecords.

        :param old_string: The string to be replaced
        :type old_string: str
        :param new_string: The string to replace the old string with
        :type new_string: str
        :param name_ids_to_include: A tuple of nameIDs to include in the search. If left blank, all nameIDs will be
            included
        :type name_ids_to_include: tuple
        :param name_ids_to_skip: A tuple of nameIDs to skip in the search. If left blank, no nameID will be skipped
        :type name_ids_to_skip: tuple
        :param platform_id: The platform ID of the name record to be changed
        :type platform_id: int
        """

        name_ids = [name.nameID for name in self.names]

        if name_ids_to_include != ():
            name_ids = [name.nameID for name in self.names if name.nameID in name_ids_to_include]

        if name_ids_to_skip != ():
            name_ids = [name.nameID for name in self.names if name.nameID not in name_ids_to_skip]

        names = self.filter_namerecords(name_ids=name_ids, platform_id=platform_id)

        for name in self.names:
            if name in names:
                if old_string in str(name):
                    string = str(name).replace(old_string, new_string).replace("  ", " ").strip()
                    self.setName(
                        string,
                        name.nameID,
                        name.platformID,
                        name.platEncID,
                        name.langID,
                    )

    def append_string(
        self, name_ids, platform_id=None, language_string=None, prefix=None, suffix=None
    ) -> None:
        """
        Appends a prefix, a suffix, or both to the namerecords that match the name IDs, platform ID, and language
        string.

        :param name_ids: A list of name IDs to filter by
        :param platform_id: The platform ID of the namerecords where to append/prepend the string
        :param language_string: The language string to filter by
        :param prefix: The string to be added to the beginning of the namerecords
        :param suffix: The string to append to the end of the namerecords
        """

        names = self.filter_namerecords(
            name_ids=name_ids, platform_id=platform_id, lang_string=language_string
        )

        for name in names:
            string = name.toUnicode()
            if prefix is not None:
                string = f"{prefix}{string}"
            if suffix is not None:
                string = f"{string}{suffix}"

            self.setName(
                string=string,
                nameID=name.nameID,
                platformID=name.platformID,
                platEncID=name.platEncID,
                langID=name.langID,
            )

    def remove_leading_trailing_spaces(self):
        for name in self.names:
            self.setName(
                str(name).strip(),
                name.nameID,
                name.platformID,
                name.platEncID,
                name.langID,
            )

    def remove_empty_names(self):
        for name in self.names:
            if str(name).strip() == "":
                self.removeNames(
                    nameID=name.nameID,
                    platformID=name.platformID,
                    platEncID=name.platEncID,
                    langID=name.langID,
                )

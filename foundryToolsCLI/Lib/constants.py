from fontTools.ttLib.tables._n_a_m_e import _WINDOWS_LANGUAGES, _MAC_LANGUAGES

NAME_IDS = {
    0: "Copyright Notice",
    1: "Family name",
    2: "Subfamily name",
    3: "Unique identifier",
    4: "Full font name",
    5: "Version string",
    6: "PostScript name",
    7: "Trademark",
    8: "Manufacturer Name",
    9: "Designer",
    10: "Description",
    11: "URL Vendor",
    12: "URL Designer",
    13: "License Description",
    14: "License Info URL",
    15: "Reserved",
    16: "Typographic Family",
    17: "Typographic Subfamily",
    18: "Compatible Full (Mac)",
    19: "Sample text",
    20: "PS CID font name",
    21: "WWS Family Name",
    22: "WWS Subfamily Name",
    23: "Light Background Palette",
    24: "Dark Background Palette",
    25: "Variations PSName Pref",
}

PLATFORMS = {
    0: "Unicode",
    1: "Macintosh",
    2: "ISO (deprecated)",
    3: "Windows",
    4: "Custom",
}

MAC_ENCODING_IDS = {
    0: "Roman",
    1: "Japanese",
    2: "Chinese (Traditional)",
    3: "Korean",
    4: "Arabic",
    5: "Hebrew",
    6: "Greek",
    7: "Russian",
    8: "RSymbol",
    9: "Devanagari",
    10: "Gurmukhi",
    11: "Gujarati",
    12: "Oriya",
    13: "Bengali",
    14: "Tamil",
    15: "Telugu",
    16: "Kannada",
    17: "Malayalam",
    18: "Sinhalese",
    19: "Burmese",
    20: "Khmer",
    21: "Thai",
    22: "Laotian",
    23: "Georgian",
    24: "Armenian",
    25: "Chinese (Simplified)",
    26: "Tibetan",
    27: "Mongolian",
    28: "Geez",
    29: "Slavic",
    30: "Vietnamese",
    31: "Sindhi",
    32: "Uninterpreted",
}

WINDOWS_ENCODING_IDS = {
    0: "Symbol",
    1: "Unicode",
    2: "ShiftJIS",
    3: "PRC",
    4: "Big5",
    5: "Wansung",
    6: "Johab",
    7: "Reserved",
    8: "Reserved",
    9: "Reserved",
    10: "UCS4",
}

EMBED_LEVEL_STRINGS = {
    0: "Installable embedding",
    2: "Restricted License embedding",
    4: "Preview & Print embedding",
    8: "Editable embedding",
}

MAX_FAMILY_NAME_LEN = 27
MAX_FULL_NAME_LEN = 31
MAX_POSTSCRIPT_NAME_LEN = 29

LANGUAGES_EPILOG = f"""
MACINTOSH LANGUAGES: {", ".join([lang for lang in _MAC_LANGUAGES.values()])}

WINDOWS LANGUAGES: f{", ".join([lang for lang in _WINDOWS_LANGUAGES.values()])}
"""

# ruff: noqa: C901
import re
from pathlib import Path

from foundrytools import Font
from pathvalidate import sanitize_filename

from foundrytools_cli.utils.logger import logger


def _apply_533_rule(postscript_name: str) -> str:
    """
    Apply the Macintosh LaserWriter Font Naming (LWFN) 5:3:3 rule.

    The rule divides the font name into "words" where each uppercase letter begins
    a new word. The file name is derived by:
    - Taking the initial uppercase letter and up to 4 lowercase letters in the first word
    - Taking the initial uppercase letter and up to 2 lowercase letters for subsequent words
    - Dropping hyphens between family and style portions

    Args:
        postscript_name: The PostScript name (e.g., "Helvetica-BoldOblique")

    Returns:
        The abbreviated filename following the 5:3:3 rule (e.g., "HelveBolObl")

    Examples:
        >>> _apply_533_rule("Helvetica-BoldOblique")
        'HelveBolObl'
        >>> _apply_533_rule("AGaramond-Bold")
        'AGarBol'
        >>> _apply_533_rule("Palatino-Roman")
        'PalatRom'
        >>> _apply_533_rule("Optima")
        'Optim'
    """
    # Remove hyphens to get a continuous string
    name_without_hyphens = postscript_name.replace("-", "")

    # Split into words where each uppercase letter begins a new word
    # This regex finds: uppercase letter followed by any number of lowercase letters
    words = re.findall(r"[A-Z][a-z]*", name_without_hyphens)

    if not words:
        # Fallback for invalid/unusual PostScript names without uppercase letters.
        # PostScript font names should start with uppercase per Adobe spec, but we handle
        # the edge case gracefully. The 11-char limit approximates typical LWFN length
        # (5+3+3 for a three-word name like FamilyStyleVariant).
        MAX_FALLBACK_LENGTH = 11
        return name_without_hyphens[:MAX_FALLBACK_LENGTH]

    result = []
    for i, word in enumerate(words):
        if i == 0:
            # First word: take up to 5 characters (1 uppercase + 4 lowercase)
            result.append(word[:5])
        else:
            # Subsequent words: take up to 3 characters (1 uppercase + 2 lowercase)
            result.append(word[:3])

    return "".join(result)


def _get_file_stem(font: Font, source: int = 1) -> str:
    """
    Get the best file name for a font.

    Args:
        source (int, optional): The source string(s) from which to extract the new file name.
            Default is 1 (FamilyName-StyleName), used also as fallback name when 4 or 5 are
            passed but the font is TrueType.

            1: FamilyName-StyleName
            2: PostScript Name
            3: Full Font Name
            4: CFF fontNames (CFF fonts only)
            5: CFF TopDict FullName (CFF fonts only)
            6: Macintosh LWFN (LaserWriter Font Naming) using 5:3:3 rule

    Returns:
        A sanitized file name for the font.
    """

    if font.is_variable:
        family_name = font.t_name.table.getBestFamilyName().replace(" ", "").strip()
        if font.flags.is_italic:
            family_name += "-Italic"
        axes = font.t_fvar.table.axes
        if not axes:
            raise RuntimeError("No axes found in the variable font.")
        file_name = f"{family_name}[{','.join([axis.axisTag for axis in axes])}]"
        return sanitize_filename(file_name, platform="auto")

    if font.is_tt and source in (4, 5):
        source = 1
    if source == 1:
        family_name = str(font.t_name.table.getBestFamilyName())
        subfamily_name = str(font.t_name.table.getBestSubFamilyName())
        file_name = f"{family_name}-{subfamily_name}".replace(" ", "").replace(".", "")
    elif source == 2:
        file_name = str(font.t_name.table.getDebugName(6))
    elif source == 3:
        file_name = str(font.t_name.table.getBestFullName())
    elif source == 4 and font.is_ps:
        file_name = font.t_cff_.table.cff.fontNames[0]
    elif source == 5 and font.is_ps:
        file_name = font.t_cff_.top_dict.FullName
    elif source == 6:
        # Build name from family and subfamily for LWFN 5:3:3 rule
        family_name = str(font.t_name.table.getBestFamilyName())
        subfamily_name = str(font.t_name.table.getBestSubFamilyName())
        font_name = f"{family_name}-{subfamily_name}".replace(" ", "").replace(".", "")
        file_name = _apply_533_rule(font_name)
    else:
        raise ValueError("Invalid source value.")
    return sanitize_filename(file_name, platform="auto")


def main(font: Font, source: int = 1, overwrite: bool = False) -> None:
    """
    Renames the given font files.
    """
    if font.file is None:
        raise AttributeError("Font file is None")
    old_file = font.file
    if source in (4, 5) and font.is_tt:
        logger.warning(
            f"source=4 and source=5 can be used for OTF files only. Using source=1 for "
            f"{old_file.name}"
        )
    new_file_name = sanitize_filename(_get_file_stem(font=font, source=source))
    new_file = font.get_file_path(
        file=Path(new_file_name),
        extension=font.get_file_ext(),
        output_dir=old_file.parent,
        overwrite=overwrite,
    )
    if new_file == old_file:
        logger.skip(f"{old_file.name} is already named correctly")  # type: ignore
        return
    if new_file.exists():
        logger.warning(f"Another file named {new_file.name} already exists")
        logger.skip(f"{old_file.name} was not renamed")  # type: ignore
        return
    try:
        old_file.rename(new_file)
        logger.opt(colors=True).info(
            f"<light-black>{old_file.name}</> --> <bold><magenta>{new_file.name}</></>"
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Error renaming {old_file.name}: {e}")
        return

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Union, get_type_hints

from foundrytools import Font
from foundrytools.lib.font_finder import (
    FinderError,
    FinderFilter,
    FinderOptions,
    FontFinder,
)

from foundrytools_cli.utils.logger import logger
from foundrytools_cli.utils.timer import Timer


class FontSaveError(Exception):
    """Raised when there is an error saving a font"""


class NoFontsFoundError(Exception):
    """Raised when no fonts are found by the FontFinder"""


@dataclass
class SaveOptions:
    """
    A class that specifies how to save the font.
    """

    reorder_tables: Optional[bool] = True
    suffix: str = ""
    output_dir: Optional[Path] = None
    overwrite: bool = False


class TaskRunnerConfig:  # pylint: disable=too-few-public-methods
    """
    Handle options for TaskRunner.
    """

    def __init__(self, task_callable: Callable, options: dict[str, Any]):
        self.task = task_callable
        self.filter = FinderFilter()
        self.finder_options = FinderOptions()
        self.save_options = SaveOptions()
        self.task_options: dict[str, Any] = {}
        self._handle_options(options)

    def _handle_options(self, options: dict[str, Any]) -> None:
        self._parse_finder_options(options)
        self._parse_save_options(options)
        self._parse_task_options(options)

    def _parse_finder_options(self, options: dict[str, Any]) -> None:
        self._set_options(self.finder_options, options)

    def _parse_save_options(self, options: dict[str, Any]) -> None:
        self._set_options(self.save_options, options)

    def _parse_task_options(self, options: dict[str, Any]) -> None:
        if "kwargs" in get_type_hints(self.task):
            self.task_options.update(
                {
                    k: v
                    for k, v in options.items()
                    if k not in get_type_hints(FinderOptions)
                    and k not in get_type_hints(SaveOptions)
                }
            )
        for key, value in options.items():
            if key in get_type_hints(self.task):
                self.task_options.update({key: value})

    @staticmethod
    def _set_options(
        options_group: Union[dict, FinderOptions, SaveOptions], options: dict[str, Any]
    ) -> None:
        """
        Update attributes of an options_group with provided options if the attribute exists.
        """
        for key, value in options.items():
            if hasattr(options_group, key):
                setattr(options_group, key, value)


class TaskRunner:  # pylint: disable=too-few-public-methods
    """
    A class for running tasks on multiple fonts.

    Attributes:
        input_path (Path): The input path to search for fonts.
        task (Callable): The task to be executed.
        filter (FinderFilter): The filter to apply to the FontFinder.
        save_if_modified (bool): Whether to save the font if it has been modified. Set to False
            when the saving process is handled by the task itself. Defaults to True.
        force_modified (bool): Whether to force the font to be saved even if it has not been
            modified. Set to True when it's not possible to determine if the font has been modified,
            or when it's too expensive to check. Defaults to False.
        config (TaskRunnerConfig): A configuration object containing FinderOptions, SaveOptions,
            and specific task options.
    """

    def __init__(
        self,
        input_path: Path,
        task: Callable,
        **options: dict[str, Any],
    ) -> None:
        """
        Initialize a new instance of the class.

        Args:
            input_path (Path): The input path to search for fonts.
            task (Callable): The task to be executed.
            **options (Dict[str, Any]): A dictionary containing the options to be parsed.
        """
        self.input_path = input_path
        self.task = task
        self.filter = FinderFilter()
        self.save_if_modified = True
        self.force_modified = False
        self.config = TaskRunnerConfig(options=options, task_callable=task)

    @Timer(logger=logger.opt(colors=True).info, text="Elapsed time <cyan>{:0.4f} seconds</>")
    def run(self) -> None:
        """
        Executes a task processing multiple fonts.
        """
        try:
            fonts = self._find_fonts()
        except (FinderError, NoFontsFoundError) as e:
            logger.error(e)
            return

        timer = Timer(
            logger=logger.opt(colors=True).info,
            text="Processing time: <cyan>{:0.4f} seconds</>",
        )
        for font in fonts:
            self._process_font(font, timer=timer)

    def _find_fonts(self) -> list[Font]:
        finder = FontFinder(
            input_path=self.input_path, options=self.config.finder_options, filter_=self.filter
        )
        fonts = finder.find_fonts()
        if not fonts:
            raise NoFontsFoundError(f"No fonts found in {self.input_path}")
        return fonts

    def _process_font(self, font: Font, timer: Timer) -> None:
        with font:
            timer.start()
            logger.info(f"Processing file {font.file}")
            task_result = bool(self._execute_task(font))
            self._save_or_skip(font, task_status=task_result)
            timer.stop()
            print()  # add a newline after each font

    def _execute_task(self, font: Font) -> bool:
        try:
            return bool(self.task(font, **self.config.task_options))
        except Exception as e:  # pylint: disable=broad-except
            self._log_error(e)
            return False

    def _save_or_skip(self, font: Font, task_status: bool) -> None:
        if not self._font_should_be_saved(task_status=task_status):
            if self.save_if_modified:
                logger.skip("No changes made")  # type: ignore
        else:
            self._save_font_to_file(font)

    def _font_should_be_saved(self, task_status: bool) -> bool:
        return (self.save_if_modified and task_status) or self.force_modified

    def _save_font_to_file(self, font: Font) -> None:
        try:
            out_file = self._get_out_file_name(font)
            font.save(out_file, reorder_tables=self.config.save_options.reorder_tables)
            logger.success(f"File saved to {out_file}")
        except Exception as e:  # pylint: disable=broad-except
            self._log_error(e)

    def _get_out_file_name(self, font: Font) -> Path:
        return font.get_file_path(
            output_dir=self.config.save_options.output_dir,
            extension=font.get_file_ext(),
            overwrite=self.config.save_options.overwrite,
            suffix=self.config.save_options.suffix,
        )

    @staticmethod
    def _log_error(e: Exception) -> None:
        if hasattr(e, "__module__"):
            logger.opt(colors=True).error(f"<lr>{e.__module__}.{type(e).__name__}</lr>: {e}")
        else:
            logger.opt(colors=True).error(f"<lr>{type(e).__name__}</lr>: {e}")

"""A module that defines common command behaviors."""

import re
from typing import Any

from oudjat.utils import Context
from oudjat.utils.file_utils import FileUtils


class Base:
    """A base command."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, options: dict[str, Any], *args: Any, **kwargs: Any) -> None:
        """
        Create a new Base command instance.

        Args:
            options (dict): A dictionary of configuration options for the command.
            args (tuple): Positional arguments passed to the constructor.
            kwargs (dict): Keyword arguments passed to the constructor.

        This method initializes the instance variables `options`, `args`, and `kwargs`.
        """

        self._options: dict[str, Any] = options
        self._args: tuple[Any, ...] = args
        self._kwargs: dict[str, Any] = kwargs

    # ****************************************************************
    # Methods

    @property
    def options(self) -> dict[str, Any]:
        """
        Return the base command options.

        Returns:
            dict[str, Any]: options passed to the command
        """

        return self._options

    @property
    def args(self) -> tuple[Any, ...]:
        """
        Return the args passed to the command.

        Returns:
            tuple[Any, ...]: additional non-named arguments passed to the command
        """

        return self._args

    @property
    def kwargs(self) -> dict[str, Any]:
        """
        Return the args passed to the command.

        Returns:
            dict[str, Any]: additional named arguments passed to the command
        """

        return self._kwargs

    def _is_opt_present(self, opt: str) -> bool:
        """
        Check if the option is present.

        Args:
            opt (str): Option to check the presence of

        Returns:
            bool: True if the option is present. False otherwise
        """

        return bool(self.options.get(opt) or False)

    def _unify_str_opt(self, str_opt: str, file_opt: str) -> list[str]:
        """
        Unify option case where a list of information can be passed either as a string, a list of strings or a txt file.

        Args:
            str_opt (str) : The key in the `self.options` dictionary where the resulting list should be stored.
            file_opt (str): The key in the `self.options` dictionary that, if exists, points to a file path.

        Returns:
            list[str]: A cleaned list of strings
        """

        args = (
            FileUtils.import_txt(filepath=self.options[file_opt])
            if self.options[file_opt]
            else self.options[str_opt].split(",")
        )

        return list(filter(None, args))

    def _ensure_json(self, json_str: str) -> str:
        """
        Ensure the provided string is a valid json string.

        Args:
            json_str (str): string to JSONify

        Returns:
            str: Valid JSON string
        """

        return re.sub(r'(\w+)(?=\s*:)', r'"\1"', json_str)

    def run(self) -> None:
        """
        Run method to be implemented by subclasses.

        Raises:
            NotImplementedError: Indicates that the `run` method must be overridden in any subclass.
        """

        raise NotImplementedError(
            f"{Context()}::Method must be implemented by the overloading class"
        )

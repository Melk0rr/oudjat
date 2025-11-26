"""A module that defines common command behaviors."""

from typing import Any

from oudjat.utils import Context


class Base(object):
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

    def run(self) -> None:
        """
        Run method to be implemented by subclasses.

        Raises:
            NotImplementedError: Indicates that the `run` method must be overridden in any subclass.
        """

        raise NotImplementedError(
            f"{Context()}::Method must be implemented by the overloading class"
        )

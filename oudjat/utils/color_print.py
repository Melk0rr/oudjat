"""A module that provide simple ways to change output color."""

from typing import Any


class ColorPrint:
    """A utility class to provide colored text output in the terminal."""

    RED: str = "\033[91m"
    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    BLUE: str = "\033[94m"
    PURPLE: str = "\033[95m"
    END: str = "\033[0m"

    @classmethod
    def white(cls, s: str, **kwargs: Any) -> None:
        """
        Print the string `s` in default color (white).

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(s, **kwargs)

    @classmethod
    def red(cls, s: str, **kwargs: Any) -> None:
        """
        Print the string `s` in red color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(cls.RED + s + cls.END, **kwargs)

    @classmethod
    def green(cls, s: str, **kwargs: Any) -> None:
        """
        Print the string `s` in green color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(cls.GREEN + s + cls.END, **kwargs)

    @classmethod
    def yellow(cls, s: str, **kwargs: Any) -> None:
        """
        Print the string `s` in yellow color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(cls.YELLOW + s + cls.END, **kwargs)

    @classmethod
    def blue(cls, s: str, **kwargs: Any) -> None:
        """
        Print the string `s` in blue color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(cls.BLUE + s + cls.END, **kwargs)

    @classmethod
    def purple(cls, s: str, **kwargs: Any) -> None:
        """
        Print the string `s` in purple color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(cls.PURPLE + s + cls.END, **kwargs)

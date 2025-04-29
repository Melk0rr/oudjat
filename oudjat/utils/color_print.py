class ColorPrint:
    """A utility class to provide colored text output in the terminal."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    END = "\033[0m"

    @classmethod
    def white(self, s: str, **kwargs) -> None:
        """
        Prints the string `s` in default color (white).

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(s, **kwargs)

    @classmethod
    def red(self, s: str, **kwargs) -> None:
        """
        Prints the string `s` in red color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(self.RED + s + self.END, **kwargs)

    @classmethod
    def green(self, s: str, **kwargs) -> None:
        """
        Prints the string `s` in green color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(self.GREEN + s + self.END, **kwargs)

    @classmethod
    def yellow(self, s: str, **kwargs) -> None:
        """
        Prints the string `s` in yellow color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(self.YELLOW + s + self.END, **kwargs)

    @classmethod
    def blue(self, s: str, **kwargs) -> None:
        """
        Prints the string `s` in blue color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(self.BLUE + s + self.END, **kwargs)

    @classmethod
    def purple(self, s: str, **kwargs) -> None:
        """
        Prints the string `s` in purple color.

        Args:
            s (str) : The string to be printed.
            **kwargs: Additional keyword arguments to pass to the built-in print function.
        """

        print(self.PURPLE + s + self.END, **kwargs)


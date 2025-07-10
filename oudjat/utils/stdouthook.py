"""A module to handle std output."""

import sys


class StdOutHook:
    """
    A class to handle output redirection and cleaning for standard output.

    Attributes:
        lines (list)  : A list to store the lines written during execution.
        filename (str): The name of the file where the output will be saved.
    """

    def __init__(self, filename: str, silent: bool = False, output: bool = True) -> None:
        """
        Initialize a new instance of StdOutHook.

        Args:
            filename (str)         : the name of the file to write to.
            silent (bool, optional): whether to suppress writing to stdout. Defaults to False.
            output (bool, optional): whether to write to the specified file. Defaults to True.
        """

        self.lines: list[str] = []
        self.filename: str = filename
        self.silent: bool = silent
        self.output: bool = output

    def write(self, text: str, override: bool = False) -> None:
        """
        Write the provided text to stdout if not in silent mode or if `override` is True.

        Args:
            text (str)               : the text to be written.
            override (bool, optional): whether to bypass the silent setting and write to stdout anyway. Defaults to False.

        """

        if not self.silent or override:
            if sys.__stdout__ is not None:
                _ = sys.__stdout__.write(text)

        self.lines.append(text)

    def write_out(self) -> None:
        """
        Write the stored lines to the file, clearing any ANSI color codes before writing.

        If output is not enabled, this method does nothing.
        """

        if not self.output:
            return

        with open(self.filename, "w") as file:
            for line in self.lines:
                # INFO: Cleaning stdout colors
                clean_line = (
                    line.replace("\033[91m", "")
                    .replace("\033[92m", "")
                    .replace("\033[93m", "")
                    .replace("\033[94m", "")
                    .replace("\033[95m", "")
                    .replace("\033[0m", "")
                )
                _ = file.write(clean_line)

    def flush(self):
        """
        Handle Python3 compatibility.

        A placeholder method for compatibility with Python's stdlib; currently does nothing.
        """

        # NOTE: Python3 compatability, does nothing
        pass

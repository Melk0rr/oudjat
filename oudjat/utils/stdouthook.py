# INFO: Helper function to handle std out

import sys


class StdOutHook:
    """
    A class to handle output redirection and cleaning for standard output.

    Attributes:
        lines (list)  : A list to store the lines written during execution.
        filename (str): The name of the file where the output will be saved.
    """

    lines = []
    filename = ""

    def __init__(self, filename, silent, output):
        """
        Initializes a new instance of StdOutHook.

        Args:
            filename (str)         : The name of the file to write to.
            silent (bool, optional): Whether to suppress writing to stdout. Defaults to False.
            output (bool, optional): Whether to write to the specified file. Defaults to True.
        """

        self.filename = filename
        self.silent = silent
        self.output = output

    def write(self, text, override=False, **kwargs):
        """
        Writes the provided text to stdout if not in silent mode or if `override` is True.

        Args:
            text (str)               : The text to be written.
            override (bool, optional): Whether to bypass the silent setting and write to stdout anyway. Defaults to False.
        """

        if not self.silent or override:
            sys.__stdout__.write(text)

        self.lines.append(text)

    def write_out(self) -> None:
        """
        Writes the stored lines to the file, clearing any ANSI color codes before writing.
        If output is not enabled, this method does nothing.
        """

        if not self.output:
            return

        with open(self.filename, "w") as file:
            for line in self.lines:
                # INFO: Cleaning stdout colors
                clean_line = line.replace("\033[91m", "")
                clean_line = clean_line.replace("\033[92m", "")
                clean_line = clean_line.replace("\033[93m", "")
                clean_line = clean_line.replace("\033[94m", "")
                clean_line = clean_line.replace("\033[95m", "")
                clean_line = clean_line.replace("\033[0m", "")

                file.write(clean_line)

    def flush(self):
        """
        A placeholder method for compatibility with Python's stdlib; currently does nothing.
        """

        # NOTE: Python3 compatability, does nothing
        pass

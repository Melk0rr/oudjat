# INFO: Helper function to handle std out

import sys


class StdOutHook:
    lines = []
    filename = ""

    def __init__(self, filename, silent, output):
        self.filename = filename
        self.silent = silent
        self.output = output

    def write(self, text, override=False, **kwargs):
        if not self.silent or override:
            sys.__stdout__.write(text)

        self.lines.append(text)

    def write_out(self) -> None:
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
        # NOTE: Python3 compatability, does nothing
        pass


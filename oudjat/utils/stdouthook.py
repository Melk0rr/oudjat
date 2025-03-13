import sys


class StdOutHook:
    lines = []
    filename = ""

    def __init__(self, filename: str, silent: bool = True, output: bool = False):
        self.filename = filename
        self.silent = silent
        self.output = output

    def write(self, text: str, override: bool = False, **kwargs) -> None:
        if not self.silent or override:
            sys.__stdout__.write(text)
        self.lines.append(text)

    def write_out(self) -> None:
        if self.output:
            with open(self.filename, "w") as file:
                for line in self.lines:
                    # remove stdout colors
                    line = line.replace("\033[91m", "")
                    line = line.replace("\033[92m", "")
                    line = line.replace("\033[93m", "")
                    line = line.replace("\033[94m", "")
                    line = line.replace("\033[95m", "")
                    line = line.replace("\033[0m", "")
                    file.write(line)

    def flush(self):
        # python3 compatibility, does nothing
        pass


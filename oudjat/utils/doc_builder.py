"""
A helper module to handle __doc__ and docopt strings.
"""

from dataclasses import dataclass


@dataclass
class DocOption:
    """
    A dataclass to store doc option details.
    """

    name: str
    description: str
    arg: str = ""
    shortname: str = ""


@dataclass
class DocCommand:
    """
    A dataclass to describe a doc command.
    """

    name: str
    description: str


@dataclass
class DocUsage:
    """
    A dataclass to describe a doc usage and its related options.
    """

    cmd: str = ""
    options: list["DocUsage"] = []


@dataclass
class DocOptUsage:
    """
    A dataclass that describe an option usage.

    It associates to an option name, a requirement and a repeatability.
    """

    opt: str
    required: bool = False
    repeatable: bool = False


class DocBuilder:
    """
    A helper class to build a docopt string.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, program_name: str, description: str) -> None:
        """
        Create a new instance of DocBuilder.

        Args:
            program_name (str): The name of the program for which the doc is written
            description (str) : The main doc description
        """

        self._program: str = program_name
        self._description: str = description

        self._commands: dict[str, "DocCommand"] = {}
        self._options: dict[str, "DocOption"] = {}
        self._usages: dict[str, "DocUsage"] = {}
        self._help: str | None = None

    # ****************************************************************
    # Methods

    def __str__(self) -> str:

        longest_opt = len(max(self._options, key=len))

        opt_desc = """Options:"""
        for opt_k, opt in self._options:
            pad = (longest_opt - len(opt_k)) * " "
            opt_desc += f"    {opt_k}"

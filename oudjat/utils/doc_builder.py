"""
A helper module to handle __doc__ and docopt strings.
"""

from dataclasses import dataclass
from typing import override

from oudjat.utils import Context


@dataclass
class DocOption:
    """
    A dataclass to store doc option details.
    """

    long: str
    description: str
    short: str | None = None
    arg: str | None = None
    default: str | None = None

    @override
    def __str__(self) -> str:
        """
        Convert the current doc option into a string.

        Returns:
            str: A string representation of the current doc option
        """

        short = f"{self.short} " if self.short else ""
        arg = f"={self.arg}" if self.arg else ""

        return f"{short}{self.long}{arg}"

@dataclass
class DocCommand:
    """
    A dataclass to describe a doc command.
    """

    name: str
    description: str

class DocBuilder:
    """
    A helper class to build a docopt string.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, program_name: str, description: str = "") -> None:
        """
        Create a new instance of DocBuilder.

        Args:
            program_name (str): The name of the program for which the doc is written
            description (str) : The main doc description
        """

        self._program: str = program_name.strip().lower()
        self._description: str = description

        self._commands: list["DocCommand"] = []
        self._options: list["DocOption"] = []
        self._usages: list[str] = []
        self._help: list[str] = []

    # ****************************************************************
    # Methods - helpers

    def _longest_key_len(self, keys: list[str]) -> int:
        """
        Return the length of the longest key in a dictionary.

        Args:
            keys (list[str]): The keys to compare

        Returns:
            int: Length of the longest key in the provided dictionary
        """

        return len(max(keys, key=len))

    def _pad_opt(self, k: str, pad_len: int) -> str:
        """
        Return a space padding based on a provided option key and a pad length.

        Args:
            k (str)      : The option key the padding will be appended to
            pad_len (int): The length of the padding

        Returns:
            str: Space padding
        """

        return (pad_len - len(k)) * " "

    def _opt_line(self, option: "DocOption", pad_len: int) -> str:
        """
        Format an option line.

        Args:
            option (DocOption): The option the line will be formatted on
            pad_len (int)     : The length of the padding that will be appended to the option name

        Returns:
            str: Formatted option line
        """

        default = f"[default: {option.default}]" if option.default else ""
        return f"    {option}{self._pad_opt(str(option), pad_len)}    {option.description}{default}"


    # ****************************************************************
    # Methods - content appenders

    def add_opt(self, name: str, description: str, arg: str | None = None, shortname: str | None = None) -> None:
        """
        Add a new option.

        Args:
            name (str)            : The name of the option - basically its fullname like --user
            description (str)     : The description of the option
            arg (str | None)      : The option argument if any
            shortname (str | None): The shortname of the option if any - basically a single letter like -u
        """

        context = Context()

        if name.lower() == name.upper():
            raise ValueError(f"{context}::Invalid option name provided")

        if "-" not in name:
            name = f"--{name}"

        if shortname and (shortname.lower() == shortname.upper()):
            raise ValueError(f"{context}::Invalid option shortname provided")

        if shortname and len(shortname) != 1:
            raise ValueError(f"{context}::Option shortname must be a single character")

        if shortname and "-" not in shortname:
            shortname = f"-{shortname}"

        self._options.append(DocOption(name, description, arg, shortname))

    def add_command(self, name: str, description: str) -> None:
        """
        Add a new command.

        Args:
            name (str)       : The name of the command
            description (str): The description of the command
        """

        name = name.lower()
        self._commands.append(DocCommand(name, description))

    def add_usage(self, usage: str) -> None:
        """
        Add a usage string.

        Args:
            usage (str): The usage string
        """

        self._usages.append(usage)

    # ****************************************************************
    # Methods - doc generation

    def commands_lines(self) -> list[str]:
        """
        Return the doc part related to command descriptions.

        Returns:
            str: Command descriptions
        """

        pad_len = self._longest_key_len([c.name for c in self._commands])
        return [ f"    {cmd.name}{self._pad_opt(cmd.name, pad_len)}    {cmd.description}" for cmd in self._commands]

    def usage_lines(self) -> list[str]:
        """
        Return the doc part related to option descriptions.

        Returns:
            str: Option descriptions
        """

        return [ f"    {self._program} {usg}" for usg in self._usages ]

    def options_lines(self) -> list[str]:
        """
        Return the doc part related to option descriptions.

        Returns:
            str: Option descriptions
        """

        pad_len = self._longest_key_len([ str(o) for o in self._options ])
        return [self._opt_line(opt, pad_len) for opt in self._options]

    @override
    def __str__(self) -> str:

        lines = []

        # Header
        lines.append(f"{self._program.capitalize()}")
        lines.append(f"{self._description}")

        # Commands section
        if len(self._commands) > 0:
            lines.append("\nCommands")
            lines.extend(self.commands_lines())

        # Usage section
        lines.append("\nUsage:")
        lines.extend(self.usage_lines())

        # Option section
        lines.append("\nOptions:")
        lines.extend(self.options_lines())

        # Help section
        if len(self._help) > 0:
            lines.append("\nHelp:")
            lines.extend(self._help)

        return "\n".join(lines).rstrip() + "\n"


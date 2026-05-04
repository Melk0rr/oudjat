"""
A helper module to handle __doc__ and docopt strings.
"""

import re
from dataclasses import dataclass
from typing import Any, override


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


@dataclass
class DocUsage:
    """
    A dataclass to describe a doc command.
    """

    name: str
    usage_str: str
    description: str

    @override
    def __str__(self) -> str:
        """
        Convert the current usage into a simple string.

        Returns:
            str: The usage string representation
        """

        return self.usage_str


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

        self._commands: dict[str, "DocCommand"] = {}
        self._options: dict[str, "DocOption"] = {}
        self._usages: list["DocUsage"] = []
        self._help: list[str] = []

    # ****************************************************************
    # Methods - getters / setters

    @property
    def commands(self) -> dict[str, "DocCommand"]:
        """
        Return the commands of the current builder.

        Returns:
            dict[str, DocCommand]: The dictionary of commands referenced by the builder
        """

        return self._commands

    @commands.setter
    def commands(self, new_commands: dict[str, "DocCommand"]) -> None:
        """
        Specify commands to be referenced by this doc builder.

        Args:
            new_commands (dict[str, DocCommand]): A dictionary of commands to set
        """

        self._commands = new_commands

    @property
    def options(self) -> dict[str, "DocOption"]:
        """
        Return the options of the current builder.

        Returns:
            dict[str, DocOption]: The dictionary of options referenced by the builder
        """

        return self._options

    @options.setter
    def options(self, new_options: dict[str, "DocOption"]) -> None:
        """
        Specify options to be referenced by this doc builder.

        Args:
            new_options (dict[str, DocOption]): A dictionary of options to set
        """

        self._options = new_options

    @property
    def usages(self) -> list["DocUsage"]:
        """
        Return the usage lines of the current builder.

        Returns:
            list[str]: The list of usage strings referenced by the builder
        """

        return self._usages

    @usages.setter
    def usages(self, new_usages: list["DocUsage"]) -> None:
        """
        Specify usage lines to be referenced by this doc builder.

        Args:
            new_usages (list[str]): A new list of usage strings to set
        """

        self._usages = new_usages

    @property
    def help_content(self) -> list[str]:
        """
        Return the help strings of the current builder.

        Returns:
            list[str]: The list of help strings referenced by the builder at the foot of the doc
        """

        return self._help

    @help_content.setter
    def help_content(self, new_help: list[str]) -> None:
        """
        Specify help lines to be referenced by this doc builder.

        Args:
            new_help (list[str]): A new list of help strings to set
        """

        self._help = new_help

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
        return (
            f"    {option}{self._pad_opt(str(option), pad_len)}    {option.description} {default}"
        )

    # ****************************************************************
    # Methods - content appenders

    def add_option(
        self,
        long: str,
        description: str,
        arg: str | None = None,
        short: str | None = None,
        default: Any | None = None,
    ) -> None:
        """
        Add a new option.

        Args:
            long (str)       : The name of the option - basically its fullname like --user
            description (str): The description of the option
            arg (str | None) : The option argument if any
            short(str | None): The shortname of the option if any - basically a single letter like -u
            default (Any)    : The default value of the option
        """

        if long.lower() == long.upper():
            raise ValueError("Invalid option name provided")

        if not long.startswith("--"):
            long = f"--{long}"

        if short and (short.lower() == short.upper()):
            raise ValueError("Invalid option shortname provided")

        if short is not None and (len(short) > 2 or len(short.replace("-", "")) != 1):
            raise ValueError("Option shortname must be a single character")

        if short and not short.startswith("-"):
            short = f"-{short}"

        if arg is not None:
            arg = arg.upper()

        self._options[long] = DocOption(long, description, short, arg=arg, default=default)

    def add_command(self, name: str, description: str) -> None:
        """
        Add a new command.

        Args:
            name (str)       : The name of the command
            description (str): The description of the command
        """

        name = name.lower()
        self._commands[name] = DocCommand(name, description)

    def add_usage(self, name: str, usage: str, description: str) -> None:
        """
        Add a usage string.

        Args:
            name (str)       : A short name that match the usage
            usage (str)      : The usage string
            description (str): A description of the usage
        """

        self._usages.append(DocUsage(name, usage, description))

    # ****************************************************************
    # Methods - merger

    def merge(self, other: "DocBuilder") -> None:
        """
        Merge another doc builder into the current one.

        Program and description are kept from the current builder.

        Args:
            other (DocBuilder): The other DocBuilder instance to merge into the current one
        """

        for cmd in other.commands.values():
            self.add_command(cmd.name, cmd.description)

        for opt in other.options.values():
            self.add_option(opt.long, opt.description, opt.arg, opt.short, opt.default)

        for usg in other.usages:
            self.add_usage(usg.name, usg.usage_str, usg.description)

        self._help.extend(other.help_content)

    # ****************************************************************
    # Methods - doc generation

    def commands_lines(self) -> list[str]:
        """
        Return the doc part related to command descriptions.

        Returns:
            str: Command descriptions
        """

        pad_len = self._longest_key_len(list(self._commands.keys()))
        return [
            f"    {cmd.name}{self._pad_opt(cmd.name, pad_len)}    {cmd.description}"
            for cmd in self._commands.values()
        ]

    def usage_lines(self) -> list[str]:
        """
        Return the doc part related to option descriptions.

        Returns:
            str: Option descriptions
        """

        lines = []
        for usg in self._usages:
            full_usg = f"{self._program} {usg}"
            if len(usg.usage_str) > 110:
                usg_split = re.findall(r"\(+[^\)]*\)+|\[+[^\]]*\]+|[^\s]+", full_usg)
                baseline = f"    {' '.join(usg_split[:3])}"
                pad = len(baseline) - len(usg_split[2])

                lines.append(baseline)
                for usg_piece in usg_split[3:]:
                    lines.append(f"{' ' * pad}{usg_piece}")

            else:
                lines.append(f"    {full_usg}")

        return lines

    def usage_description_lines(self) -> list[str]:
        """
        Return the usage descriptions lines.

        Returns:
            list[str]: Lines that describe usages
        """

        pad_len = self._longest_key_len([usg.name for usg in self._usages])
        return [
            f"    {usg.name.replace('--', '')}{self._pad_opt(usg.name, pad_len)}    {usg.description}"
            for usg in self._usages
        ]

    def options_lines(self) -> list[str]:
        """
        Return the doc part related to option descriptions.

        Returns:
            str: Option descriptions
        """

        pad_len = self._longest_key_len([str(o) for o in self._options.values()])
        return [self._opt_line(opt, pad_len) for opt in self._options.values()]

    @override
    def __str__(self) -> str:
        lines = []

        # Header
        lines.append(f"{self._program.capitalize()}")
        if len(self._description) > 0:
            lines.append(f"{self._description}")

        # Commands section
        if len(self._commands) > 0:
            lines.append("\nCommands:")
            lines.extend(self.commands_lines())

        # Usage section
        lines.append("\nUsage:")
        lines.extend(self.usage_lines())

        # Usage descriptions
        lines.append("\nUsage-description:")
        lines.extend(self.usage_description_lines())

        # Option section
        lines.append("\nOptions:")
        lines.extend(self.options_lines())

        # Help section
        if len(self._help) > 0:
            lines.append("\nHelp:")
            lines.extend(self._help)

        return "\n".join(lines).rstrip() + "\n"

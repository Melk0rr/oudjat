"""A module that defines common command behaviors."""

from dataclasses import dataclass, field
from typing import Any, Callable, TypeAlias

import orjson

from oudjat.utils import Context
from oudjat.utils.file import FileUtils
from oudjat.utils.string import StringUtils
from oudjat.utils.types import DataType


@dataclass
class CmdUsageOpt:
    """
    A dataclass which holds the name of the option which is mapped to a backend parameter.

    The class also holds an optional transform function which is applied to the option value before passing it as backend argument.

    Attributes:
        option (str)                           : The name of the option which will be mapped to backend parameter
        transform (Callable[[Any], Any] | None): The transform function that may be applied to the option value
    """

    option: str
    transform: Callable[[Any], Any] | None = None


@dataclass
class CmdUsage:
    """
    A dataclass to handle command usages.

    Attributes:
        option (CmdOpt)                   : The option the usage is focused on
        usage_str (str)                   : The usage string that will be passed to docopt
        mapping_opts (CmdOptUsageRegistry): The registry that maps backend parameters with command options
        backend (Callable[..., DataType]) : The backend function / method which is called by this usage

    """

    option: "CmdOpt"
    usage_str: str
    mapping_opts: "CmdOptUsageRegistry" = field(default_factory=lambda: {})
    backend: Callable[..., "DataType"] | None = None


@dataclass
class CmdOpt:
    """
    A dataclass that holds a command option details that will be passed to docopt string.

    Attributes:
        description (str)   : A description passed
        short (str | None)  : An optional short version of the option name
        arg (str | None)    : An optional argument name
        default (Any | None): A default value for the option
        transform           : An optional transform function that will be given the option name and the option value
    """

    description: str
    short: str | None = None
    arg: str | None = None
    default: Any | None = None
    transform: "CmdMappingCallback | None" = None


@dataclass
class CmdProps:
    """
    A dataclass that stores connector command options and usages.

    Attributes:
        name (str)               : The name of the command
        description (str)        : A description of the command
        base (CmdUsageRegistry)  : A registry of usages that will be appended to all usages strings
        options (CmdOptRegistry) : A registry of available options
        usages (CmdUsageRegistry): A registry of available command usages
    """

    name: str
    description: str
    options: "CmdOptRegistry" = field(default_factory=lambda: {})
    usages: "CmdUsageRegistry" = field(default_factory=lambda: {})

    def backends(self, registry: dict[str, Callable[..., "DataType"] | None]) -> None:
        """
        Set usages backend functions based on the provided registry.

        The registry must contain couples of usage key / transform function.

        Args:
            registry (dict[str, Callable[..., DataType]]): A registry which contains usage keys and their transform function
        """

        for usage, backend in registry.items():
            if usage in self.usages:
                self.usages[usage].backend = backend

    def opts_transform(self, registry: dict[str, "CmdMappingCallback | None"]) -> None:
        """
        Set options transform functions based on the provided registry.

        The registry must contain couples of option key / transform function.

        Args:
            registry (dict[str, CmdMappingCallback | None]): A registry which contains option keys and their transform function
        """

        for opt, tr in registry.items():
            if opt in self.options:
                self.options[opt].transform = tr

    def append_usages(
        self, append_str: str, inc: set[str] | None = None, exc: set[str] | None = None
    ) -> None:
        """
        Append the provided usage string to usages `usage_str` attribute.

        If no include nor exlude key sets are provided, the string will be appended to all usages.
        If you provide an include set, the string will be appended only to usages which key is included.
        If you provide an exclude set, its keys will be substracted to those in the initial scope (all or included usages).

        Args:
            append_str (str)     : New usage string to append to all others
            inc (set[str] | None): Include key set
            exc (set[str] | None): Exclude key set
        """

        target_keys = (
            {k for k in self.usages if k in inc} if inc is not None else set(self.usages.keys())
        )

        if exc:
            target_keys -= exc

        for k in target_keys:
            usg = self.usages[k]
            usg.usage_str = f"{usg.usage_str} {append_str}"

    def prepend_usages(
        self, prepend_str: str, inc: set[str] | None = None, exc: set[str] | None = None
    ) -> None:
        """
        Prepend the provided usage string to usages `usage_str` attribute.

        If no include nor exlude key sets are provided, the string will be prepended to all usages.
        If you provide an include set, the string will be prepended only to usages which key is included.
        If you provide an exclude set, its keys will be substracted to those in the initial scope (all or included usages).

        Args:
            prepend_str (str)     : New usage string to append to all others
            inc (set[str] | None): Include key set
            exc (set[str] | None): Exclude key set
        """

        target_keys = (
            {k for k in self.usages if k in inc} if inc is not None else set(self.usages.keys())
        )

        if exc:
            target_keys -= exc

        for k in target_keys:
            usg = self.usages[k]
            usg.usage_str = f"{prepend_str} {usg.usage_str}"


CmdMappingCallback: TypeAlias = Callable[[str, Any], Any]
CmdOptRegistry: TypeAlias = dict[str, "CmdOpt"]
CmdOptUsageRegistry: TypeAlias = dict[str, "CmdUsageOpt"]
CmdUsageRegistry: TypeAlias = dict[str, "CmdUsage"]


class Base:
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
    # Methods - getters/setters

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

    # ****************************************************************
    # Methods - helpers

    def _parse_payload(self, payload_str: str) -> dict[str, Any]:
        """
        Parse a payload string into a dictionary.

        Args:
            payload_str (str): The payload string to parse

        Returns:
            dict[str, Any]: The dictionary resulting of the parsing
        """

        return orjson.loads(StringUtils.jsonify(payload_str))

    def _is_opt_present(self, opt: str) -> bool:
        """
        Check if the option is present.

        Args:
            opt (str): Option to check the presence of

        Returns:
            bool: True if the option is present. False otherwise
        """

        return bool(self.options.get(opt) or False)

    def _unify_str_opt(self, str_opt: str) -> list[str]:
        """
        Unify option case where a list of information can be passed either as a string, a list of strings or a txt file.

        Args:
            str_opt (str) : The key in the `self.options` dictionary where the resulting list should be stored.
            file_opt (str): The key in the `self.options` dictionary that, if exists, points to a file path.

        Returns:
            list[str]: A cleaned list of strings
        """

        values = []

        if self.options[str_opt].startswith("@"):
            path = self.options[str_opt][1:]

            if not FileUtils.check_path(path):
                raise FileNotFoundError(f"{Context()}::Could not find {path}")

            values = [v.strip() for v in FileUtils.import_txt(path)]

        else:
            values = [v.strip() for v in self.options[str_opt].split(",")]

        return list(filter(None, values))

    def run(self) -> None:
        """
        Run method to be implemented by subclasses.

        Raises:
            NotImplementedError: Indicates that the `run` method must be overridden in any subclass.
        """

        raise NotImplementedError(
            f"{Context()}::Method must be implemented by the overloading class"
        )

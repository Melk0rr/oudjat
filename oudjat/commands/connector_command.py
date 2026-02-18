"""
A command module to address some shared behaviors accross connector commands.
"""

from ctypes import ArgumentError
from dataclasses import dataclass, field
from typing import Any, Callable, TypeAlias, override

from oudjat.connectors.exceptions import ConnectorCredentialError
from oudjat.core.mapper import Mapper
from oudjat.utils.context import Context
from oudjat.utils.file_utils import FileUtils
from oudjat.utils.types import DataType

from .base import Base
from .exceptions import ConnectorCommandInvalidBackend

CmdMappingCallback: TypeAlias = Callable[[str, Any], Any]

@dataclass
class CmdUsageOpt:
    """
    A helper class to handle command usage options.
    """

    opt: str
    transform: Callable[[Any], Any] | None = None
    required: bool = False
    repeatable: bool = False

@dataclass
class CmdOpt:
    """
    A dataclass to handle main command options.
    """

    description: str
    mapping_opts: "CommandMappingOpts"
    backend: Callable[..., "DataType"] | None = None
    callback: Callable[..., "DataType"] | None = None

@dataclass
class OptMappingValue:
    """
    A dataclass to handle option mapping value.
    """

    description: str
    shortname: str = ""
    arg: str = ""
    transform: "CmdMappingCallback | None" = None

@dataclass
class ConnectorOptions:
    """
    A dataclass that stores connector command options.
    """

    base: "CommandMappingOpts" = field(default_factory=lambda : {})
    shared: "CmdMappingRegistry" = field(default_factory=lambda : {})
    main: "CommandOpts" = field(default_factory=lambda : {})

CmdMappingRegistry: TypeAlias = dict[str, "OptMappingValue"]
CommandMappingOpts: TypeAlias = dict[str, "CmdUsageOpt"]
CommandOpts: TypeAlias = dict[str, "CmdOpt"]


class ConnectorCommand(Base):
    """
    A class that handles shared properties and behaviors across connector commands.
    """

    # ****************************************************************
    # Constructor & Attributes

    _opt: "ConnectorOptions" = ConnectorOptions()

    def __init__(self, options: dict[str, Any], need_credentials: bool = False) -> None:
        """
        Create a new ConnectorCommand.

        Args:
            options (dict[str, Any]): Command options
            need_credentials (bool) : Whether the connector needs credentials
        """

        super().__init__(options)
        context = Context()

        if need_credentials and not (
            ("--username" in self.options and "--password" in self.options)
            or "--creds-service" in self.options
        ):
            raise ConnectorCredentialError(
                f"{context}::No credentials were provided for the connector"
            )

    # ****************************************************************
    # Methods

    def _resolve_arg_value(self, val: str) -> Any:
        """
        Resolve the option value based on option name and optional transform function.

        Args:
            val (CommandMappingValue): A tuple containing at least the option name and a transform function

        Returns:
            Any: Either the raw option value or a transformed value based on the provided function
        """

        raw = self.options.get(val, None)
        shared_opt = self._opt.shared[val]

        return shared_opt.transform(val, raw) if callable(shared_opt.transform) else raw

    def _build_cmd_kwargs(self, args: "CommandMappingOpts") -> dict[str, Any]:
        """
        Build command arguments based on its mapping registry.

        Args:
            args (str): The name of the command being used

        Returns:
            dict[str, Any]: The command kwargs
        """

        res = {}
        for k,v in args.items():
            if self._is_opt_present(v.opt):
                value = self._resolve_arg_value(v.opt)

                if callable(v.transform):
                    value = v.transform(value)

                res[k] = value

        return res

    def _find_cmd_name(self) -> str:
        """
        Return the command name that is specified in command options.

        Returns:
            str: The command name provided in the options
        """

        def cmd_in_options(cmd: str) -> bool:
            return cmd in self.options

        return next(filter(cmd_in_options, self._opt.main.keys()))

    @override
    def run(self) -> None:
        """
        Run the command main process.
        """

        context = Context()

        # Prepare the command
        cmd_name = self._find_cmd_name()
        cmd_opt = self._opt.main[cmd_name]
        args = self._build_cmd_kwargs(cmd_opt.mapping_opts)

        if cmd_opt.backend is None:
            raise ConnectorCommandInvalidBackend(f"{context}::No backend function defined for {cmd_name} command.")

        req_params = Mapper.required_params(Mapper.signature_params(cmd_opt.backend))

        # Check if no required parameters were ommited
        if not bool(set(args.keys()) & req_params) and len(req_params) > 0:
            raise ArgumentError(f"{context}::{cmd_name} command requires {list(req_params)}")

        # Run the command
        data = cmd_opt.backend(**args)

        # Post operations
        if self.options["--csv"]:
            FileUtils.export_csv(data, self.options["--csv"], delimiter="|")

        if self.options["--json"]:
            FileUtils.export_json(data, self.options["--json"])


    @staticmethod
    def _gen_doc(connector_opts: "ConnectorOptions") -> str:
        """
        Gen the connector command doc from the connector options.

        Args:
            connector_opts (ConnectorOptions): Connector options

        Returns:
            str: __doc__ string to pass to docopt
        """

        all_opts = connector_opts.main | connector_opts.shared
        longest_opt = len(max(all_opts, key=len))

        opt_desc = """Options:"""


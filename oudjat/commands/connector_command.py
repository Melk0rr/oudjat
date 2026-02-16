"""
A command module to address some shared behaviors accross connector commands.
"""

from ctypes import ArgumentError
from typing import Any, Callable, TypeAlias, override

from oudjat.connectors.exceptions import ConnectorCredentialError
from oudjat.core.mapper import Mapper
from oudjat.utils.context import Context
from oudjat.utils.file_utils import FileUtils
from oudjat.utils.types import DataType

from .base import Base

CommandMappingCallback: TypeAlias = Callable[[str, Any], Any]
CommandMappingValue: TypeAlias = "CommandMappingCallback | None"
CommandMappingRegistry: TypeAlias = dict[str, "CommandMappingValue"]
CommandMappingOpts: TypeAlias = dict[str, str | tuple[str, Callable[[Any], Any]]]
CommandOpts: TypeAlias = dict[str, tuple[Callable[..., "DataType"], "CommandMappingOpts"]]


class ConnectorCommand(Base):
    """
    A class that handles shared properties and behaviors across connector commands.
    """

    # ****************************************************************
    # Constructor

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

        # A mapping of all the available options for this connector, and their mapped value
        self._opt_map: "CommandMappingRegistry" = {}

        # A mapping of all the main commands for this connector and their options
        self._command_opt: "CommandOpts" = {}

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
        trans = self._opt_map[val]

        return trans(val, raw) if callable(trans) else raw

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

            opt_k = v[0] if isinstance(v, tuple) else v
            opt_v = self._resolve_arg_value(opt_k)

            if isinstance(v, tuple):
                _, trs = v
                opt_v = trs(opt_v)

            res[k] = opt_v

        return res

    def _find_cmd_name(self) -> str:
        """
        Return the command name that is specified in command options.

        Returns:
            str: The command name provided in the options
        """

        def cmd_in_options(cmd: str) -> bool:
            return cmd in self.options

        return next(filter(cmd_in_options, self._command_opt.keys()))

    @override
    def run(self) -> None:
        """
        Run the command main process.
        """

        # Prepare the command
        cmd_name = self._find_cmd_name()
        cmd, params = self._command_opt[cmd_name]
        args = self._build_cmd_kwargs(params)

        req_params = Mapper.required_params(Mapper.signature_params(cmd))

        # Check if no required parameters were ommited
        if not bool(set(args.keys()) & req_params) and len(req_params) > 0:
            raise ArgumentError(f"{Context()}::{cmd_name} command requires {list(req_params)}")

        # Run the command
        data = cmd(**args)

        # Post operations
        if self.options["--csv"]:
            FileUtils.export_csv(data, self.options["--csv"], delimiter="|")

        if self.options["--json"]:
            FileUtils.export_json(data, self.options["--json"])

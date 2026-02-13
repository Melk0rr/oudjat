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

CommandMappingValue: TypeAlias = tuple[str, Callable[[str, Any], Any] | None]
CommandMappingRegistry: TypeAlias = dict[str, "CommandMappingValue"]
CommandOpts: TypeAlias = dict[str, tuple[Callable[..., "DataType"], "CommandMappingRegistry"]]

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

        self.data: "DataType" = []
        self._command_opt: "CommandOpts" = {}

    # ****************************************************************
    # Methods

    def _resolve_arg_value(self, val: "CommandMappingValue") -> Any:
        """
        Resolve the option value based on option name and optional transform function.

        Args:
            val (CommandMappingValue): A tuple containing at least the option name and a transform function

        Returns:
            Any: Either the raw option value or a transformed value based on the provided function
        """

        opt, trans = val
        raw = self.options.get(opt, None)

        return trans(opt, raw) if trans else raw

    def _build_cmd_kwargs(self, args: "CommandMappingRegistry") -> dict[str, Any]:
        """
        Build command arguments based on its mapping registry.

        Args:
            args (str): The name of the command being used

        Returns:
            dict[str, Any]: The command kwargs
        """

        return {k: self._resolve_arg_value(v) for k,v in args.items() if self._is_opt_present(v[0])}

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


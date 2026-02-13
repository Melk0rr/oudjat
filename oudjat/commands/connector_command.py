"""
A command module to address some shared behaviors accross connector commands.
"""

from typing import Any, Callable, TypeAlias

from oudjat.connectors.exceptions import ConnectorCredentialError
from oudjat.utils.context import Context
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

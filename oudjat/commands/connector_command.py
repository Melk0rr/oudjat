"""
A command module to address some shared behaviors accross connector commands.
"""

from typing import Any, Callable, TypeAlias

from oudjat.connectors.exceptions import ConnectorCredentialError
from oudjat.core.mapper import MappingRegistry
from oudjat.utils.context import Context
from oudjat.utils.types import DataType

from .base import Base

CommandOpts: TypeAlias = dict[str, tuple[Callable[..., "DataType"], "MappingRegistry"]]

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

    def _build_cmd_kwargs(self, cmd_name: str) -> dict[str, Any]:
        """
        Build command arguments based on its mapping registry.

        Args:
            cmd_name (str): The name of the command being used

        Returns:
            dict[str, Any]: The command kwargs
        """

        _, args_map = self._command_opt[cmd_name]
        return {k: self.options[v] for k, v in args_map if v in self.options}

    def _find_cmd_name(self) -> str:
        """
        Return the command name that is specified in command options.

        Returns:
            str: The command name provided in the options
        """

        def cmd_in_options(cmd: str) -> bool:
            return cmd in self.options

        return next(filter(cmd_in_options, self._command_opt.keys()))

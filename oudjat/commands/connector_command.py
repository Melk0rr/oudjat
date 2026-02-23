"""
A command module to address some shared behaviors accross connector commands.
"""

from ctypes import ArgumentError
from typing import Any, override

from oudjat.connectors.exceptions import ConnectorCredentialError
from oudjat.core.mapper import Mapper
from oudjat.utils.context import Context
from oudjat.utils.doc_builder import DocBuilder
from oudjat.utils.file_utils import FileUtils

from .base import Base, CmdOptUsageRegistry, CmdProps
from .exceptions import ConnectorCommandInvalidBackend


class ConnectorCommand(Base):
    """
    A class that handles shared properties and behaviors across connector commands.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps("connectors", "Oudjat connectors parent command")
    __doc_builder__: "DocBuilder" = DocBuilder("oudjat", "")

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
        shared_opt = self.__cmd_props__.options[val]

        return shared_opt.transform(val, raw) if callable(shared_opt.transform) else raw

    def _build_cmd_kwargs(self, args: "CmdOptUsageRegistry") -> dict[str, Any]:
        """
        Build command arguments based on its mapping registry.

        Args:
            args (str): The name of the command being used

        Returns:
            dict[str, Any]: The command kwargs
        """

        res = {}
        for k, v in args.items():
            if self._is_opt_present(v.option):
                value = self._resolve_arg_value(v.option)

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
            return self._is_opt_present(cmd)

        return next(filter(cmd_in_options, self.__cmd_props__.usages.keys()))

    @override
    def run(self) -> None:
        """
        Run the command main process.
        """

        context = Context()

        # Prepare the command
        cmd_name = self._find_cmd_name()
        cmd_opt = self.__cmd_props__.usages[cmd_name]
        args = self._build_cmd_kwargs(cmd_opt.mapping_opts)

        if cmd_opt.backend is None:
            raise ConnectorCommandInvalidBackend(
                f"{context}::No backend function defined for {cmd_name} command."
            )

        req_params = Mapper.required_params(Mapper.signature_params(cmd_opt.backend))

        # Check if no required parameters were ommited
        if not bool(set(args.keys()) & req_params) and len(req_params) > 0:
            raise ArgumentError(f"{context}::{cmd_name} command requires {list(req_params)}")

        # Run the command
        data = cmd_opt.backend(**args)

        # Post operations
        if self.options["--csv"]:
            if not isinstance(self.options["--csv"], list):
                self.options["--csv"] = [self.options["--csv"]]

            for p in self.options["--csv"]:
                FileUtils.export_csv(data, p, delimiter="|")

        if self.options["--json"]:
            FileUtils.export_json(data, self.options["--json"])

        if self.options["--print"]:
            print(data)

    @staticmethod
    def _gen_doc(program: str, cmd_hub: "CmdProps", description: str = "") -> "DocBuilder":
        """
        Gen the connector command doc from the connector options.

        Args:
            program (str)    : The name of the program running
            cmd_hub (CmdHub) : Connector options hub
            description (str): The program's description

        Returns:
            DocBuilder: a doc builder instance that can be converted to a string
        """

        builder = DocBuilder(program, description)

        builder.add_command(cmd_hub.name, cmd_hub.description)

        for opt_k, opt in cmd_hub.options.items():
            builder.add_option(opt_k, opt.description, opt.arg, opt.short)

        for usg_k, usg in cmd_hub.usages.items():
            builder.add_option(usg_k, usg.option.description, usg.option.arg, usg.option.short)
            builder.add_usage(f"{cmd_hub.name} {usg.usage_str}")

        return builder

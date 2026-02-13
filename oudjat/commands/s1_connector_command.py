"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from ctypes import ArgumentError
from typing import Any, override

from oudjat.connectors.edr.sentinelone import S1Connector
from oudjat.core.mapper import Mapper
from oudjat.utils import Context
from oudjat.utils.file_utils import FileUtils

from .connector_command import CommandOpts, ConnectorCommand


class S1ConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the S1Connector.
    """

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new S1ConnectorCommand.

        Args:
            options (dict[str, Any]): Provided options
        """

        super().__init__(options, True)

        credentials = {}
        if "--password" in self.options:
            credentials = {
                "username": self.options["--username"],
                "password": self.options["--password"],
            }

        self.connector: "S1Connector" = S1Connector(target=self.options["--target"], **credentials)

        if "--creds-service" in self.options:
            self.connector.set_creds_from_svc_name(self.options["--creds-service"])

        self.connector.connect()

        self._command_opt: "CommandOpts" = {
            "--agents": (
                self.connector.agents,
                {
                    "site_ids": (
                        "--site-list",
                        lambda opt, _: self._unify_str_opt(opt, "--site-file"),
                    ),
                    "payload": ("--payload", None),
                    "infected": ("--infected", lambda opt, _: self._is_opt_present(opt)),
                    "net_statuses": ("--net-status", None),
                },
            ),
            "--move-agent-site": (
                self.connector.move_agent_to_site,
                {
                    "site_id": ("--site-list", lambda _, v: v.split(",")),
                    "agent_name": ("--agent-list", None),
                },
            ),
        }

    @override
    def run(self) -> None:
        """
        Run the command main process.
        """

        cmd_name = self._find_cmd_name()
        cmd, params = self._command_opt[cmd_name]
        args = self._build_cmd_kwargs(params)

        req_params = Mapper.required_params(Mapper.signature_params(cmd))

        if not bool(set(args) & req_params):
            raise ArgumentError(f"{Context()}::{cmd_name} command requires {req_params}")

        data = cmd(**args)

        if "--csv" in self.options:
            FileUtils.export_csv(data, self.options["--csv"], delimiter="|")

        elif "--json" in self.options:
            FileUtils.export_json(data, self.options["--json"])

"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

from oudjat.connectors.edr.sentinelone import S1Connector

from .connector_command import CommandMappingRegistry, CommandOpts, ConnectorCommand


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

        con_args = {"target": self.options["--target"]}
        if self.options["--username"] and self.options["--password"]:
            con_args.update(
                {
                    "username": self.options["--username"],
                    "password": self.options["--password"],
                }
            )

        self.connector: "S1Connector" = S1Connector(**con_args)

        if "--creds-service" in self.options:
            self.connector.set_creds_from_svc_name(self.options["--creds-service"])

        self.connector.connect()

        self._opt_map: "CommandMappingRegistry" = {
            "--agent-list": lambda opt, _: self._unify_str_opt(opt, "--agent-file"),
            "--group-list": lambda opt, _: self._unify_str_opt(opt, "--group-file"),
            "--infected": lambda opt, _: self._is_opt_present(opt),
            "--payload": None,
            "--site-list": lambda opt, _: self._unify_str_opt(opt, "--site-file"),
            "--status-filters": lambda opt, v: v.split(","),
            "--verdict-filters": lambda opt, v: v.split(","),
        }

        self._command_opt: "CommandOpts" = {
            # Export S1 agents details
            "--agents": (
                self.connector.agents,
                {
                    "site_ids": "--site-list",
                    "limit": "--limit",
                    "payload": "--payload",
                    "infected": "--infected",
                },
            ),

            # Export flat agent data
            "--agents-export": (
                self.connector.agents_export,
                {
                    "site_ids": "--site-list",
                    "payload": "--payload",
                    "infected": "--infected",
                }
            ),

            # Move one or multiple agents to a site based on its id
            "--move-agent-site": (
                self.connector.move_agent_to_site,
                {
                    "site_id": ("--site-list", lambda lst: next(iter(lst))),
                    "agent_name": "--agent-list",
                },
            ),

            # Retrieve CVEs detected by S1
            "--cves": (
                self.connector.cves,
                {
                    "site_ids": "--site-list",
                    "payload": "--payload",
                },
            ),

            # Retrieve threats detected by S1
            "--threats": (
                self.connector.cves,
                {
                    "site_ids": "--site-list",
                    "payload": "--payload",
                },
            ),
        }

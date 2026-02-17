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
            "--auto": lambda opt, _: self._is_opt_present(opt),
            "--filter": None,
            "--ids": lambda opt, _: self._unify_str_opt(opt, "--ids-file"),
            "--infected": lambda opt, _: self._is_opt_present(opt),
            "--malicious-policy": None,
            "--names": lambda opt, _: self._unify_str_opt(opt, "--names-file"),
            "--path": None,
            "--payload": None,
            "--sites": lambda opt, _: self._unify_str_opt(opt, "--ids-file"),
            "--status": None,
            "--status-filters": lambda opt, v: v.split(","),
            "--suspicious-policy": None,
            "--vendor": lambda opt, _: self._unify_str_opt(opt, "--vendor-file"),
            "--verdict": None,
            "--verdict-filters": lambda opt, v: v.split(","),
        }

        self._command_opt: "CommandOpts" = {
            # Export S1 agents details
            "--agents": (
                self.connector.agents,
                {
                    "site_ids": "--sites",
                    "payload": "--payload",
                    "infected": "--infected",
                },
            ),
            # Export flat agent data
            "--agents-export": (
                self.connector.agents_export,
                {
                    "site_ids": "--sites",
                    "payload": "--payload",
                    "infected": "--infected",
                },
            ),
            # Move one or multiple agents to a site based on its id
            "--move-agent-site": (
                self.connector.move_agent_to_site,
                {
                    "site_id": ("--sites", lambda lst: next(iter(lst))),
                    "agent_name": "--names",
                },
            ),
            # Retrieve CVEs detected by S1
            "--cves": (
                self.connector.cves,
                {
                    "site_ids": "--sites",
                    "payload": "--payload",
                },
            ),
            # Retrieve threats detected by S1
            "--threats": (
                self.connector.threats,
                {
                    "site_ids": "--sites",
                    "payload": "--payload",
                },
            ),
            # Change the verdict of filtered threats
            "--threats-verdict": (
                self.connector.threat_verdict,
                {
                    "verdict": "--verdict",
                    "threat_ids": "--ids",
                    "site_ids": "--sites",
                    "status_filter": "--status-filter",
                    "verdict_filter": "--verdict-filter",
                    "file_path": "--path",
                    "threat_filter": "--filter",
                },
            ),
            # Change the verdict and status of filtered threats
            "--threats-incident": (
                self.connector.threat_incident,
                {
                    "status": "--status",
                    "verdict": "--verdict",
                    "threat_ids": "--ids",
                    "site_ids": "--sites",
                    "status_filter": "--status-filter",
                    "verdict_filter": "--verdict-filter",
                    "file_path": "--path",
                    "auto": "--auto",
                    "threat_filter": "--filter",
                },
            ),
            # Retrieve an inventory of applications detected by S1
            "--applications": (
                self.connector.applications,
                {
                    "vendors": "--vendor",
                    "site_ids": "--sites",
                    "payload": "--payload",
                },
            ),
            # Retrieve an inventory of applications detected by S1 that present a security risk
            "--applications-with-risks": (
                self.connector.applications_with_risks,
                {
                    "vendors": "--vendor",
                    "site_ids": "--sites",
                    "payload": "--payload",
                },
            ),

            # Retrieve CVEs for specific application(s)
            "--applications-cves": (
                self.connector.application_cves,
                {
                    "appliation_ids": "--ids",
                    "appliation_name": "--names",
                    "application_vendor": "--vendor",
                    "site_ids": "--sites",
                    "payload": "--payload",
                },
            ),

            # Retrieve groups
            "--groups": (
                self.connector.groups,
                {
                    "site_ids": "--sites",
                    "payload": "--payload",
                },
            ),

            # Update the policy of the specified groups
            "--group-policy": (
                self.connector.group_policy_update,
                {
                    "group_id": "--ids",
                    "malicious_mitigation": "--malicious-policy",
                    "suspicious_mitigation": "--suspicious-policy",
                    "payload": "--payload",
                },
            ),

            # Move agents into specified group
            "--group-move-agent": (
                self.connector.group_move_agent,
                {
                    "group_id": ("--ids", lambda lst: next(iter(lst))),
                    "agent_name": "--names",
                    "payload": "--payload",
                },
            ),

            # Retrieve sites
            "--sites": (
                self.connector.sites,
                {
                    "payload": "--payload",
                },
            ),

            # Retrieve sites by names
            "--sites-by-name": (
                self.connector.sites_by_name,
                {
                    "site_name": "--sites",
                    "payload": "--payload",
                },
            ),
        }

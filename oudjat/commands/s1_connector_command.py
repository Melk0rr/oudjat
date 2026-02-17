"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

import orjson

from oudjat.connectors.edr.sentinelone import S1Connector

from .connector_command import CommandMappingRegistry, CommandOpts, ConnectorCommand


class S1ConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the S1Connector.
    """

    __doc__ = """
Usage:
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --agents
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --agents-export
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --move-agent-site
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--names=NAMES | --names-file=NAMESFILE]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --threats
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --threats-verdict
                                                                    [--verdict=VERDICT]
                                                                    [--ids=IDS | --ids-file=IDSFILE]
                                                                    [--sites-list=SITELIST | --site-file=SITEFILE]
                                                                    [--status-filter=STATUSFILTER]
                                                                    [--verdict-filter=VERDICTFILTER]
                                                                    [--path=PATH]
                                                                    [--filter=FILTER]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --threats-incident
                                                                    [--status=STATUS]
                                                                    [--verdict=VERDICT]
                                                                    [--ids=IDS | --ids-file=IDSFILE]
                                                                    [--sites-list=SITELIST | --site-file=SITEFILE]
                                                                    [--status-filter=STATUSFILTER]
                                                                    [--verdict-filter=VERDICTFILTER]
                                                                    [--path=PATH]
                                                                    [--auto]
                                                                    [--filter=FILTER]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --applications
                                                                    [--vendor=VENDOR | --vendor-file=VENDORFILE]
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --applications-with-risks
                                                                    [--vendor=VENDOR | --vendor-file=VENDORFILE]
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --applications-cves
                                                                    [--ids=IDS | --ids-file=IDSFILE]
                                                                    [--names=NAMES | --names-file=NAMESFILE]
                                                                    [--vendor=VENDOR | --vendor-file=VENDORFILE]
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --cves
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --groups
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --group-policy
                                                                    [--ids=IDS | --ids-file=IDSFILE]
                                                                    [--malicious-policy=MALPOLICY]
                                                                    [--suspicious-policy=SUPOLICY]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --group-move-agent
                                                                    [--ids=IDS | --ids-file=IDSFILE]
                                                                    [--names=NAMES | --names-file=NAMESFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --sites
                                                                    [--payload=PAYLOAD]
                                                                    [options]
    oudjat connectors.edr.sentinelone (-t TARGET | --target TARGET) --sites-by-name
                                                                    [--site-list=SITELIST | --site-file=SITEFILE]
                                                                    [--payload=PAYLOAD]
                                                                    [options]

Options:
    --agents                            retrieve S1 agents details
    --agents-export                     export flat agent data
    --move-agent-site                   move one or multiple agents to a site based on its id
    --cves                              retrieve CVEs detected by S1
    --threats                           retrieve threats detected by S1
    --threats-verdict                   change the verdict of filtered threats
    --threats-incident                  change the verdict and status of filtered threats
    --applications                      retrieve an inventory of applications detected by S1
    --applications-with-risks           retrieve an inventory of applications detected by S1 that present a security risk
    --applications-cves                 retrieve CVEs for specific application(s)
    --groups                            retrieve groups
    --group-policy                      update the policy of the specified groups
    --group-move-agent                  move agents into specified group
    --sites                             retrieve sites
    --sites-by-name                     retrieve sites by name
    --auto                              trigger auto mode. See the doc for full usage details
    --filter=FILTER                     provide a JSON filter to narrow down selection
    --ids=IDS                           a list of IDs to narrow down selection. See the doc for full usage details
    --ids-file=IDSFILE                  a list of IDs (as a file) to narrow down selection. See the doc for full usage details
    --malicious-policy=MALPOLICY        specify the malicious policy for a group or agent
    --names=NAMES                       a list of names to narrow down selection. See the doc for full usage details
    --names-file=NAMESFILE              a list of names (as a file) to narrow down selection. See the doc for full usage details
    --path=PATH                         a path of a file or process to narrow down selection, See the doc for full usage details
    --payload=PAYLOAD                   a JSON payload to pass additional query parameters
    --sites-list=SITELIST               a list of site IDs or names
    --sites-file=SITEFILE               a list of site IDs or names (as file)
    --status=STATUS                     specify an incident status to an alert or a threat
    --status-filter=STATUSFILTER       a list of incident statuses for alert/threat selection. See the doc for full usage details
    --suspicious-policy=SUPOLICY        specify the suspicious policy for a group or agent
    --vendor=VENDOR                     a list of application vendor for CVEs/application selection.
    --vendor-file=VENDORFILE            a list of application vendor (as a file) for CVEs/application selection.
    --verdict=VERDICT                   specify an incident analyst verdict to an alert or a threat
    --verdict-filter=VERDICTFILTER     a list of incident statuses for alert/threat selection. See the doc for full usage details
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

        if self._is_opt_present("--creds-service"):
            self.connector.set_creds_from_svc_name(self.options["--creds-service"])

        self.connector.connect()

        self._opt_map: "CommandMappingRegistry" = {
            "--auto": lambda opt, _: self._is_opt_present(opt),
            "--filter": lambda _, v: orjson.loads(self._ensure_json(v)),
            "--ids": lambda opt, _: self._unify_str_opt(opt, "--ids-file"),
            "--malicious-policy": None,
            "--names": lambda opt, _: self._unify_str_opt(opt, "--names-file"),
            "--path": None,
            "--payload": lambda _, v: orjson.loads(self._ensure_json(v)),
            "--sites-list": lambda opt, _: self._unify_str_opt(opt, "--site-file"),
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
                    "site_ids": "--sites-list",
                    "payload": "--payload",
                },
            ),
            # Export flat agent data
            "--agents-export": (
                self.connector.agents_export,
                {
                    "site_ids": "--sites-list",
                    "payload": "--payload",
                },
            ),
            # Move one or multiple agents to a site based on its id
            "--move-agent-site": (
                self.connector.move_agent_to_site,
                {
                    "site_id": ("--sites-list", lambda lst: next(iter(lst))),
                    "agent_name": "--names",
                },
            ),
            # Retrieve threats detected by S1
            "--threats": (
                self.connector.threats,
                {
                    "site_ids": "--sites-list",
                    "payload": "--payload",
                },
            ),
            # Change the verdict of filtered threats
            "--threats-verdict": (
                self.connector.threat_verdict,
                {
                    "verdict": "--verdict",
                    "threat_ids": "--ids",
                    "site_ids": "--sites-list",
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
                    "site_ids": "--sites-list",
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
                    "site_ids": "--sites-list",
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
                    "site_ids": "--sites-list",
                    "payload": "--payload",
                },
            ),
            # Retrieve CVEs detected by S1
            "--cves": (
                self.connector.cves,
                {
                    "site_ids": "--sites-list",
                    "payload": "--payload",
                },
            ),
            # Retrieve groups
            "--groups": (
                self.connector.groups,
                {
                    "site_ids": "--sites-list",
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
                    "site_name": "--sites-list",
                    "payload": "--payload",
                },
            ),
        }

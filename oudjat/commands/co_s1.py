"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

from oudjat.connectors.edr.sentinelone import S1Connector
from oudjat.utils.doc_builder import DocBuilder

from .base import CmdOpt, CmdProps, CmdUsage, CmdUsageOpt
from .connector_command import ConnectorCommand


class S1ConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the S1Connector.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps(
        "connectors.edr.sentinelone",
        "A command to interact with SentinelOne API through oudjat S1Connector",
    )

    __cmd_props__.options = {
        "--auto": CmdOpt(
            "Trigger auto mode. See the doc for full usage details",
        ),
        "--auto-mitigation-action": CmdOpt(
            "Specify the automatic mitigation action",
            arg="AUTOMITIGATION",
        ),
        "--creds-service": CmdOpt(
            "A credential service name to retrieve username and password from",
            short="c",
            arg="SERVICE",
        ),
        "--filter": CmdOpt(
            "Provide a JSON filter to narrow down selection",
            arg="FILTER",
        ),
        "--ids": CmdOpt(
            "A list of IDs to narrow down selection. See the doc for full usage details",
            arg="IDS",
        ),
        "--malicious-policy": CmdOpt(
            "Specify the malicious policy for a group or agent",
            arg="MALPOLICY",
        ),
        "--names": CmdOpt(
            "A list of names to narrow down selection",
            arg="NAMES",
        ),
        "--password": CmdOpt(
            "The password used for authentication",
            short="p",
            arg="PASS",
        ),
        "--path": CmdOpt(
            "A path of a file or process to narrow down selection",
            arg="PATH",
        ),
        "--payload": CmdOpt(
            "A JSON payload to pass additional query parameters",
            arg="PAYLOAD",
        ),
        "--severities": CmdOpt(
            "A list severity numbers",
            arg="SEVERITIES",
        ),
        "--sites-list": CmdOpt(
            "A list of site IDs or names",
            arg="SITES",
        ),
        "--status": CmdOpt(
            "Specify an incident status to an alert or a threat",
            arg="STATUS",
        ),
        "--status-filter": CmdOpt(
            "A list of incident statuses for alert/threat selection",
            arg="STATUSFILTER",
        ),
        "--suspicious-policy": CmdOpt(
            "Specify the suspicious policy for a group or agent",
            arg="SUPOLICY",
        ),
        "--target": CmdOpt(
            "Specify the SentinelOne URL to query",
            short="t",
            arg="TARGET",
        ),
        "--username": CmdOpt(
            "The username used for authentication",
            short="u",
            arg="USER",
        ),
        "--vendors": CmdOpt(
            "A list of application vendor for CVEs/application selection",
            arg="VENDORS",
        ),
        "--verdict": CmdOpt(
            "Specify an incident analyst verdict to an alert or a threat",
            arg="VERDICT",
        ),
        "--verdict-filter": CmdOpt(
            "a list of incident statuses for alert/threat selection",
            arg="VERDICTFILTER",
        ),
    }

    __cmd_props__.usages = {
        # Agents
        "agents": CmdUsage(
            "Export S1 agents details",
            (
                "--agents",
                "[--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "agents-export": CmdUsage(
            "Export flat agent data",
            (
                "--agents-export",
                "[--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "move-agent-site": CmdUsage(
            "Move one or multiple agents to a site based on its id",
            (
                "--move-agent-site",
                "[--sites-list=SITES] [--names=NAMES]",
            ),
            {
                "site_id": CmdUsageOpt("--sites-list"),
                "agent_name": CmdUsageOpt("--names"),
            },
        ),
        # Threats
        "threats": CmdUsage(
            "Retrieve threats detected by S1",
            (
                "--threats",
                "[--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "threats-verdict": CmdUsage(
            "Change the verdict of filtered threats",
            (
                "--threats-verdict",
                "[--verdict=VERDICT] [--ids=IDS] [--sites-list=SITES] [--status-filter=STATUSFILTER] [--verdict-filter=VERDICTFILTER] [--path=PATH] [--filter=FILTER]",
            ),
            {
                "verdict": CmdUsageOpt("--verdict"),
                "threat_ids": CmdUsageOpt("--ids"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "status_filter": CmdUsageOpt("--status-filter"),
                "verdict_filter": CmdUsageOpt("--verdict-filter"),
                "file_path": CmdUsageOpt("--path"),
                "threat_filter": CmdUsageOpt("--filter"),
            },
        ),
        "threats-incident": CmdUsage(
            "Change the verdict and status of filtered threats",
            (
                "--threats-incident",
                "(--status=STATUS --verdict=VERDICT) [--ids=IDS] [--sites-list=SITES] [--status-filter=STATUSFILTER] [--verdict-filter=VERDICTFILTER] [--path=PATH] [--auto] [--filter=FILTER]",
            ),
            {
                "status": CmdUsageOpt("--status"),
                "verdict": CmdUsageOpt("--verdict"),
                "threat_ids": CmdUsageOpt("--ids"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "status_filter": CmdUsageOpt("--status-filter"),
                "verdict_filter": CmdUsageOpt("--verdict-filter"),
                "file_path": CmdUsageOpt("--path"),
                "auto": CmdUsageOpt("--auto"),
                "threat_filter": CmdUsageOpt("--filter"),
            },
        ),
        # Alerts
        "alert-verdict": CmdUsage(
            "Change the verdict of filtered alerts",
            (
                "--alert-verdict",
                "[--verdict=VERDICT] [--ids=IDS] [--sites-list=SITES] [--status-filter=STATUSFILTER] [--verdict-filter=VERDICTFILTER] [--path=PATH] [--filter=FILTER]",
            ),
            {
                "verdict": CmdUsageOpt("--verdict"),
                "alert_ids": CmdUsageOpt("--ids"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "status_filter": CmdUsageOpt("--status-filter"),
                "verdict_filter": CmdUsageOpt("--verdict-filter"),
                "file_path": CmdUsageOpt("--path"),
                "alert_filter": CmdUsageOpt("--filter"),
            },
        ),
        "alert-incident": CmdUsage(
            "Change the status of filtered alerts",
            (
                "--alert-incident",
                "[--status=STATUS] [--ids=IDS] [--sites-list=SITES] [--status-filter=STATUSFILTER] [--verdict-filter=VERDICTFILTER] [--path=PATH] [--auto] [--filter=FILTER]",
            ),
            {
                "status": CmdUsageOpt("--status"),
                "alert_ids": CmdUsageOpt("--ids"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "status_filter": CmdUsageOpt("--status-filter"),
                "verdict_filter": CmdUsageOpt("--verdict-filter"),
                "file_path": CmdUsageOpt("--path"),
                "auto": CmdUsageOpt("--auto"),
                "alert_filter": CmdUsageOpt("--filter"),
            },
        ),
        # Applications
        "applications": CmdUsage(
            "Retrieve an inventory of applications detected by S1",
            (
                "--applications",
                "[--names=NAMES] [--vendors=VENDOR] [--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "names": CmdUsageOpt("--names"),
                "vendors": CmdUsageOpt("--vendors"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "applications-endpoints": CmdUsage(
            "Retrieve an inventory of endpoints for a specific application",
            (
                "--applications-endpoints",
                "[--names=NAMES] [--vendors=VENDOR] [--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "name": CmdUsageOpt("--names", transform=lambda lst: next(iter(lst))),
                "vendor": CmdUsageOpt("--vendors", transform=",".join),
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "applications-with-risks": CmdUsage(
            "Retrieve an inventory of applications detected by S1 that present a security risk",
            (
                "--applications-with-risks",
                "[--vendors=VENDOR] [--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "vendors": CmdUsageOpt("--vendors"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "applications-cves": CmdUsage(
            "Retrieve CVEs for specific application(s)",
            (
                "--applications-cves",
                "[--ids=IDS] [--names=NAMES] [--vendors=VENDORS] [--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "ids": CmdUsageOpt("--ids"),
                "name": CmdUsageOpt("--names"),
                "vendor": CmdUsageOpt("--vendors"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "cves": CmdUsage(
            "Retrieve CVEs detected by S1",
            (
                "--cves",
                "[--ids=IDS] [--severities=SEVERITIES] [--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "ids": CmdUsageOpt("--ids"),
                "severities": CmdUsageOpt("--severities"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        # Groups
        "groups": CmdUsage(
            "Retrieve groups",
            (
                "--groups",
                "[--names=NAMES] [--sites-list=SITES] [--payload=PAYLOAD]",
            ),
            {
                "names": CmdUsageOpt("--names"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "group-policy": CmdUsage(
            "Retrieve the policy of a specific group",
            (
                "--group-policy",
                "[--ids=IDS]",
            ),
            {
                "group_id": CmdUsageOpt("--ids", transform=lambda lst: next(iter(lst))),
            },
        ),
        "group-policy-update": CmdUsage(
            "Update the policy of the specified groups",
            (
                "--group-policy-update",
                "[--ids=IDS] [--malicious-policy=MALPOLICY] [--suspicious-policy=SUPOLICY] [--payload=PAYLOAD]",
            ),
            {
                "group_id": CmdUsageOpt("--ids"),
                "malicious_mitigation": CmdUsageOpt("--malicious-policy"),
                "suspicious_mitigation": CmdUsageOpt("--suspicious-policy"),
                "auto_mitigation_action": CmdUsageOpt("--auto-mitigation-action"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "group-move-agent": CmdUsage(
            "Move agents into specified group",
            (
                "--group-move-agent",
                "[--ids=IDS] [--names=NAMES] [--payload=PAYLOAD]",
            ),
            {
                "group_id": CmdUsageOpt("--ids"),
                "agent_name": CmdUsageOpt("--names"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        # Sites
        "sites": CmdUsage(
            "Retrieve sites data",
            (
                "--sites",
                "[--payload=PAYLOAD]",
            ),
            {
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "sites-by-name": CmdUsage(
            "Retrieve sites by names",
            (
                "--sites-by-name",
                "[--names=NAMES] [--payload=PAYLOAD]",
            ),
            {
                "site_name": CmdUsageOpt("--names"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
    }

    __cmd_props__.prepend_usages(
        "(-t=TARGET | --target=TARGET) (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])"
    )
    __cmd_props__.append_usages("[options]")

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

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

        # Retrieve credentials from credential service if provided
        if self._is_opt_present("--creds-service"):
            self.connector.set_creds_from_service(
                self.options["--creds-service"], self.options["--username"]
            )

        self.connector.connect()

        # Options transform based on instance
        self.__cmd_props__.opts_transform(
            {
                "--auto": lambda opt, _: self._is_opt_present(opt),
                "--ids": lambda opt, _: self._unify_str_opt(opt),
                "--filter": lambda _, v: self._parse_payload(v),
                "--names": lambda opt, _: self._unify_str_opt(opt),
                "--payload": lambda _, v: self._parse_payload(v),
                "--severities": lambda opt, _: list(map(int, self._unify_str_opt(opt))),
                "--sites-list": lambda opt, _: self._unify_str_opt(opt),
                "--status-filter": lambda _, v: self._unify_str_opt(v),
                "--vendors": lambda opt, _: self._unify_str_opt(opt),
                "--verdict-filter": lambda _, v: self._unify_str_opt(v),
            }
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
                "agents": self.connector.agents,
                "agents-export": self.connector.agents_export,
                "move-agent-site": self.connector.move_agent_to_site,
                "threats": self.connector.threats,
                "threats-verdict": self.connector.threat_verdict,
                "threats-incident": self.connector.threat_incident,
                "alert-verdict": self.connector.alert_verdict,
                "alert-incident": self.connector.alert_incident,
                "applications": self.connector.applications,
                "applications-endpoints": self.connector.applications_endpoints,
                "applications-with-risks": self.connector.applications_with_risks,
                "applications-cves": self.connector.application_cves,
                "cves": self.connector.cves,
                "groups": self.connector.groups,
                "group-policy": self.connector.group_policy,
                "group-policy-update": self.connector.group_policy_update,
                "group-move-agent": self.connector.group_move_agent,
                "sites": self.connector.sites,
                "sites-by-name": self.connector.sites_by_name,
            }
        )

"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

import orjson

from oudjat.connectors.edr.sentinelone import S1Connector
from oudjat.utils.doc_builder import DocBuilder
from oudjat.utils.string_utils import StringUtils

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
        "--password": CmdOpt(
            "The password used for authentication",
            short="p",
            arg="PASS",
        ),
        "--creds-service": CmdOpt(
            "A credential service name to retrieve username and password from",
            short="c",
            arg="SERVICE",
        ),
        "--auto": CmdOpt(
            "Trigger auto mode. See the doc for full usage details",
        ),
        "--filter": CmdOpt(
            "Provide a JSON filter to narrow down selection",
            arg="FILTER",
            transform=lambda _, v: orjson.loads(StringUtils.jsonify(v)),
        ),
        "--ids": CmdOpt(
            "A list of IDs to narrow down selection. See the doc for full usage details",
            arg="IDS",
        ),
        "--ids-file": CmdOpt(
            "A list of IDs (as a file) to narrow down selection",
            arg="IDSFILE",
        ),
        "--malicious-policy": CmdOpt(
            "Specify the malicious policy for a group or agent",
            arg="MALPOLICY",
        ),
        "--names": CmdOpt(
            "A list of names to narrow down selection",
            arg="NAMES",
        ),
        "--names-file": CmdOpt(
            "A list of names (as a file) to narrow down selection",
            arg="NAMESFILE",
        ),
        "--path": CmdOpt(
            "A path of a file or process to narrow down selection",
            arg="PATH",
        ),
        "--payload": CmdOpt(
            "A JSON payload to pass additional query parameters",
            arg="PAYLOAD",
            transform=lambda _, v: orjson.loads(StringUtils.jsonify(v)),
        ),
        "--sites-list": CmdOpt(
            "A list of site IDs or names",
            arg="SITELIST",
        ),
        "--sites-file": CmdOpt(
            "A list of site IDs or names (as file)",
            arg="SITESFILE",
        ),
        "--status": CmdOpt(
            "Specify an incident status to an alert or a threat",
            arg="STATUS",
        ),
        "--status-filter": CmdOpt(
            "A list of incident statuses for alert/threat selection",
            arg="STATUSFILTER",
            transform=lambda opt, v: v.split(","),
        ),
        "--suspicious-policy": CmdOpt(
            "Specify the suspicious policy for a group or agent",
            arg="SUPOLICY",
        ),
        "--vendors": CmdOpt(
            "A list of application vendor for CVEs/application selection",
            arg="VENDOR",
        ),
        "--vendors-file": CmdOpt(
            "A list of application vendor (as a file) for CVEs/application selection.",
            arg="VENDORSFILE",
        ),
        "--verdict": CmdOpt(
            "Specify an incident analyst verdict to an alert or a threat",
            arg="VERDICT",
        ),
        "--verdict-filters": CmdOpt(
            "a list of incident statuses for alert/threat selection",
            arg="VERDICTFILTER",
            transform=lambda opt, v: v.split(","),
        ),
    }

    __cmd_props__.usages = {
        "--agents": CmdUsage(
            CmdOpt("Export S1 agents details"),
            "--agents [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--agents-export": CmdUsage(
            CmdOpt("Export flat agent data"),
            "--agents-export [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--move-agent-site": CmdUsage(
            CmdOpt("Move one or multiple agents to a site based on its id"),
            "--move-agent-site [--sites-list=SITELIST | --sites-file=SITEFILE] [--names=NAMES | --names-file=NAMESFILE] [options]",
            {
                "site_id": CmdUsageOpt("--sites-list", lambda lst: next(iter(lst))),
                "agent_name": CmdUsageOpt("--names"),
            },
        ),
        # Threats
        "--threats": CmdUsage(
            CmdOpt("Retrieve threats detected by S1"),
            "--threats [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--threats-verdict": CmdUsage(
            CmdOpt("Change the verdict of filtered threats (threats:malicious / alerts:suspicious)"),
            "--threats-verdict [--verdict=VERDICT] [--ids=IDS | --ids-file=IDSFILE] [--sites-list=SITELIST | --sites-file=SITEFILE] [--status-filter=STATUSFILTER] [--verdict-filter=VERDICTFILTER] [--path=PATH] [--filter=FILTER] [options]",
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
        "--threats-incident": CmdUsage(
            CmdOpt("Change the verdict and status of filtered threats (threats:malicious / alerts:suspicious)"),
            "--threats-incident [--status=STATUS] [--verdict=VERDICT] [--ids=IDS | --ids-file=IDSFILE] [--sites-list=SITELIST | --sites-file=SITEFILE] [--status-filter=STATUSFILTER] [--verdict-filter=VERDICTFILTER] [--path=PATH] [--auto] [--filter=FILTER] [options]",
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
        "--alert-verdict": CmdUsage(
            CmdOpt("Change the verdict of filtered alerts (threats:malicious / alerts:suspicious)"),
            "--alert-verdict [--verdict=VERDICT] [--ids=IDS | --ids-file=IDSFILE] [--sites-list=SITELIST | --sites-file=SITEFILE] [--status-filter=STATUSFILTER] [--verdict-filter=VERDICTFILTER] [--path=PATH] [--filter=FILTER] [options]",
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
        "--alert-incident": CmdUsage(
            CmdOpt("Change the status of filtered alerts (threats:malicious / alerts:suspicious)"),
            "--alert-incident [--status=STATUS] [--ids=IDS | --ids-file=IDSFILE] [--sites-list=SITELIST | --sites-file=SITEFILE] [--status-filter=STATUSFILTER] [--verdict-filter=VERDICTFILTER] [--path=PATH] [--auto] [--filter=FILTER] [options]",
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
        "--applications": CmdUsage(
            CmdOpt("Retrieve an inventory of applications detected by S1"),
            "--applications [--vendors=VENDOR | --vendors-file=VENDORFILE] [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "vendors": CmdUsageOpt("--vendors"),
                "site_ids": CmdUsageOpt("--sites"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--applications-with-risks": CmdUsage(
            CmdOpt(
                "Retrieve an inventory of applications detected by S1 that present a security risk"
            ),
            "--applications-with-risks [--vendors=VENDOR | --vendors-file=VENDORFILE] [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "vendors": CmdUsageOpt("--vendors"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--applications-cves": CmdUsage(
            CmdOpt("Retrieve CVEs for specific application(s)"),
            "--applications-cves [--ids=IDS | --ids-file=IDSFILE] [--names=NAMES | --names-file=NAMESFILE] [--vendors=VENDOR | --vendors-file=VENDORFILE] [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "appliation_ids": CmdUsageOpt("--ids"),
                "appliation_name": CmdUsageOpt("--names"),
                "application_vendor": CmdUsageOpt("--vendors"),
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--cves": CmdUsage(
            CmdOpt("Retrieve CVEs detected by S1"),
            "--cves [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--groups": CmdUsage(
            CmdOpt("Retrieve groups"),
            "--groups [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "site_ids": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--group-policy": CmdUsage(
            CmdOpt("Update the policy of the specified groups"),
            "--group-policy [--ids=IDS | --ids-file=IDSFILE] [--malicious-policy=MALPOLICY] [--suspicious-policy=SUPOLICY] [--payload=PAYLOAD] [options]",
            {
                "group_id": CmdUsageOpt("--ids"),
                "malicious_mitigation": CmdUsageOpt("--malicious-policy"),
                "suspicious_mitigation": CmdUsageOpt("--suspicious-policy"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--group-move-agent": CmdUsage(
            CmdOpt("Move agents into specified group"),
            "--group-move-agent [--ids=IDS | --ids-file=IDSFILE] [--names=NAMES | --names-file=NAMESFILE] [--payload=PAYLOAD] [options]",
            {
                "group_id": CmdUsageOpt("--ids", lambda lst: next(iter(lst))),
                "agent_name": CmdUsageOpt("--names"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--sites": CmdUsage(
            CmdOpt("Retrieve sites"),
            "--sites [--payload=PAYLOAD] [options]",
            {
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--sites-by-name": CmdUsage(
            CmdOpt("Retrieve sites by names"),
            "--sites-by-name [--sites-list=SITELIST | --sites-file=SITEFILE] [--payload=PAYLOAD] [options]",
            {
                "site_name": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
    }

    __cmd_props__.prepend_usages(
        "(-t=TARGET | --target TARGET) (--username=USER --password=PASS | --creds-service=SERVICE)"
    )

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
            self.connector.set_creds_from_svc_name(self.options["--creds-service"])

        self.connector.connect()

        # Options transform based on instance
        self.__cmd_props__.opts_transform(
            {
                "--auto": lambda opt, _: self._is_opt_present(opt),
                "--ids": lambda opt, _: self._unify_str_opt(opt, "--ids-file"),
                "--ids-file": lambda opt, _: self._unify_str_opt("--ids", opt),
                "--names": lambda opt, _: self._unify_str_opt(opt, "--names-file"),
                "--names-file": lambda opt, _: self._unify_str_opt("--names-list", opt),
                "--sites-list": lambda opt, _: self._unify_str_opt(opt, "--sites-file"),
                "--sites-file": lambda opt, _: self._unify_str_opt("--sites-list", opt),
                "--vendors": lambda opt, _: self._unify_str_opt(opt, "--vendor-file"),
                "--vendors-file": lambda opt, _: self._unify_str_opt("--vendor-list", opt),
            }
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--agents": self.connector.agents,
                "--agents-export": self.connector.agents_export,
                "--move-agent-site": self.connector.move_agent_to_site,
                "--threats": self.connector.threats,
                "--threats-verdict": self.connector.threat_verdict,
                "--threats-incident": self.connector.threat_incident,
                "--applications": self.connector.applications,
                "--applications-with-risks": self.connector.applications_with_risks,
                "--applications-cves": self.connector.application_cves,
                "--cves": self.connector.cves,
                "--groups": self.connector.groups,
                "--group-policy": self.connector.group_policy_update,
                "--group-move-agent": self.connector.group_move_agent,
                "--sites": self.connector.sites,
                "--sites-by-name": self.connector.sites_by_name,
            }
        )

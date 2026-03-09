"""
A command module to handle interactions with vulnerability databases.
"""

from typing import Any

from oudjat.connectors.vuln import CVEConnector, CVEDatabase
from oudjat.connectors.vuln.cve_load_balancer import CVELoadBalancer
from oudjat.utils.doc_builder import DocBuilder

from .base import (
    CmdOpt,
    CmdProps,
    CmdUsage,
    CmdUsageOpt,
)
from .connector_command import ConnectorCommand


class VulnConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the EndOfLifeConnector.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps(
        "connectors.vulns",
        "A command to interact with some vulnerability databases (CVE.org, Nist, Circl)",
    )
    __cmd_props__.options = {
        "--target": CmdOpt(
            "Specify the name database to use (cveorg, nist or circl)",
            short="t",
            arg="TARGET",
            default="cveorg",
        ),
        "--cves": CmdOpt(
            "Specify cve references to retrieve data for",
            arg="CVES",
        ),
    }

    __cmd_props__.usages = {
        "--db": CmdUsage(
            CmdOpt(
                "Use a specific database to retrieve CVE data. Keep in mind APIs are requests/min restricted",
            ),
            "--db (-t=TARGET | --target=TARGET) (--cves=CVES) [options]",
            {
                "cves": CmdUsageOpt("--cves"),
            },
        ),
        "--auto": CmdUsage(
            CmdOpt(
                "Use load balancing to retrieve data dynamically from available CVE APIs",
            ),
            "--auto (--cves=CVES) [options]",
            {
                "cves": CmdUsageOpt("--cves"),
            },
        ),
    }

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new EOLConnectorCommand.

        Args:
            options (dict[str, Any]): Provided options
        """

        super().__init__(options, False)

        connector_cls = CVEDatabase.CVEORG.connector
        if self.options["--db"]:
            CVEDatabase[self.options["--db"].upper()].connector

        self.connector: "CVEConnector" = connector_cls()

        self.__cmd_props__.opts_transform(
            {
                "--cves": lambda opt, _: self._unify_str_opt(opt),
            },
        )

        self._balancer: "CVELoadBalancer" = CVELoadBalancer()

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--db": self.connector.fetch,
                "--auto": self._balancer.fetch,
            }
        )

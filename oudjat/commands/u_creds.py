"""
A command module to handle credential utility.
"""

from typing import Any

from oudjat.connectors.vuln import CVEConnector, CVEDatabase
from oudjat.utils.credentials import CredentialUtils
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
    A class to provide an access to various CVE databases.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps(
        "utils.credentials",
        "A command to handle services credentials through the oudjat credential helper",
    )
    __cmd_props__.options = {
        "--service": CmdOpt(
            "Specify the name of the service you want to handle credentials for",
            short="s",
            arg="SERVICE",
        ),
        "--username": CmdOpt(
            "Specify the credentials username",
            short="u",
            arg="USERNAME",
        ),
    }

    __cmd_props__.usages = {
        "--db": CmdUsage(
            CmdOpt(
                "Use a specific database to retrieve CVE data. Keep in mind APIs are requests/min restricted",
            ),
            "--db (-t=TARGET | --target=TARGET) (--cves=CVES) [--payload=PAYLOAD] [options]",
            {
                "cves": CmdUsageOpt("--cves"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--auto": CmdUsage(
            CmdOpt(
                "Use load balancing to retrieve data dynamically from available CVE APIs",
            ),
            "--auto (--cves=CVES) [--payload=PAYLOAD] [options]",
            {
                "cves": CmdUsageOpt("--cves"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
    }

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new VulnConnectorCommand.

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
                "--payload": lambda _, v: self._parse_payload(v),
            },
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--db": self.connector.fetch,
            }
        )

"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

from oudjat.connectors.tenable.sc import TenableSCConnector
from oudjat.utils.doc_builder import DocBuilder

from .base import (
    CmdOpt,
    CmdProps,
    CmdUsage,
    CmdUsageOpt,
)
from .connector_command import ConnectorCommand


class TenableSCConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the TenableSCConnector.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps(
        "connectors.tenable.sc",
        "A command to interact with Tenable.sc API through the oudjat TenableSCConnector",
    )
    __cmd_props__.options = {
        "--severities": CmdOpt(
            "Specify severity numbers (1:MINOR,2:MODERATE,3:HIGH,4:CRITICAL)",
            arg="SEVERITIES",
        ),

    }

    __cmd_props__.usages = {
        "--vulns": CmdUsage(
            CmdOpt("Retrieve vulnerabilities that match the provided severities and filters"),
            "--vulns [--severities=SEVERITIES]",
            {
                "": CmdUsageOpt("--sites-list"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
    }

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new .

        Args:
            options (dict[str, Any]): Provided options
        """

        super().__init__(options, False)
        con_args = {"target": self.options["--target"]}
        if self.options["--username"] and self.options["--password"]:
            con_args.update(
                {
                    "username": self.options["--username"],
                    "password": self.options["--password"],
                }
            )

        self.connector: "TenableSCConnector" = TenableSCConnector(**con_args)

        # Retrieve credentials from credential service if provided
        if self._is_opt_present("--creds-service"):
            self.connector.set_creds_from_svc_name(self.options["--creds-service"])

        self.connector.connect()

        # Options transform based on instance
        self.__cmd_props__.opts_transform(
            {
                "--severities": lambda opt, _: self._unify_str_opt(opt),
            }
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
            }
        )

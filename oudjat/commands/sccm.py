"""
A command module to handle interactions with an SCCM server.
"""

from typing import Any

from oudjat.connectors.microsoft.sccm.sccm_connector import SCCMConnector
from oudjat.utils.doc_builder import DocBuilder

from .base import (
    CmdOpt,
    CmdProps,
    CmdUsage,
    CmdUsageOpt,
)
from .connector_command import ConnectorCommand


class SCCMConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to various CVE databases.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps(
        "connectors.sccm",
        "A command to interact with an SCCM server through the oudjat SCCMConnector",
    )
    __cmd_props__.options = {
        "--target": CmdOpt(
            "Specify the target server",
            short="t",
            arg="TARGET",
        ),
    }

    __cmd_props__.usages = {
        "--": CmdUsage(
            CmdOpt(
                "",
            ),
            "-- (-t=TARGET | --target=TARGET)",
            {
            },
        ),
    }

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new SCCMConnectorCommand.

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

        self.connector: "SCCMConnector" = SCCMConnector(**con_args)

        self.__cmd_props__.opts_transform(
            {
            },
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
            }
        )

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
        "--query": CmdOpt(
            "Specify the SQL query file",
            short="q",
            arg="QUERY",
        ),
        "--target": CmdOpt(
            "Specify the target server",
            short="t",
            arg="TARGET",
        ),
        "--db": CmdOpt(
            "The name of the database to query",
            arg="DBNAME",
        ),
        "--driver": CmdOpt(
            "The ODBC driver to use ",
            arg="DRIVER",
        ),
        "--format": CmdOpt(
            "A format JSON dictionary",
            arg="FORMAT",
        ),
    }

    __cmd_props__.usages = {
        "--target": CmdUsage(
            "Query the specified target server",
            (
                "(-t=TARGET | --target=TARGET)",
                "(--username=USER --password=PASS | --creds-service=SERVICE [--username=USER]) (--db=DBNAME) [--driver=DRIVER] (-q=QUERY | --query=QUERY) [--format=FORMAT]",
            ),
            {
                "payload": CmdUsageOpt("--query"),
                "payload_fmt": CmdUsageOpt("--format"),
            },
        ),
    }

    __cmd_props__.append_usages("[options]")

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

        con_args["db_name"] = self.options["--db"]

        self.connector: "SCCMConnector" = SCCMConnector(**con_args)

        self.__cmd_props__.opts_transform(
            {
                "--query": lambda opt, _: self._unify_str_opt(opt),
                "--format": lambda _, v: self._parse_payload(v),
            },
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--target": self.connector.fetch,
            },
        )

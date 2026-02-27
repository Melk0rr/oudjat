"""
A command module to handle interactions with an LDAP server.
"""

from typing import Any

from oudjat.connectors.ldap import LDAPConnector
from oudjat.utils.doc_builder import DocBuilder

from .base import (
    CmdOpt,
    CmdProps,
    CmdUsage,
    CmdUsageOpt,
)
from .connector_command import ConnectorCommand


class LDAPConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the LDAPConnector.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps(
        "connectors.ldap",
        "A command to interact with an LDAP server through the oudjat LDAPConnector",
    )
    __cmd_props__.options = {}

    __cmd_props__.usages = {}

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new EOLConnectorCommand.

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

        self.connector: "LDAPConnector" = LDAPConnector(**con_args)

        # Retrieve credentials from credential service if provided
        if self._is_opt_present("--creds-service"):
            self.connector.set_creds_from_svc_name(self.options["--creds-service"])

        self.connector.connect()

        # Usage backends
        self.__cmd_props__.backends({})

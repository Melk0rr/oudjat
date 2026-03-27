"""
A command module to handle credential utility.
"""

from datetime import datetime
from typing import Any

from oudjat.utils.credentials import CredentialUtils
from oudjat.utils.doc_builder import DocBuilder
from oudjat.utils.types import DataType

from .base import (
    CmdOpt,
    CmdProps,
    CmdUsage,
    CmdUsageOpt,
)
from .connector_command import ConnectorCommand


class CredentialUtilCmd(ConnectorCommand):
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
        "--new": CmdUsage(
            CmdOpt(
                "Register a new set of credentials for a specified service and user",
            ),
            "--new (-s=SERVICE | --service=SERVICE) [-u=USERNAME | --username=USERNAME]",
            {
                "service": CmdUsageOpt("--service"),
                "username": CmdUsageOpt("--username"),
            },
        ),
        "--edit": CmdUsage(
            CmdOpt(
                "Edit the password for the specified service and user",
            ),
            "--edit (-s=SERVICE | --service=SERVICE) (-u=USERNAME | --username=USERNAME)",
            {
                "service": CmdUsageOpt("--service"),
                "username": CmdUsageOpt("--username"),
            },
        ),
        "--delete": CmdUsage(
            CmdOpt(
                "Delete the password for the specified service and user",
            ),
            "--delete (-s=SERVICE | --service=SERVICE) [-u=USERNAME | --username=USERNAME]",
            {
                "service": CmdUsageOpt("--service"),
                "username": CmdUsageOpt("--username"),
            },
        ),
    }

    __cmd_props__.append_usages("[options]")

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new VulnConnectorCommand.

        Args:
            options (dict[str, Any]): Provided options
        """

        super().__init__(options, False)

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--new": self._new_creds,
                "--edit": self._edit_creds,
                "--delete": self._delete_creds,
            }
        )

    def _new_creds(self, service: str, username: str | None = None) -> "DataType":
        """
        Wrap CredentialUtils save_credentials method to match backend signature.

        Args:
            service (str) : The service the credentials are for
            username (str): The credentials username

        Returns:
            DataType: A simple output to match backend signature
        """

        _ = CredentialUtils.save_credentials(service, username)

        return [
            {
                "utils": self.__cmd_props__.name,
                "action": "new",
                "service": service,
                "username": username,
                "time": datetime.now()
            }
        ]

    def _edit_creds(self, service: str, username: str) -> "DataType":
        """
        Wrap CredentialUtils edit_credentials method to match backend signature.

        Args:
            service (str) : The service the credentials are for
            username (str): The credentials username

        Returns:
            DataType: A simple output to match backend signature
        """

        _ = CredentialUtils.edit_credentials(service, username)

        return [
            {
                "utils": self.__cmd_props__.name,
                "action": "edit",
                "service": service,
                "username": username,
                "time": datetime.now()
            }
        ]

    def _delete_creds(self, service: str, username: str = "") -> "DataType":
        """
        Wrap CredentialUtils del_credentials method to match backend signature.

        Args:
            service (str) : The service the credentials are for
            username (str): The credentials username

        Returns:
            DataType: A simple output to match backend signature
        """

        _ = CredentialUtils.del_credentials(service, username)

        return [
            {
                "utils": self.__cmd_props__.name,
                "action": "delete",
                "service": service,
                "username": username,
                "time": datetime.now()
            }
        ]

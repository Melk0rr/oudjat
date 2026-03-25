"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

from oudjat.connectors.tenable.sc import TenableSCConnector
from oudjat.connectors.tenable.sc.tsc_connector import TSCFilter
from oudjat.utils import Context
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
        "--creds-service": CmdOpt(
            "A credential service name to retrieve username and password from",
            short="c",
            arg="SERVICE",
        ),
        "--exploitable": CmdOpt(
            "Include only exploitable vulnerabilities in the results",
        ),
        "--filter": CmdOpt(
            "Provide 3 values filter to narrow down vulnerability search (attribute,operator,value)",
            arg="FILTER",
        ),
        "--fields": CmdOpt(
            "A list of attributes to return for each scan / asset lists",
            arg="FIELDS",
        ),
        "--ids": CmdOpt(
            "A list of IDs of scans or asset list",
            arg="IDS",
        ),
        "--password": CmdOpt(
            "The password used for authentication",
            short="p",
            arg="PASS",
        ),
        "--payload": CmdOpt(
            "Additional parameters to pass",
            arg="PAYLOAD",
        ),
        "--product": CmdOpt(
            "Specify a product name to retrieve vulnerabilities for",
            arg="PRODUCT",
        ),
        "--severities": CmdOpt(
            "Provide severity numbers, comma separated (1:MINOR,2:MODERATE,3:HIGH,4:CRITICAL)",
            arg="SEVERITIES",
            default="3,4"
        ),
        "--target": CmdOpt(
            "Specify the SentinelOne URL to query",
            short="t",
            arg="TARGET",
        ),
        "--tool": CmdOpt(
            "Specify an analysis tool which provides a specific vulnerability view. See the list of available tools",
            arg="TOOL",
            default="vulndetails",
        ),
        "--username": CmdOpt(
            "The username used for authentication",
            short="u",
            arg="USER",
        ),
    }

    __cmd_props__.usages = {
        "--vulns": CmdUsage(
            CmdOpt("Retrieve vulnerabilities that match the provided severities and filters"),
            "--vulns [--severities=SEVERITIES] [--tool=TOOL] [--product=PRODUCT] [--exploitable] [--filter=FILTER]... [--payload=PAYLOAD]",
            {
                "*severities": CmdUsageOpt("--severities"),
                "tool": CmdUsageOpt("--tool"),
                "product": CmdUsageOpt("--product"),
                "exploitable": CmdUsageOpt("--exploitable"),
                "filters": CmdUsageOpt("--filter"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--asset-lists": CmdUsage(
            CmdOpt("Retrieve a list of asset lists with minimal informations like list ids."),
            "--asset-lists [--filter=FILTER]... [--fields=FIELDS] [--payload=PAYLOAD]",
            {
                "scan_filter": CmdUsageOpt("--filter"),
                "fields": CmdUsageOpt("--scan-fields"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--asset-lists-details": CmdUsage(
            CmdOpt("Return the details of one or more asset lists."),
            "--asset-lists-details [--ids=IDS]",
            {
                "scan_ids": CmdUsageOpt("--ids"),
            },
        ),
        "--asset-lists-delete": CmdUsage(
            CmdOpt("Delete an asset list based on given id."),
            "--asset-lists-delete [--ids=IDS]",
            {
                "scan_ids": CmdUsageOpt("--ids"),
            },
        ),
        "--scans": CmdUsage(
            CmdOpt("Retrieve a list of scans with minimal information like scan ids"),
            "--scans [--filter=FILTER]... [--fields=FIELDS] [--payload=PAYLOAD]",
            {
                "scan_filter": CmdUsageOpt("--filter"),
                "fields": CmdUsageOpt("--fields"),
                "payload": CmdUsageOpt("--payload"),
            },
        ),
        "--scans-details": CmdUsage(
            CmdOpt("Return the details of one or more scans."),
            "--scans-details [--ids=IDS]",
            {
                "scan_ids": CmdUsageOpt("--ids"),
            },
        ),
        "--scans-delete": CmdUsage(
            CmdOpt("Delete one or more scans."),
            "--scans-delete [--ids=IDS]",
            {
                "scan_ids": CmdUsageOpt("--ids"),
            },
        ),
    }

    __cmd_props__.prepend_usages(
        "(-t=TARGET | --target=TARGET) (--username=USER --password=PASS | --creds-service=SERVICE)"
    )
    __cmd_props__.append_usages("[options]")
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
                "--fields": lambda opt, _: self._unify_str_opt(opt),
                "--filter": lambda _, v: self._parse_filter(v),
                "--payload": lambda _, v: self._parse_payload(v),
                "--severities": lambda opt, _: self._unify_str_opt(opt),
            }
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--vulns": self.connector.vulns,
                "--asset-lists": self.connector.asset_lists,
                "--asset-lists-details": self.connector.asset_lists_details,
                "--asset-lists-delete": self.connector.asset_lists_delete,
                "--scans": self.connector.scans,
                "--scans-details": self.connector.scans_details,
                "--scans-delete": self.connector.scans_delete,
            }
        )

    def _parse_filter(self, filter_str: list[str]) -> list["TSCFilter"]:
        """
        Parse filter values into tuples.

        Returns:
            list[TSCFilter]: A list of filter tuples
        """

        filters = []
        for f in filter_str:
            f_split = f.strip().split(",")

            if len(f_split) != 3:
                raise ValueError(f"{Context()}::Invalid filter provided {f}.")

            filters.append(tuple(f_split))

        return filters

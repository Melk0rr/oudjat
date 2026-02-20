"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

from oudjat.connectors.endoflife import EndOfLifeConnector
from oudjat.utils.doc_builder import DocBuilder

from .base import (
    CmdOpt,
    CmdProps,
    CmdUsage,
    CmdUsageOpt,
)
from .connector_command import ConnectorCommand


class EOLConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the S1Connector.
    """

    __cmd_props__: "CmdProps" = CmdProps(
        "connectors.endoflife",
        "A command to interact with endoflife.date API through the oudjat EndOfLifeConnector",
    )
    __cmd_props__.options = {
        "--category-name": CmdOpt(
            "Specify a product category name",
            arg="CTGNAME",
        ),
        "--full": CmdOpt(
            "If specified, retrieve full product data",
        ),
        "--product-name": CmdOpt(
            "Specify a product name",
            arg="PRODUCTNAME",
        ),
        "--release-name": CmdOpt(
            "Specify a release name (its version)",
            arg="RELNAME",
        ),
        "--tag": CmdOpt(
            "Specify one or several tag (repeatable)",
            arg="TAG",
        ),
    }

    __cmd_props__.usages = {
        "--products": CmdUsage(
            CmdOpt(
                "Retrieve all or a specific product from EOL",
            ),
            "--products [--product-name=PRODUCTNAME] [--tag=TAG]... [--full] [options]",
            {
                "product": CmdUsageOpt("--product-name"),
                "tags": CmdUsageOpt("--tag"),
                "full": CmdUsageOpt("--full"),
            },
        ),
        "--product-releases": CmdUsage(
            CmdOpt("Retrieve a product release from EOL"),
            "--product-releases [--product-name=PRODUCTNAME] [--release-name=RELNAME] [options]",
            {
                "product": CmdUsageOpt("--product-name"),
                "release": CmdUsageOpt("--release-name"),
            },
        ),
        "--linux": CmdUsage(
            CmdOpt("Retrieve linux related products"),
            "--linux [--full] [options]",
            {
                "full": CmdUsageOpt("--full"),
            },
        ),
        "--windows": CmdUsage(
            CmdOpt("Retrieve windows related products"),
            "--windows [options]",
        ),
        "--windows-server": CmdUsage(
            CmdOpt("Retrieve windows server related products"),
            "--windows-server [options]",
        ),
        "--categories": CmdUsage(
            CmdOpt("Retrieve product categories"),
            "--categories [--category-name=CTGNAME] [options]",
            {
                "category": CmdUsageOpt("--category-name"),
            },
        ),
        "--apps": CmdUsage(CmdOpt("Retrieve app category products"), "--apps [options]"),
        "--oses": CmdUsage(CmdOpt("Retrieve os category products"), "--oses [options]"),
        "--tags": CmdUsage(
            CmdOpt("Retrieve all, or a specific tag"),
            "--tags [--tag=TAG] [options]",
            {
                "tag": CmdUsageOpt("--tag", lambda lst: next(iter(lst))),
            },
        ),
    }

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new S1ConnectorCommand.

        Args:
            options (dict[str, Any]): Provided options
        """

        super().__init__(options, False)
        con_args = {"target": self.options["--target"]}

        self.connector: "EndOfLifeConnector" = EndOfLifeConnector(**con_args)

        if self._is_opt_present("--creds-service"):
            self.connector.set_creds_from_svc_name(self.options["--creds-service"])

        self.connector.connect()

        # Options transform based on instance
        self.__cmd_props__.opts_transform(
            {
                "--full": lambda opt, _: self._is_opt_present(opt),
            }
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--products": self.connector.products,
                "--product-releases": self.connector.product_releases,
                "--linux": self.connector.linux,
                "--windows": self.connector.windows,
                "--windows-server": self.connector.windows_server,
                "--categories": self.connector.categories,
                "--apps": self.connector.apps,
                "--oses": self.connector.oses,
                "--tags": self.connector.tags,
            }
        )

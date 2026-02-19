"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

from oudjat.connectors.endoflife import EndOfLifeConnector

from .base import (
    CmdHub,
    CmdOpt,
    CmdUsage,
    CmdUsageOpt,
)
from .connector_command import ConnectorCommand


class EOLConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the S1Connector.
    """

    _CMD_NAME: str = "connectors.endoflife"
    __doc__ = f"""
Usage:
    oudjat {_CMD_NAME} --products [--product-name=PRODUCTNAME] [--tag=TAG...] [--full] [options]
    oudjat {_CMD_NAME} --product-releases [--product-name=PRODUCTNAME] [--release-name=RELNAME] [options]
    oudjat {_CMD_NAME} --linux [--full] [options]
    oudjat {_CMD_NAME} --windows [options]
    oudjat {_CMD_NAME} --windows-server [options]
    oudjat {_CMD_NAME} --categories [--category-name=CTGNAME] [options]
    oudjat {_CMD_NAME} --apps [options]
    oudjat {_CMD_NAME} --oses [options]
    oudjat {_CMD_NAME} --tags [--tag=TAG] [options]

Options:
    --products                              retrieve all or a specific product
    --product-releases                      retrieve a product release
    --linux                                 retrieve linux related products
    --windows                               retrieve windows related products
    --windows-server                        retrieve windows server related products
    --categories                            retrieve product categories
    --apps                                  retrieve app category products
    --oses                                  retrieve os category products
    --tags                                  retrieve all available tags or a specific one
    --category-name=CTGNAME                 specify a category name
    --full                                  if specified, retrieve full product data
    --product-name=PRODUCTNAME              specify a product name
    --releases-name=RELNAME                 specify a release name (its version)
    --tag=TAG                               specify one or several tag (repeatable)
"""
    _opt: "CmdHub" = CmdHub()
    _opt.options = {
        "--category-name": CmdOpt(
            "Specify a category name",
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

    _opt.usages = {
        "--products": CmdUsage(
            "Retrieve all or a specific product from EOL",
            {
                "product": CmdUsageOpt("--product-name"),
                "tags": CmdUsageOpt("--tag"),
                "full": CmdUsageOpt("--full"),
            },
        ),
        "--product-releases": CmdUsage(
            "Retrieve a product release from EOL",
            {
                "product": CmdUsageOpt("--product-name"),
                "release": CmdUsageOpt("--release-name"),
            },
        ),
        "--linux": CmdUsage(
            "Retrieve linux related products",
            {
                "full": CmdUsageOpt("--full"),
            },
        ),
        "--windows": CmdUsage(
            "Retrieve windows related products",
            {},
        ),
        "--windows-server": CmdUsage(
            "Retrieve windows server related products",
            {},
        ),
        "--categories": CmdUsage(
            "Retrieve product categories",
            {
                "category": CmdUsageOpt("--category-name"),
            },
        ),
        "--apps": CmdUsage(
            "Retrieve app category products",
            {},
        ),
        "--oses": CmdUsage(
            "Retrieve os category products",
            {},
        ),
        "--tags": CmdUsage(
            "Retrieve all available tags",
            {
                "tag": CmdUsageOpt("--tag", lambda lst: next(iter(lst))),
            },
        ),
    }

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

        self._opt.options["--full"].transform = lambda opt, _: self._is_opt_present(opt)

        self._opt.usages["--products"].backend = self.connector.products
        self._opt.usages["--product-releases"].backend = self.connector.product_releases
        self._opt.usages["--linux"].backend = self.connector.linux
        self._opt.usages["--windows"].backend = self.connector.windows
        self._opt.usages["--windows-server"].backend = self.connector.windows_server
        self._opt.usages["--categories"].backend = self.connector.categories
        self._opt.usages["--apps"].backend = self.connector.apps
        self._opt.usages["--oses"].backend = self.connector.oses
        self._opt.usages["--tags"].backend = self.connector.tags

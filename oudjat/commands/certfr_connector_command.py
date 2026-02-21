"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

from oudjat.connectors.cert.certfr import CERTFRConnector
from oudjat.utils.doc_builder import DocBuilder

from .base import (
    CmdOpt,
    CmdProps,
    CmdUsage,
    CmdUsageOpt,
)
from .connector_command import ConnectorCommand


class CERTFRConnectorCommand(ConnectorCommand):
    """
    A class to provide an access to the S1Connector.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps(
        "connectors.cert.certfr",
        "A command to parse CERTFR pages through oudjat CERTFRConnector",
    )
    __cmd_props__.options = {
        "--feed-filter": CmdOpt(
            "A filter to retrieve only RSS feed items that were published after a certain date (YYYY-MM-DD format)",
            arg="FEEDFILTER",
        ),
        "--keywords": CmdOpt(
            "A list of keywords (comma separated, no space)",
            arg="KEYWORDS",
        ),
        "--keywords-file": CmdOpt(
            "A list of keywords (as a file)",
            arg="KEYWORDSFILE",
        ),
    }

    __cmd_props__.usages = {
        "--target": CmdUsage(
            CmdOpt(
                "Specify CERTFR page references for parsing (comma separated, no space)",
            ),
            "(-t=TARGET | --target=TARGET) [--keywords=KEYWORDS | --keywords-file=KEYWORDSFILE] [options]",
            {
                "search_filter": CmdUsageOpt("--target"),
                "keywords": CmdUsageOpt("--keywords"),
            },
        ),
        "--target-file": CmdUsage(
            CmdOpt(
                "Specify CERTFR page references for parsing (comma separated, no space)",
            ),
            "--target-file=TARGETFILE [--keywords=KEYWORDS | --keywords-file=KEYWORDSFILE] [options]",
            {
                "search_filter": CmdUsageOpt("--target-file"),
                "keywords": CmdUsageOpt("--keywords"),
            },
        ),
        "--feed": CmdUsage(
            CmdOpt(
                "Automatically retrieve and parse CERTFR pages from RSS feed",
            ),
            "--feed [--feed-filter] [--keywords=KEYWORDS | --keywords-file=KEYWORDSFILE] [options]",
            {
                "date_filter": CmdUsageOpt("--feed-filter"),
                "keywords": CmdUsageOpt("--keywords"),
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

        self.connector: "CERTFRConnector" = CERTFRConnector()

        if self._is_opt_present("--creds-service"):
            self.connector.set_creds_from_svc_name(self.options["--creds-service"])

        self.connector.connect()

        # Options transform based on instance
        self.__cmd_props__.opts_transform(
            {
                "--target": lambda opt, _: self._unify_str_opt(opt, "--target-file"),
                "--target-file": lambda opt, _: self._unify_str_opt("--target", opt),
                "--keywords": lambda opt, _: self._unify_str_opt(opt, "--keywords-file"),
                "--keywords-file": lambda opt, _: self._unify_str_opt("--keywords", opt),
            }
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--target": self.connector.fetch,
                "--target-file": self.connector.fetch,
                "--feed": self.connector.feed,
            }
        )

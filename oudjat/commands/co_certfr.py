"""
A command module to handle interactions with the CERTFR website.
"""

from typing import Any, override

from oudjat.connectors.cert.certfr import CERTFRConnector
from oudjat.connectors.vuln.cve_load_balancer import CVELoadBalancer
from oudjat.control.vulnerability.cve import CVE
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
    A class to provide an access to the CERTFRConnector.
    """

    # ****************************************************************
    # Constructor & Attributes

    __cmd_props__: "CmdProps" = CmdProps(
        "connectors.cert.certfr",
        "A command to parse CERTFR pages through oudjat CERTFRConnector",
    )
    __cmd_props__.options = {
        "--feed-date": CmdOpt(
            "A filter to retrieve only RSS feed items that were published after a certain date (YYYY-MM-DD format)",
            arg="FEEDDATE",
        ),
        "--keywords": CmdOpt(
            "A list of keywords (comma separated, no space)",
            arg="KEYWORDS",
        ),
        "--limit": CmdOpt(
            "Define a limit to the number of CVEs resolve when using max-cve option",
            arg="LIMIT",
            default=50,
        ),
        "--max-cve": CmdOpt(
            "Resolve CVEs data and the highests (most critical) ones",
        ),
        "--target": CmdOpt("Specify one or multiple CERTFR page refs", short="t", arg="TARGET"),
    }

    __cmd_props__.usages = {
        "--target": CmdUsage(
            "Specify CERTFR page references for parsing (comma separated, no space)",
            (
                "(-t=TARGET | --target=TARGET)",
                "[--keywords=KEYWORDS] [--max-cve [--limit=LIMIT]] [options]",
            ),
            {
                "search_filter": CmdUsageOpt("--target"),
                "keywords": CmdUsageOpt("--keywords"),
            },
        ),
        "--feed": CmdUsage(
            "Automatically retrieve and parse CERTFR pages from RSS feed",
            (
                "--feed",
                "[--feed-date=FEEDDATE] [--keywords=KEYWORDS] [--max-cve [--limit=LIMIT]] [options]",
            ),
            {
                "date_filter_str": CmdUsageOpt("--feed-date"),
                "keywords": CmdUsageOpt("--keywords"),
            },
        ),
    }

    __doc_builder__: "DocBuilder" = ConnectorCommand._gen_doc("oudjat", __cmd_props__, "")

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new CERTFRConnectorCommand.

        Args:
            options (dict[str, Any]): Provided options
        """

        super().__init__(options, False)

        self.connector: "CERTFRConnector" = CERTFRConnector()
        self.connector.connect()

        # Options transform based on instance
        self.__cmd_props__.opts_transform(
            {
                "--target": lambda opt, _: self._unify_str_opt(opt),
                "--keywords": lambda opt, _: self._unify_str_opt(opt),
            }
        )

        # Usage backends
        self.__cmd_props__.backends(
            {
                "--target": self.connector.fetch,
                "--feed": self.connector.feed,
            }
        )

        if self.options["--max-cve"]:
            self._callbacks.append(self._max_cve_cb)

        self.options["--limit"] = int(self.options["--limit"])

    # ****************************************************************
    # Methods - callbacks

    @override
    def print(self) -> None:
        for p in self._data:
            print(f"{p['ref']} - {p['title']}")

            if self.options["--keywords"]:
                print(f"    Matched {len(p['matches'])} keywords")

                for k in p["matches"]:
                    print(f"        {k}")

            if self.options["--max-cve"]:
                print("    Highest CVEs")

                for cve in p["highestCVEs"]:
                    print(f"        {cve['id']}: {cve['score']}")

    # ****************************************************************
    # Methods - callbacks

    def _max_cve_cb(self) -> None:
        balancer = CVELoadBalancer()

        cves = {}

        def _cve_not_resolved(cve: str) -> bool:
            return cve not in cves

        for page in self._data:
            initial_page_cves = page["cves"]
            page_cves = balancer.fetch(list(filter(_cve_not_resolved, initial_page_cves)))

            cves.update({cve.ref: cve for cve in CVE.from_db(page_cves)})

            max_cves = CVE.max_cve([cves[cve] for cve in initial_page_cves])
            page["highestCVEs"] = [{"id": cve.ref, "score": cve.cvss_score} for cve in max_cves]

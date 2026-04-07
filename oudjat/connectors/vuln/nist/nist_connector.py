"""A module that handles the connection to Nist and Nist API."""

import re
from decimal import Context
from time import sleep, time
from typing import Any, override
from urllib.parse import ParseResult, urlparse

from yaspin import yaspin

from oudjat.utils import DataType
from oudjat.utils.logging import spinner_log
from oudjat.utils.types import StrType

from ..cve_connector import CVEConnector
from ..cve_formats import CVEDataFormat


class NistConnector(CVEConnector):
    """A class that handles connection with Nist API to retrieve CVE informations."""

    # ****************************************************************
    # Attributes & Constructors

    URL: "ParseResult" = urlparse("https://nvd.nist.gov/")
    API_URL: "ParseResult" = urlparse("https://services.nvd.nist.gov/rest/json/cves/2.0")

    # ****************************************************************
    # Methods

    @override
    def vuln_from_connection(self) -> dict[str, Any] | None:
        """
        Extract base vulnerability from the connection object.

        Returns:
            dict[str, Any]: The base vulnerability dictionary
        """

        if self._connection is None:
            return None

        vuln = self._connection.get("vulnerabilities", [])

        if len(vuln) > 0:
            vuln = next(iter(vuln)).get("cve", {})

        return vuln

    @override
    def fetch(
        self,
        cves: StrType,
        raw: bool = False,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the NIST API based on the provided CVE IDs.
        If `search_filter` is not a list, it converts it to one.
        Similarly, if `attributes` is provided but not a list, it converts it to a list.

        It iterates over each CVE ID in `search_filter`, constructs the API endpoint URL for that CVE, and connects to retrieve data.

        Args:
            cves (str | list[str])             : A single CVE ID or a list of CVE IDs to be searched.
            raw (bool)                         : Weither to return the raw result or the unified one
            payload (dict[str, Any] | None)    : Payload to send to the target CVE API url

        Returns:
            DataType: A list of dictionaries containing filtered vulnerability information for each provided CVE ID.
        """

        context = Context()

        if not isinstance(cves, list):
            cves = [cves]

        if payload is None:
            payload = {}

        self.logger.info(f"Fetching data for {len(cves)} CVEs from {self.URL}")

        res = []
        spinner_txt = f"Fetching CVE data from {self.URL.netloc}"
        with yaspin(text=f"{spinner_txt}...") as spinner:
            for i, cve in enumerate(cves):
                spinner.text = f"{spinner_txt} ({i+1}/{len(cves)})..."

                if not re.match(r"CVE-\d{4}-\d{4,7}", cve):
                    continue

                while True:
                    if not self.token():
                        wait_time = max(
                            self.rate - ((time() - self.last_token_time) * self.rate), 0.1
                        )

                        spinner_log(
                            f"API not available, waiting {wait_time}...",
                            self.logger.warning,
                            spinner,
                        )

                        sleep(wait_time)
                        continue

                    cve_url = NistConnector.cve_api_url(cve)

                    spinner_log(f"{context}::{cve_url} > {payload}", self.logger.debug, spinner)
                    self.connect(cve_url, **payload)

                    vuln = self.vuln_from_connection()

                    if vuln:
                        spinner_log(f"{context}::{cve_url} > {vuln}", self.logger.debug, spinner)
                        res.append(self.unify_cve_data(vuln) if not raw else vuln)

                    else:
                        spinner_log(
                            f"No data for vulnerability {cve}", self.logger.warning, spinner
                        )

                    break

            if len(res) > 0:
                spinner.text = f"Retrieved data for {len(res)} CVEs"
                spinner.ok("✅ ")

            else:
                spinner.fail("❌ ")

        return res

    @override
    def unify_cve_data(self, cve: dict[str, Any]) -> "CVEDataFormat":
        """
        Filter and reorganize cve data properties in order to obtain a unified format accross CVE connectors.

        Args:
            cve (dict[str, Any]): cve data as a dictionary

        Returns:
            CVEDataFormat: unified formated CVE dictionary
        """

        cve_id: str | None = cve.get("id")

        published_date: str | None = cve.get("published")

        if cve_id is None or published_date is None:
            raise ValueError(
                f"{Context()}::Invalid CVE provided {cve} missing mandatory informations"
            )

        updated_date: str = cve.get("lastModified", published_date)

        metrics = cve.get("metrics", {})
        metric_data = {}
        if len(metrics.keys()) > 0:
            valid_keys = self._cvss_metrics_keys(list(metrics.keys()))

            if len(valid_keys) > 0:
                metric_data = metrics.get(valid_keys[0], [])[0]

        cvss_data = metric_data.get("cvssData", {})

        unified_fmt: "CVEDataFormat" = {
            "id": cve_id,
            "status": cve.get("vulnStatus", ""),
            "dates": {
                "published": CVEConnector.format_date_str(published_date),
                "updated": CVEConnector.format_date_str(updated_date),
            },
            "description": cve.get("descriptions", [])[0].get("value", ""),
            "sources": [r["url"] for r in cve.get("references", [])],
            "vectors": {
                "vectorStr": cvss_data.get("vectorString", ""),
                "attackVector": cvss_data.get("attackVector", ""),
            },
            "metrics": {
                "score": cvss_data.get("baseScore", 0),
                "version": float(cvss_data.get("version", -1.0)),
                "severity": cvss_data.get("baseSeverity", "INFO"),
            },
            "requirements": {
                "privilegesRequired": cvss_data.get("privilegesRequired", "NONE"),
                "attackRequirements": cvss_data.get("attackRequirements", "NONE"),
            },
        }

        return unified_fmt

    # ****************************************************************
    # Static methods

    @staticmethod
    @override
    def cve_url(cve: str) -> str:
        """
        Return the Nist website URL of the given CVE.

        Args:
            cve (str): the ref string of the CVE

        Returns:
            str: Nist vuln detail URL based on the provided CVE
        """

        return f"{NistConnector.URL.geturl()}vuln/detail/{cve}"

    @staticmethod
    @override
    def cve_api_url(cve: str) -> str:
        """
        Return the Nist website URL of the given CVE.

        Args:
            cve (str): the ref string of the CVE

        Returns:
            str: Nist vuln detail URL based on the provided CVE
        """

        return f"{NistConnector.API_URL.geturl()}?cveId={cve}"

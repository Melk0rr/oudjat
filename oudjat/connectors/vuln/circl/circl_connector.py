"""A module that handles the connection to circl.lu API."""

import re
from typing import Any, override
from urllib.parse import ParseResult, urlparse

from oudjat.utils.context import Context
from oudjat.utils.types import DataType, StrType

from ..cve_connector import CVEConnector
from ..cve_formats import CVEDataFormat


class CirclConnector(CVEConnector):
    """A class that handles connection with CVE.org API to retrieve CVE informations."""

    # ****************************************************************
    # Attributes & Constructors

    URL: "ParseResult" = urlparse("https://www.circl.lu")
    API_URL: "ParseResult" = urlparse("https://cve.circl.lu/api/cve/")

    # ****************************************************************
    # Methods

    @override
    def fetch(
        self,
        cves: "StrType",
        attributes: "StrType | None" = None,
        raw: bool = False,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the circl.lu API based on the provided CVE refs.
        If `search_filter` is not a list, it converts it to one. Similarly, if `attributes` is provided but not a list, it converts it to a list.
        It iterates over each CVE ID in `search_filter`, constructs the API endpoint URL for that CVE, and connects to retrieve data.
        If a valid response is received, it extracts vulnerability information and filters it based on the specified attributes before appending it to the result list.

        Args:
            cves (str | list[str])             : A single CVE ID or a list of CVE IDs to be searched.
            attributes (str | list[str] | None): A single attribute name or a list of attribute names to filter the retrieved vulnerability data by. Defaults to None.
            raw (bool)                         : Weither to return the raw result or the unified one
            payload (dict[str, Any] | None)    : Payload to send to the target CVE API url

        Returns:
            DataType: A list of dictionaries containing filtered vulnerability information for each provided CVE ID.
        """

        context = Context()
        if not isinstance(cves, list):
            cves = [cves]

        if attributes is not None and not isinstance(attributes, list):
            attributes = [attributes]

        if payload is None:
            payload = {}

        res = []
        for cve in cves:
            if not re.match(r"CVE-\d{4}-\d{4,7}", cve):
                continue

            cve_target = CirclConnector.cve_api_url(cve)

            self.logger.debug(f"{context}::{cve_target} > {payload}")
            self.connect(cve_target, **payload)

            vuln = self._connection
            if vuln is not None:
                self.logger.debug(f"{context}::{cve_target} > {vuln}")
                res.append(self.unify_cve_data(vuln) if not raw else vuln)

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

        cve_metadata: dict[str, Any] = cve.get("cveMetadata", {})
        cve_id: str | None = cve_metadata.get("cveId")
        published_date: str | None = cve_metadata.get("datePublished")

        if cve_id is None or published_date is None:
            raise ValueError(
                f"{Context()}::Invalid CVE provided {cve} missing mandatory informations"
            )

        containers = cve.get("containers", {}).get("cna", {})
        metrics: "DataType" = containers.get("metrics", [])
        metrics_data: dict[str, Any] = {}
        if len(metrics) > 0:
            valid_keys = self._cvss_metrics_keys(list(metrics[0].keys()))

            if len(valid_keys) > 0:
                metrics_data = metrics[0].get(valid_keys[0], {})

        raw_description = containers.get("descriptions", [])

        unified_fmt: "CVEDataFormat" = {
            "id": cve_id,
            "status": cve_metadata.get("state", ""),
            "dates": {
                "published": CVEConnector.format_date_str(published_date),
                "updated": CVEConnector.format_date_str(
                    cve_metadata.get("dateUpdated", published_date)
                ),
            },
            "description": raw_description[0].get("value", "") if len(raw_description) > 0 else "",
            "sources": [r["url"] for r in containers.get("references", [])],
            "vectors": {
                "vectorStr": metrics_data.get("vectorString", ""),
                "attackVector": metrics_data.get("attackVector", ""),
            },
            "metrics": {
                "score": metrics_data.get("baseScore", 0),
                "version": float(metrics_data.get("version", 4.0)),
                "severity": metrics_data.get("baseSeverity", "INFO"),
            },
            "requirements": {
                "privilegesRequired": metrics_data.get("privilegesRequired", "NONE"),
                "attackRequirements": metrics_data.get("attackRequirements", "NONE"),
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

        return f"{CirclConnector.URL.geturl()}"

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

        return f"{CirclConnector.API_URL.geturl()}{cve}"


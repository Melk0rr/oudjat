"""A module that handles the connection to Nist and Nist API."""

import re
from typing import Any, override

from oudjat.utils import DataType
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.types import StrType

from ..cve_connector import CVEConnector
from ..cve_formats import CVEDataFormat


class NistConnector(CVEConnector):
    """A class that handles connection with Nist API to retrieve CVE informations."""

    # ****************************************************************
    # Attributes & Constructors

    URL: str = "https://nvd.nist.gov/"
    API_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    # ****************************************************************
    # Methods

    @override
    def fetch(
        self,
        cves: StrType,
        attributes: "StrType | None" = None,
        raw: bool = False,
        payload: dict[str, Any] | None = None
    ) -> "DataType":
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the NIST API based on the provided CVE IDs.
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

        if not isinstance(cves, list):
            cves = [cves]

        if attributes is not None and not isinstance(attributes, list):
            attributes = [attributes]

        if payload is None:
            payload = {}

        # Vuln filter function
        def key_in_attr(item: tuple) -> bool:
            return item[0] in attributes

        res = []
        for cve in cves:
            if not re.match(r"CVE-\d{4}-\d{4,7}", cve):
                continue

            cve_target = NistConnector.cve_api_url(cve)
            self.connect(cve_target, **payload)

            if self._connection:
                vuln = self._connection.get("vulnerabilities", [])

                if len(vuln) > 0:
                    vuln = vuln[0].get("cve", {})

                else:
                    ColorPrint.yellow(f"No data for vulnerability {cve}")
                    continue

                if not raw:
                    vuln = self.unify_cve_data(vuln)

                if attributes is not None:
                    vuln = dict(filter(key_in_attr, vuln.items()))

                res.append(vuln)

        return res

    @override
    def unify_cve_data(self, cve: dict[str, Any]) -> CVEDataFormat:
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
            raise ValueError(f"{__class__.__name__}.unify_cve_data::Invalid CVE provided {cve} missing mandatory informations")

        updated_date: str = cve.get("lastModified", published_date)

        metrics = cve.get("metrics", {})
        metric_data = metrics.get(list(metrics.keys())[0], [])[0]
        cvss_data = metric_data.get("cvssData", {})

        unified_fmt: CVEDataFormat = {
            "id": cve_id,
            "status": cve.get("vulnStatus", ""),
            "dates": {
                "published": published_date,
                "updated": updated_date,
            },
            "description": cve.get("descriptions", [])[0].get("value", ""),
            "sources": [r["url"] for r in cve.get("references", [])],
            "vectors": {
                "vector_str": cvss_data.get("vectorString", ""),
                "attack_vector": cvss_data.get("attackVector", ""),
            },
            "metrics": {
                "score": cvss_data.get("baseScore", 0),
                "version": float(cvss_data.get("version", 4.0)),
                "severity": cvss_data.get("baseSeverity", "INFO")
            },
            "requirements": {
                "privileges_required": cvss_data.get("privilegesRequired", "NONE"),
                "attack_requirements": cvss_data.get("attackRequirements", "NONE"),
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

        return f"{NistConnector.URL}vuln/detail/{cve}"

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

        return f"{NistConnector.API_URL}?cveId={cve}"

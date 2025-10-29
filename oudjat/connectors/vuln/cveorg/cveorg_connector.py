"""A module that handles the connection to CVE.org and CVE.org API."""

import re
from typing import Any, override

from oudjat.utils import DataType
from oudjat.utils.types import DatumType, StrType

from ..cve_connector import CVEConnector
from ..cve_formats import CVEDataFormat


class CVEorgConnector(CVEConnector):
    """A class that handles connection with CVE.org API to retrieve CVE informations."""

    # ****************************************************************
    # Attributes & Constructors

    URL: str = "https://www.cve.org/"
    API_URL: str = "https://cveawg.mitre.org/api/cve/"

    # ****************************************************************
    # Methods

    @override
    def fetch(
        self,
        search_filter: StrType,
        attributes: StrType | None = None,
        raw: bool = False,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the CVE.org API based on the provided CVE refs.
        If `search_filter` is not a list, it converts it to one. Similarly, if `attributes` is provided but not a list, it converts it to a list.
        It iterates over each CVE ID in `search_filter`, constructs the API endpoint URL for that CVE, and connects to retrieve data.
        If a valid response is received, it extracts vulnerability information and filters it based on the specified attributes before appending it to the result list.

        Args:
            search_filter (str | list[str])       : A single CVE ID or a list of CVE IDs to be searched.
            attributes (str | list[str], optional): A single attribute name or a list of attribute names to filter the retrieved vulnerability data by. Defaults to None.
            raw (bool)                            : Weither to return the raw result or the unified one
            kwargs (Any)                          : Additional arguments that will be passed to connect method

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing filtered vulnerability information for each provided CVE ID.
        """

        res = []

        if not isinstance(search_filter, list):
            search_filter = [search_filter]

        if attributes is not None and not isinstance(attributes, list):
            attributes = [attributes]

        for cve in search_filter:
            if not re.match(r"CVE-\d{4}-\d{4,7}", cve):
                continue

            cve_target = CVEorgConnector.get_cve_api_url(cve)
            self.connect(cve_target, **kwargs)

            vuln = self._connection
            if vuln is not None:
                res.append(self.unify_cve_data(vuln) if not raw else vuln)

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

        cve_metadata: dict[str, Any] = cve.get("cveMetadata", {})
        cve_id: str | None = cve_metadata.get("cveId")
        published_date: str | None = cve_metadata.get("datePublished")

        if cve_id is None or published_date is None:
            raise ValueError(
                f"{__class__.__name__}.unify_cve_data::Invalid CVE provided {cve} missing mandatory informations"
            )

        containers = cve.get("containers", {}).get("cna", {})
        metrics: DataType = containers.get("metrics", [])
        metric_data: DatumType = metrics[0].get(list(metrics[0].keys())[0], {})

        raw_description = containers.get("descriptions", [])

        unified_fmt: CVEDataFormat = {
            "id": cve_id,
            "status": cve_metadata.get("state", ""),
            "dates": {
                "published": published_date,
                "updated": cve_metadata.get("dateUpdated", published_date),
            },
            "description": raw_description[0].get("value", "") if len(raw_description) > 0 else "",
            "sources": [r["url"] for r in containers.get("references", [])],
            "vectors": {
                "vector_str": metric_data.get("vectorString", ""),
                "attack_vector": metric_data.get("attackVector", ""),
            },
            "metrics": {
                "score": metric_data.get("baseScore", 0),
                "version": float(metric_data.get("version", 4.0)),
                "severity": metric_data.get("baseSeverity", "INFO"),
            },
            "requirements": {
                "privileges_required": metric_data.get("privilegesRequired", "NONE"),
                "attack_requirements": metric_data.get("attackRequirements", "NONE"),
            },
        }

        return unified_fmt

    # ****************************************************************
    # Static methods

    @staticmethod
    @override
    def get_cve_url(cve: str) -> str:
        """
        Return the Nist website URL of the given CVE.

        Args:
            cve (str): the ref string of the CVE

        Returns:
            str: Nist vuln detail URL based on the provided CVE
        """

        return f"{CVEorgConnector.URL}CVERecord?id={cve}"

    @staticmethod
    @override
    def get_cve_api_url(cve: str) -> str:
        """
        Return the Nist website URL of the given CVE.

        Args:
            cve (str): the ref string of the CVE

        Returns:
            str: Nist vuln detail URL based on the provided CVE
        """

        return f"{CVEorgConnector.API_URL}{cve}"

"""A module that handles the connection to CVE.org and CVE.org API."""

import re
from typing import Dict, List, Union

from ..cve_connector import CVEConnector


class CVEorgConnector(CVEConnector):
    """A class that handles connection with CVE.org API to retrieve CVE informations."""

    # ****************************************************************
    # Attributes & Constructors

    URL = "https://www.cve.org/"
    API_URL = "https://cveawg.mitre.org/api/cve/"

    # ****************************************************************
    # Methods

    def search(
        self,
        search_filter: Union[str, List[str]],
        attributes: Union[str, List[str]] = None,
        raw: bool = False,
        **kwargs,
    ) -> List[Dict]:
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the CVE.org API based on the provided CVE refs.
        If `search_filter` is not a list, it converts it to one. Similarly, if `attributes` is provided but not a list, it converts it to a list.
        It iterates over each CVE ID in `search_filter`, constructs the API endpoint URL for that CVE, and connects to retrieve data.
        If a valid response is received, it extracts vulnerability information and filters it based on the specified attributes before appending it to the result list.

        Args:
            search_filter (Union[str, List[str]])       : A single CVE ID or a list of CVE IDs to be searched.
            attributes (Union[str, List[str]], optional): A single attribute name or a list of attribute names to filter the retrieved vulnerability data by. Defaults to None.
            raw (bool)                                  : Weither to return the raw result or the unified one
            kwargs (Dict)                               : Additional arguments that will be passed to connect method

        Returns:
            List[Dict]: A list of dictionaries containing filtered vulnerability information for each provided CVE ID.
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

            vuln = self.connection
            if vuln is not None:
                res.append(self.unify_cve_data(vuln) if not raw else vuln)

        return res

    def unify_cve_data(self, cve: Dict) -> Dict:
        """
        Filter and reorganize cve data properties in order to obtain a unified format accross CVE connectors.

        Args:
            cve (Dict): cve data as a dictionary

        Returns:
            Dict: formated dictionary
        """

        base_format = self.UNIFIED_FORMAT

        try:
            base_format["id"] = cve["cveMetadata"].get("cveId")
            base_format["status"] = cve["cveMetadata"].get("state", None)

            base_format["dates"]["published"] = cve["cveMetadata"].get("datePublished", None)
            base_format["dates"]["updated"] = cve["cveMetadata"].get("dateUpdated", None)

            containers = cve.get("containers", {}).get("cna", {})
            base_format["source"] = [r["url"] for r in containers.get("references", [])]

            metrics: List = containers.get("metrics", [])

            if len(metrics) > 0:
                base_format["description"] = containers.get("descriptions", [])[0].get(
                    "value", None
                )
                metric_data = metrics[0].get(list(metrics[0].keys())[0], {})

                base_format["metrics"]["score"] = metric_data.get("baseScore", 0)
                base_format["metrics"]["version"] = float(metric_data.get("version", 4.0))
                base_format["metrics"]["severity"] = metric_data.get("baseSeverity", "INFO")

                base_format["vectors"]["vectorString"] = metric_data.get("vectorString", "")
                base_format["vectors"]["attackVector"] = metric_data.get("attackVector", None)

                base_format["requirements"]["privilegesRequired"] = metric_data.get(
                    "privilegesRequired", None
                )
                base_format["requirements"]["attackRequirements"] = metric_data.get(
                    "attackRequirements", "NONE"
                )

        except ValueError as e:
            raise ValueError(
                f"{__class__.__name__}.unify_cve_data::An error occured while unifying cve data...\n{e}"
            )

        return base_format

    # ****************************************************************
    # Static methods

    @staticmethod
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
    def get_cve_api_url(cve: str) -> str:
        """
        Return the Nist website URL of the given CVE.

        Args:
            cve (str): the ref string of the CVE

        Returns:
            str: Nist vuln detail URL based on the provided CVE
        """

        return f"{CVEorgConnector.API_URL}{cve}"

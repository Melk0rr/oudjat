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
        self, search_filter: Union[str, List[str]], attributes: Union[str, List[str]] = None
    ) -> List[Dict]:
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the CVE.org API based on the provided CVE refs.
        If `search_filter` is not a list, it converts it to one. Similarly, if `attributes` is provided but not a list, it converts it to a list.
        It iterates over each CVE ID in `search_filter`, constructs the API endpoint URL for that CVE, and connects to retrieve data.
        If a valid response is received, it extracts vulnerability information and filters it based on the specified attributes before appending it to the result list.

        Args:
            search_filter (Union[str, List[str]]): A single CVE ID or a list of CVE IDs to be searched.
            attributes (Union[str, List[str]], optional): A single attribute name or a list of attribute names to filter the retrieved vulnerability data by. Defaults to None.

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
            self.connect(cve_target)

            if self.connection is not None:
                res.append(self.connection)

        return res

    def unify_cve_data(self, cve: Dict) -> Dict:
        """
        Filter and reorganize cve data properties in order to obtain a unified format accross CVE connectors.

        Args:
            cve (Dict): cve data as a dictionary

        Returns:
            Dict: formated dictionary
        """

        return {}

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

"""A module that handles the connection to Nist API."""
import json
import re
from typing import Dict, List, Union

import requests

from oudjat.utils.color_print import ColorPrint

from ..connector import Connector

NIST_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class NistConnector(Connector):
    """NIST API Connector class."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self):
        """
        Create a new instance of NistConnector.

        Initializes a new instance of the `NistConnector` class, inheriting from `Connector`.
        It sets the target URL to the NIST API URL.
        """

        super().__init__(target=NIST_API_URL)

    # ****************************************************************
    # Methods

    def connect(self, target: str) -> None:
        """
        Test connection to NIST API.

        Sends a GET request to the specified target URL with an Accept header set to application/json.
        If the response status code is 200, it parses the JSON content and stores it in `self.connection`. Raises a ConnectionError if the connection cannot be established.

        Args:
            target (str): The URL to which the GET request will be sent.
        """

        self.connection = None

        try:
            headers = {"Accept": "application/json"}
            req = requests.get(target, headers=headers)

            if req.status_code == 200:
                self.connection = json.loads(req.content.decode("utf-8"))

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.connect::Could not connect to {self.target}\n{e}"
            )

    def search(
        self, search_filter: Union[str, List[str]], attributes: Union[str, List[str]] = None
    ) -> List[Dict]:
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the NIST API based on the provided CVE IDs.
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

            cve_target = f"{self.target}?cveId={cve}"
            self.connect(cve_target)

            if self.connection is not None:
                vuln = self.connection.get("vulnerabilities", [])

                if len(vuln) > 0:
                    vuln = vuln[0].get("cve", {})

                else:
                    ColorPrint.yellow(f"No data for vulnerability {cve}")
                    continue

                if attributes is not None:
                    vuln = {k: v for k, v in vuln.items() if k in attributes}

                res.append(vuln)

        return res

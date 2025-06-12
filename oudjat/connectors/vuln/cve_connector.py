"""A module that describes common CVE connector behaviors."""

import json
from datetime import datetime
from typing import Dict, List, Union

import requests

from oudjat.connectors.connector import Connector


class CVEConnector(Connector):
    """A class that handles connection with Nist API to retrieve CVE informations."""

    # ****************************************************************
    # Attributes & Constructors

    URL = None
    API_URL = None

    UNIFIED_FORMAT = {
        "id": str,
        "published": Union[str, datetime],
        "updated": Union[str, datetime],
        "source": str,
        "status": str,
        "description": str,
        "metrics": {
            "score": float,
            "version": float,
            "vectorString": str,
            "attackVector": str,
            "privilegesRequired": str,
            "attackRequirements": str,
            "severity": str,
        }
    }

    def __init__(self):
        """
        Create a new instance of NistConnector.

        Initializes a new instance of the `NistConnector` class, inheriting from `Connector`.
        It sets the target URL to the NIST API URL.
        """

        super().__init__(target=CVEConnector.API_URL)

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

        raise NotImplementedError(
            f"{__class__.__name__}.search::Method must be implemented by the overloading class"
        )

    def unify_cve_data(self, cve: Dict) -> Dict:
        """
        Filter and reorganize cve data properties in order to obtain a unified format accross CVE connectors.

        Args:
            cve (Dict): cve data as a dictionary

        Returns:
            Dict: formated dictionary
        """

        raise NotImplementedError(
            f"{__class__.__name__}.unify_cve_data::Method must be implemented by the overloading class"
        )

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

        raise NotImplementedError(
            f"{__class__.__name__}.get_cve_url::Method must be implemented by the overloading class"
        )

    @staticmethod
    def get_cve_api_url(cve: str) -> str:
        """
        Return the Nist website URL of the given CVE.

        Args:
            cve (str): the ref string of the CVE

        Returns:
            str: Nist vuln detail URL based on the provided CVE
        """

        raise NotImplementedError(
            f"{__class__.__name__}.get_cve_api_url::Method must be implemented by the overloading class"
        )

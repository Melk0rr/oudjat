"""A module that describes common CVE connector behaviors."""

import json
from abc import ABC, abstractmethod
from typing import Any, override

import requests

from oudjat.connectors.connector import Connector

from .cve_formats import CVEDataFormat


class CVEConnector(Connector, ABC):
    """A class that handles connection with Nist API to retrieve CVE informations."""

    # ****************************************************************
    # Attributes & Constructors

    URL: str = ""
    API_URL: str = ""

    def __init__(self) -> None:
        """
        Create a new instance of NistConnector.

        Initializes a new instance of the `NistConnector` class, inheriting from `Connector`.
        It sets the target URL to the NIST API URL.
        """

        super().__init__(target=CVEConnector.API_URL)

        self._connection: dict[str, Any] | None = None

    # ****************************************************************
    # Methods

    @override
    def connect(self, target: str, **kwargs: Any) -> None:
        """
        Test connection to NIST API.

        Sends a GET request to the specified target URL with an Accept header set to application/json.
        If the response status code is 200, it parses the JSON content and stores it in `self.connection`. Raises a ConnectionError if the connection cannot be established.

        Args:
            target (str) : The URL to which the GET request will be sent.
            kwargs (Dict): Additional arguments to pass into requests.get
        """

        self._connection = None

        try:
            headers = {"Accept": "application/json"}
            req = requests.get(target, headers=headers, **kwargs)

            if req.status_code == 200:
                self._connection = json.loads(req.content.decode("utf-8"))

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.connect::Could not connect to {self.target}\n{e}"
            )

    @override
    @abstractmethod
    def search(
        self,
        search_filter: str | list[str],
        attributes: str | list[str] | None = None,
        raw: bool = False,
        **kwargs: Any,
    ) -> list[dict]:
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

        raise NotImplementedError(
            f"{__class__.__name__}.search::Method must be implemented by the overloading class"
        )

    @abstractmethod
    def unify_cve_data(self, cve: dict[str, Any]) -> CVEDataFormat:
        """
        Filter and reorganize cve data properties in order to obtain a unified format accross CVE connectors.

        Args:
            cve (dict[str, Any]): cve data as a dictionary

        Returns:
            Dict: formated dictionary
        """

        raise NotImplementedError(
            f"{__class__.__name__}.unify_cve_data::Method must be implemented by the overloading class"
        )

    # ****************************************************************
    # Static methods

    @staticmethod
    @abstractmethod
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
    @abstractmethod
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

    @staticmethod
    def format_date_str(date_str: str) -> str:
        """
        Format a date string like YYYY-mm-dd HH:MM:SS.

        Args:
            date_str (str): Date string to format

        Returns:
            str: date string formated
        """

        return date_str[:-5].replace("T", " ")

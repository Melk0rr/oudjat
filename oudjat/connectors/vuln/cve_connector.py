"""A module that describes common CVE connector behaviors."""

import json
from abc import ABC, abstractmethod
from typing import Any, override
from urllib.parse import ParseResult

from oudjat.connectors import Connector, ConnectorMethod
from oudjat.utils import DataType
from oudjat.utils.types import StrType

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

        self._target: ParseResult
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
            target (str): The URL to which the GET request will be sent.
            kwargs (Any): Additional named arguments to pass into requests.get
        """

        self._connection = None

        try:
            headers = {"Accept": "application/json"}
            req = ConnectorMethod.GET(target, headers=headers, **kwargs)

            if req.status_code == 200:
                self._connection = json.loads(req.content.decode("utf-8"))

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.connect::Could not connect to {self.target}\n{e}"
            )

    @override
    @abstractmethod
    def fetch(
        self,
        cves: StrType,
        attributes: StrType | None = None,
        raw: bool = False,
        payload: dict[str, Any] | None = None
    ) -> "DataType":
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the CVE.org API based on the provided CVE refs.
        If `search_filter` is not a list, it converts it to one. Similarly, if `attributes` is provided but not a list, it converts it to a list.
        It iterates over each CVE ID in `search_filter`, constructs the API endpoint URL for that CVE, and connects to retrieve data.
        If a valid response is received, it extracts vulnerability information and filters it based on the specified attributes before appending it to the result list.

        Args:
            cves (str | list[str])            : A single CVE ID or a list of CVE IDs to be searched.
            attributes (str, list[str] | None): A single attribute name or a list of attribute names to filter the retrieved vulnerability data by. Defaults to None.
            raw (bool)                        : Weither to return the raw result or the unified one
            payload (dict[str, Any] | None)   : Payload to send to the target CVE API url

        Returns:
            DataType: A list of dictionaries containing filtered vulnerability information for each provided CVE ID.
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
    def cve_url(cve: str) -> str:
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
    def cve_api_url(cve: str) -> str:
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

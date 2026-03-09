"""A module that describes common CVE connector behaviors."""

import json
import logging
import threading
from abc import ABC, abstractmethod
from time import time
from typing import Any, override
from urllib.parse import ParseResult

from oudjat.connectors import Connector, ConnectorMethod
from oudjat.connectors.vuln.exceptions import CVEDatabaseConnectionError
from oudjat.utils import Context, DataType
from oudjat.utils.types import StrType

from .cve_formats import CVEDataFormat


class CVEConnector(Connector, ABC):
    """A class that handles connection with Nist API to retrieve CVE informations."""

    # ****************************************************************
    # Attributes & Constructors

    URL: "ParseResult"
    API_URL: "ParseResult"

    def __init__(self, limit_per_minute: int = 10) -> None:
        """
        Create a new instance of NistConnector.

        Initializes a new instance of the `NistConnector` class, inheriting from `Connector`.
        It sets the target URL to the NIST API URL.
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)

        self._target: "ParseResult"
        super().__init__(target=self.__class__.API_URL)

        self._connection: dict[str, Any] | None = None

        # Request control
        self._lock: "threading.Lock" = threading.Lock()
        self._limit_per_minute: int = limit_per_minute
        self._last_token_time: float = False
        self._tokens: float = self._limit_per_minute

    # ****************************************************************
    # Methods - getters/setters

    @property
    def limit_per_minute(self) -> int:
        """
        Return the request limit per minute of the connector.

        Returns:
            int: The maximum number of request per minute the connector can send
        """

        return self._limit_per_minute

    @property
    def last_token_time(self) -> float:
        """
        Return the last time the connector used a token.

        Returns:
            float: The last time a token was used
        """

        return self._last_token_time

    @property
    def rate(self) -> float:
        """
        Return the replenish rate value of the connector.

        Returns:
            float: Repplenish rate value
        """

        return self._limit_per_minute / 60.0

    @property
    def interval(self) -> float:
        """
        Return the minimum interval between each request.

        Returns:
            float: Minimum interval value
        """

        return 60.0 / self._limit_per_minute

    # ****************************************************************
    # Methods - helpers

    def _cvss_metrics_keys(self, base_metrics_keys: list[str]) -> list[str]:
        """
        Filter metric keys to keep only cvss related ones.

        Returns:
            list[str]: Filtered metric keys
        """

        def check_key(k: str) -> bool:
            return "cvssV" in k

        return list(filter(check_key, base_metrics_keys))

    def time_to_wait(self) -> float:
        """
        Return the current time to wait before the connector API is available.

        Returns:
            float: Time to wait before a request can be sent again
        """

        return max(0.0, self.interval - (time() - self._last_token_time) + 0.1)

    @abstractmethod
    def vuln_from_connection(self) -> dict[str, Any] | None:
        """
        Extract base vulnerability from the connection object.

        Returns:
            dict[str, Any]: The base vulnerability dictionary
        """

        raise NotImplementedError(
            f"{Context()}::Method must be implemented by the overloading class"
        )

    # ****************************************************************
    # Methods - access

    def replenish(self) -> None:
        """
        Add tokens based on elapsed time and api rate.
        """

        now = time()
        elapsed = now - self._last_token_time

        added = elapsed * self.rate
        if added > 1e-6:
            self._tokens = min(self._limit_per_minute, self._tokens + added)
            self._last_token_time = now

    def token(self) -> bool:
        """
        Return a token if one is available.

        Returns:
            bool: True if a token is available. False otherwise
        """

        with self._lock:
            self.replenish()

            if self._tokens >= 1:
                self._tokens -= 1
                return True

            return False

    def clear_connection(self) -> None:
        """
        Clear the current connection.
        """

        self._connection = None

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

        context = Context()
        self._connection = None

        try:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            req = ConnectorMethod.GET(target, headers=headers, **kwargs)

            if req.status_code == 200:
                self._connection = json.loads(req.content.decode("utf-8"))
                self.logger.debug(f"Connected to {target}")

        except CVEDatabaseConnectionError as e:
            raise CVEDatabaseConnectionError(f"{context}::Could not connect to {target}\n{e}")

    @override
    @abstractmethod
    def fetch(
        self,
        cves: StrType,
        raw: bool = False,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Search the API for CVEs.

        Retrieves vulnerability information from the CVE.org API based on the provided CVE refs.
        If `search_filter` is not a list, it converts it to one. Similarly, if `attributes` is provided but not a list, it converts it to a list.
        It iterates over each CVE ID in `search_filter`, constructs the API endpoint URL for that CVE, and connects to retrieve data.
        If a valid response is received, it extracts vulnerability information and filters it based on the specified attributes before appending it to the result list.

        Args:
            cves (str | list[str])            : A single CVE ID or a list of CVE IDs to be searched.
            raw (bool)                        : Weither to return the raw result or the unified one
            payload (dict[str, Any] | None)   : Payload to send to the target CVE API url

        Returns:
            DataType: A list of dictionaries containing filtered vulnerability information for each provided CVE ID.
        """

        raise NotImplementedError(
            f"{Context()}::Method must be implemented by the overloading class"
        )

    @abstractmethod
    def unify_cve_data(self, cve: dict[str, Any]) -> CVEDataFormat:
        """
        Filter and reorganize cve data properties in order to obtain a unified format accross CVE connectors.

        Args:
            cve (dict[str, Any]): cve data as a dictionary

        Returns:
            CVEDataFormat: A formated dictionary
        """

        raise NotImplementedError(
            f"{Context()}::Method must be implemented by the overloading class"
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
            f"{Context()}::Method must be implemented by the overloading class"
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
            f"{Context()}::Method must be implemented by the overloading class"
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

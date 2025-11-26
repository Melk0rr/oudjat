"""A module to handle connection to the endoflife.date website."""

import logging
from typing import Any, override
from urllib.parse import ParseResult, urlparse

from oudjat.connectors import Connector, ConnectorMethod
from oudjat.connectors.endoflife.eol_endpoints import EndOfLifeEndpoint
from oudjat.utils import Context, DataType, UtilsList
from oudjat.utils.types import StrType

from .definitions import EOL_API_URL
from .exceptions import EndOfLifeAPIConnectionError


class EndOfLifeConnector(Connector):
    """A class to connect to endoflife.date."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self) -> None:
        """
        Initialize the EndOfLifeAPIConnector by setting up the connection to the EOL API URL and initializes an empty list of products.
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)

        self._target: "ParseResult"
        super().__init__(target=urlparse(EOL_API_URL))

        self._connection: dict[str, Any] | None = None

    # ****************************************************************
    # Methods

    @override
    def connect(self, **kwargs: Any) -> None:
        """
        Attempt to establish a connection to the API endpoint and retrieves product information if successful.

        It sets up the connection status and loads the product list from the API response.

        Raises:
            ConnectionError: If unable to connect to the API endpoint or retrieve data.
        """

        context = Context()
        self.logger.info(f"{context}::Connecting to {self._target.netloc}")

        self._connection = None

        try:
            headers = {"Accept": "application/json"}
            req = ConnectorMethod.GET(f"{self._target.geturl()}", headers=headers, **kwargs)

            if req.status_code == 200:
                self._connection = req.json()
                self.logger.info(f"{context}::Connected to {self._target.netloc}")

        except EndOfLifeAPIConnectionError as e:
            raise EndOfLifeAPIConnectionError(
                f"{context}::Could not connect to {self._target.netloc}\n{e}"
            )

    @override
    def fetch(
        self,
        endpoint: "EndOfLifeEndpoint" = EndOfLifeEndpoint.PRODUCTS,
        filter: str = "",
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Search the API for product infos.

        Args:
            endpoint (str)                 : The specific product to search for.
            filter (str)                   : A filter to append to the endpoint uri
            payload (dict[str, Any] | None): Payload containing additional arguments to send to the target

        Returns:
            DataType: A list of dictionaries containing information about the products that match the search criteria.

        Raises:
            ConnectionError: If unable to connect to the API endpoint or retrieve data.
            ValueError     : If the provided `search_filter` is not a valid product in the catalog.
        """

        context = Context()
        if self._connection is None:
            raise ConnectionError(
                f"{context}::Please run connect to initialize endoflife connection"
            )

        if payload is None:
            payload = {}

        self.logger.debug(f"{context}::{endpoint.value}/{filter} > {payload}")
        res = []
        try:
            headers = {"Accept": "application/json"}
            req = ConnectorMethod.GET(
                f"{self._target.geturl()}{endpoint.value}/{filter}", headers=headers, **payload
            )

            if req.status_code == 200:
                req_json = req.json()
                self.logger.debug(f"{context}::{endpoint.value}/{filter} > {req_json}")

                UtilsList.append_flat(res, req_json.get("result", []))

        except EndOfLifeAPIConnectionError as e:
            raise EndOfLifeAPIConnectionError(
                f"{context}::Could not retrieve {endpoint} infos:\n{e}"
            )

        return res

    # ****************************************************************
    # Methods: Products

    def products(
        self, product: str | None = None, tags: "StrType | None" = None, full: bool = False
    ) -> "DataType":
        """
        Return all the products or a specific one.

        If no product is specified and the full argument is set to True, returns all products with full details.
        If no product is specified and the tags argument is not None, returns products matching the provided tags.

        Args:
            product (str | None)         : Specific product to return
            tags (str | list[str] | None): Tags to filter the result
            full (bool)                  : Whether to return all the products details or not

        Returns:
            DataType: Data of the products
        """

        payload = {}
        if full and product is None:
            payload["filter"] = "full"

        elif product is not None:
            payload["filter"] = product

        res = self.fetch(endpoint=EndOfLifeEndpoint.PRODUCTS, **payload)
        if (product is None) and (tags is not None):
            if not isinstance(tags, list):
                tags = [tags]

            def element_has_tag(element: dict[str, Any]) -> bool:
                return any(tag in element.get("tags", []) for tag in tags)

            res = list(filter(element_has_tag, res))

        return res

    def product_releases(self, product: str, release: str = "latest") -> "DataType":
        """
        Return a specific product releases.

        Args:
            product (str): The product whose release will be fetched
            release (str): The release to fetch. Default latest

        Returns:
            DataType: Data containing the release details
        """

        return self.fetch(
            endpoint=EndOfLifeEndpoint.PRODUCTS, filter=f"{product}/releases/{release}"
        )

    def linux(self, full: bool = False) -> "DataType":
        """
        Return all the Linux distributions and kernel products.

        Args:
            full (bool): Whether to return all the products details or not

        Returns:
            DataType: Data containing the products details matching the Linux-distribution and Linux-foundation tags
        """

        return self.products(tags=["linux-distribution", "linux-foundation"], full=full)

    def windows(self) -> "DataType":
        """
        Retrieve Windows releases.

        Returns:
            DataType: Data containing release details for the specified target
        """

        return self.products(product="windows")

    def windows_server(self) -> "DataType":
        """
        Retrieve Windows releases.

        Returns:
            DataType: Data containing release details for the specified target
        """

        return self.products(product="windowsserver")

    # ****************************************************************
    # Methods: Categories

    def categories(self, category: str | None = None) -> "DataType":
        """
        Return the product categories.

        If no category is specified, all categories will be fetched.

        Args:
            category (str | None): Specific category to retrieve

        Returns:
            DataType: Data containing categories details
        """

        payload = {}

        if category:
            payload["filter"] = category

        return self.fetch(endpoint=EndOfLifeEndpoint.CATEGORIES, **payload)

    def apps(self) -> "DataType":
        """
        Return all the Apps products.

        Returns:
            DataType: Data containing the products details matching the App tag
        """

        return self.categories(category="app")

    def oses(self) -> "DataType":
        """
        Return all the OS products.

        Returns:
            DataType: Data containing the products details matching the OS tag
        """

        return self.categories(category="os")

    # ****************************************************************
    # Methods: Tags

    def tags(self, tag: str | None = None) -> "DataType":
        """
        Return the tags details.

        If no tag is specified, all tags will be fetched.

        Args:
            tag (str | None): Specific tag to retrieve

        Returns:
            DataType: Data containing tags details
        """

        payload = {}

        if tag:
            payload["filter"] = tag

        return self.fetch(endpoint=EndOfLifeEndpoint.TAGS, **payload)

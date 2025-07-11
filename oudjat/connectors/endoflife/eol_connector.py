"""A module to handle connection to the endoflife.date website."""

import json
import re
from typing import Any, override

import requests

from oudjat.assets.software.os.windows import WindowsEdition
from oudjat.connectors.connector import Connector

EOL_API_URL = "https://endoflife.date/api/"


class EndOfLifeConnector(Connector):
    """A class to connect to endoflife.date."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self) -> None:
        """
        Initialize the EndOfLifeAPIConnector by setting up the connection to the EOL API URL and initializes an empty list of products.
        """

        super().__init__(target=EOL_API_URL)
        self.products: list[str] = []
        self.connection: bool = False

    # ****************************************************************
    # Methods

    def get_products(self) -> list[str]:
        """
        Return a list of products.

        Returns:
            List[str]: A list containing the names of available products.
        """

        return self.products

    @override
    def connect(self) -> None:
        """
        Attempt to establish a connection to the API endpoint and retrieves product information if successful.

        It sets up the connection status and loads the product list from the API response.

        Raises:
            ConnectionError: If unable to connect to the API endpoint or retrieve data.
        """

        self.connection = False

        try:
            headers = {"Accept": "application/json"}
            req = requests.get(f"{self.target}all.json", headers=headers)

            if req.status_code == 200:
                self.connection = True
                self.products = json.loads(req.content.decode("utf-8"))

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.connect::Could not connect to {self.target}\n{e}"
            )

    @override
    def search(
        self, search_filter: str, attributes: list[str] | None = None, *args: Any, **kwargs: Any
    ) -> list[Any]:
        """
        Search the API for product infos.

        Args:
            search_filter (str)   : The specific product to search for.
            attributes (list[str]): Specify which attributes of the product to retrieve. Can be a single string or a list of strings. Defaults to None.
            *args (Any)           : any args the overriding method provides
            **kwargs (Any)        : any kwargs the overriding method provides

        Returns:
            List[Dict]: A list of dictionaries containing information about the products that match the search criteria.

        Raises:
            ConnectionError: If unable to connect to the API endpoint or retrieve data.
            ValueError     : If the provided `search_filter` is not a valid product in the catalog.
        """

        res = []

        if not self.connection or len(self.products) == 0:
            raise ConnectionError(
                f"{__class__.__name__}.search::Please run connect to initialize endoflife connection"
            )

        if search_filter not in self.products:
            raise ValueError(
                f"{__class__.__name__}.search::{search_filter} is not a valid product:\n{self.products}"
            )

        try:
            headers = {"Accept": "application/json"}
            req = requests.get(f"{self.target}{search_filter}.json", headers=headers)

            if req.status_code == 200:
                res = json.loads(req.content.decode("utf-8"))

                if attributes is not None:
                    res = [{k: v for k, v in e.items() if k in attributes} for e in res]

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.search::Could not retrieve {search_filter} infos:\n{e}"
            )

        return res

    def get_windows_rel(self, target: str = "windows") -> list[dict[str, str]]:
        """
        Retrieve Windows releases.

        Args:
            target (str, optional): The product name to search for. Defaults to "windows".

        Returns:
            List[Dict]: A list of dictionaries containing information about the Windows releases that match the criteria.

        Raises:
            ConnectionError: If unable to connect to the API endpoint or retrieve data.
        """

        win_eol = self.search(search_filter=target)

        for rel in win_eol:
            if target == "windows":
                win_editions = list(
                    set([e.get_category() for e in WindowsEdition.WINDOWS.editions])
                )
                r_edition: list[str] = win_editions[:-1]

                edi_search = re.search(
                    rf"^.+ \(?({'|'.join(win_editions)})\)?$", rel["releaseLabel"].upper()
                )
                if edi_search:
                    r_edition = [edi_search.group(1)]
                    rel["releaseLabel"] = rel["releaseLabel"][:-4]

                rel["edition"] = r_edition

            else:
                if rel["extendedSupport"]:
                    rel["eol"] = rel["extendedSupport"]

        return win_eol

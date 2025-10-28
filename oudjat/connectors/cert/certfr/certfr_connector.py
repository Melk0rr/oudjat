"""Module to connect to the CERTFR and initialize parsing."""

from datetime import datetime
from typing import override

from bs4 import BeautifulSoup

from oudjat.connectors import Connector, ConnectorMethod
from oudjat.utils.color_print import ColorPrint

from .certfr_page import CERTFRPage


class CERTFRConnector(Connector):
    """
    CERTFR class addressing certfr page behavior.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self) -> None:
        """
        Initialize a new instance of OudjatCERTFRConnection with the base link and service name set to "OudjatCERTFRConnection".

        Args:
            self (OudjatCERTFRConnection): The instance being initialized.
        """

        super().__init__(target=CERTFRPage.BASE_LINK)

    # ****************************************************************
    # Methods

    @override
    def connect(self) -> None:
        """
        Try to do a GET request to the target URL and sets connection attribute to True if the status code is 200.

        Raises:
            ConnectionError : if connection to target is unsuccessful

        Args:
            self (OudjatCERTFRConnection): The instance on which this method is called.

        Returns:
            None
        """

        try:
            if not isinstance(self._target, str):
                raise ValueError(f"{__class__.__name__}.connect::The CERTFR connector target must be a string")

            req = ConnectorMethod.GET(self._target)

            if req.status_code == 200:
                self._connection: bool = True

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.connect::Could not connect to {CERTFRPage.BASE_LINK}\n{e}"
            )

    @override
    def search(self, search_filter: str | list[str]) -> list[CERTFRPage]:
        """
        Search the CERTFR website using a filter (either a single string or a list of strings) and returns a list of CERTFRPage objects that match the search criteria.

        Args:
            self (OudjatCERTFRConnection): The instance on which this method is called.
            search_filter (Union[str, List[str]]): A single string or a list of strings used as filters for searching within CERTFR pages.

        Returns:
            List[CERTFRPage]: A list of CERTFRPage objects that match the search criteria.
        """

        res = []

        if not self.connection:
            self.connect()

        if not isinstance(search_filter, list):
            search_filter = [search_filter]

        search_filter = list(set(search_filter))

        for ref in search_filter:
            ColorPrint.blue(ref)

            page = CERTFRPage(ref)
            page.connect()
            page.parse()

            res.append(page)

        return res

    # ****************************************************************
    # Static methods

    @staticmethod
    def parse_feed(feed_url: str, date_str_filter: str | None = None) -> list[str]:
        """
        Perform a GET request to the provided feed URL and parses its content using BeautifulSoup to extract items based on optional filtering by date string.

        Args:
            feed_url (str): The URL of the RSS feed to be parsed.
            date_str_filter (str, optional): A date string used for filtering extracted items. Defaults to None.

        Returns:
            List[str]: A list of references extracted from the CERTFR feed page that match the date filter criteria if provided.
        """

        filtered_feed = []

        try:
            feed_req = ConnectorMethod.GET(feed_url)
            feed_soup = BeautifulSoup(feed_req.content, "xml")
            feed_items = feed_soup.find_all("item")

            for item in feed_items:
                item_link = item.find_next("link")

                certfr_ref = ""
                if item_link:
                    certfr_ref = CERTFRPage.get_ref_from_link(item_link.text)

                if date_str_filter:
                    try:
                        valid_date_format = "%Y-%m-%d"
                        date_filter = datetime.strptime(date_str_filter, valid_date_format)

                        item_pubdate = item.find_next("pubDate")
                        if item_pubdate:
                            date_str = item_pubdate.text.split(" +0000")[0]
                            date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")

                            if date > date_filter:
                                filtered_feed.append(certfr_ref)

                    except ValueError:
                        ColorPrint.red(
                            "Invalid date filter format. Please provide a date filter following the pattern YYYY-MM-DD !"
                        )

                else:
                    filtered_feed.append(certfr_ref)

        except Exception as e:
            print(
                e,
                f"A parsing error occured for {feed_url}: {e}\nCheck if the page has the expected format.",
            )

        return filtered_feed

"""Module to connect to the CERTFR and initialize parsing."""

import logging
from datetime import datetime
from typing import override
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup

from oudjat.connectors import Connector, ConnectorMethod
from oudjat.utils import Context
from oudjat.utils.types import StrType

from .certfr_page import CERTFRPage
from .exceptions import CERTFRParsingError


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

        self._target: "ParseResult"
        super().__init__(target=urlparse(CERTFRPage.BASE_LINK))

        self.logger: "logging.Logger" = logging.getLogger(__name__)

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

        self.logger.info(f"{Context()}::Connecting to {self._target.netloc}")
        try:
            req = ConnectorMethod.GET(self._target.geturl())

            if req.status_code == 200:
                self._connection: bool = True

        except ConnectionError as e:
            raise ConnectionError(f"{Context()}::Could not connect to {self._target.netloc}\n{e}")

    @override
    def fetch(self, search_filter: "StrType") -> list["CERTFRPage"]:
        """
        Fetch the CERTFR website using a filter.

        You can provide either a single string or a list of strings).
        Returns a list of CERTFRPage objects that match the search criteria.

        Args:
            search_filter (str | list[str]): A single string or a list of strings used as filters for searching within CERTFR pages.

        Returns:
            list[CERTFRPage]: A list of CERTFRPage objects that match the search criteria.
        """

        res = []

        if not self.connection:
            self.connect()

        if not isinstance(search_filter, list):
            search_filter = [search_filter]

        search_filter = list(set(search_filter))

        for ref in search_filter:
            self.logger.info(f"{Context()}::Fetching {ref}")

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
        Parse the content of the provided feed URL.

        Uses BeautifulSoup to extract items based on optional filtering by date string.

        Args:
            feed_url (str)              : The URL of the RSS feed to be parsed.
            date_str_filter (str | None): A date string used for filtering extracted items. Defaults to None.

        Returns:
            list[str]: A list of references extracted from the CERTFR feed page that match the date filter criteria if provided.
        """

        context = Context()
        logger = logging.getLogger(__name__)

        filtered_feed = []

        try:
            feed_req = ConnectorMethod.GET(feed_url)
            feed_soup = BeautifulSoup(feed_req.content, "xml")
            feed_items = feed_soup.find_all("item")

            for item in feed_items:
                item_link = item.find_next("link")

                certfr_ref = ""
                if item_link:
                    certfr_ref = CERTFRPage.ref_from_link(item_link.text)

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
                        logger.error(
                            f"{context}::Invalid date filter format. Please provide a date filter following the pattern YYYY-MM-DD !"
                        )

                else:
                    filtered_feed.append(certfr_ref)

        except CERTFRParsingError as e:
            logger.error(f"{context}::A parsing error occured for {feed_url}: {e}")

        return filtered_feed

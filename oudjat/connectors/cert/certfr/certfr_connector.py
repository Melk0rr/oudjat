"""Module to connect to the CERTFR and initialize parsing."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import override
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup
from yaspin import yaspin

from oudjat.connectors import Connector, ConnectorMethod
from oudjat.utils.context import Context
from oudjat.utils.logging import spinner_log
from oudjat.utils.types import DataType, StrType

from .certfr_page import CERTFRPage
from .exceptions import CERTFRInvalidLinkError, CERTFRParsingError


@dataclass
class CERTFRFeedItem:
    """
    A simple data class to store basic CERTFR feed item infos.
    """

    title: str
    ref: str


class CERTFRConnector(Connector):
    """
    CERTFR class addressing certfr page behavior.
    """

    # ****************************************************************
    # Attributes & Constructors

    FEED_URL: "ParseResult" = urlparse("https://www.cert.ssi.gouv.fr/feed/")

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

        try:
            req = ConnectorMethod.GET(self._target.geturl())

            if req.status_code == 200:
                self._connection: bool = True
                self.logger.info(f"Connected to {self._target.netloc}")

        except ConnectionError as e:
            raise ConnectionError(f"{Context()}::Could not connect to {self._target.netloc}\n{e}")

    @override
    def fetch(self, search_filter: "StrType", keywords: list[str] | None = None) -> "DataType":
        """
        Fetch the CERTFR website using a filter.

        You can provide either a single string or a list of strings).
        Returns a list of CERTFRPage objects that match the search criteria.

        Args:
            search_filter (str | list[str]): A single string or a list of strings used as filters for searching within CERTFR pages.
            keywords (list[str] | None)    : A list of keywords to compare to the pages

        Returns:
            list[CERTFRPage]: A list of CERTFRPage objects that match the search criteria.
        """

        if not self.connection:
            self.connect()

        if not isinstance(search_filter, list):
            search_filter = [search_filter]

        search_filter = list(set(search_filter))

        self.logger.info(f"Parsing {len(search_filter)} CERTFR pages")

        # Parsing
        with yaspin(text="Parsing CERTFR pages...") as spinner:
            res = []

            for ref in search_filter:
                spinner_log(f"Parsint {ref}", self.logger.info, spinner)

                try:
                    page = CERTFRPage(ref)
                    page.connect()
                    page.parse()

                    # Keyword match check
                    if keywords is not None:
                        page.match(keywords)

                    spinner_log(f"{ref} matched {len(page.matches)} keywords", self.logger.info, spinner)

                    res.append(page.to_dict())

                except Exception as e:
                    spinner_log(f"{Context()}::{e}", self.logger.error, spinner)
                    continue

            if len(res) == len(search_filter):
                spinner.ok(f"✅ Parsed of {len(res)} CERTFR pages")

            else:
                spinner.fail(f"❌ Parsing failed for {len(search_filter) - len(res)} CERTFR pages")

        return res

    def feed(
        self, date_filter_str: str | None = None, keywords: list[str] | None = None
    ) -> "DataType":
        """
        Parse the content of the provided feed URL.

        Uses BeautifulSoup to extract items based on optional filtering by date string.

        Args:
            date_filter_str (str | None): A date string used for filtering extracted items. Defaults to None.
            keywords (list[str] | None) : A list of keywords to compare to the pages

        Returns:
            list[str]: A list of references extracted from the CERTFR feed page that match the date filter criteria if any provided.
        """

        context = Context()
        logger = logging.getLogger(__name__)

        target = CERTFRConnector.FEED_URL.geturl()
        filtered_feed = []

        try:
            feed_req = ConnectorMethod.GET(target)
            feed_soup = BeautifulSoup(feed_req.content, "xml")
            feed_items = feed_soup.find_all("item")

            for item in feed_items:
                item_link = item.find_next("link")

                certfr_ref = ""
                if item_link:
                    try:
                        certfr_ref = CERTFRPage.ref_from_link(item_link.text)

                    except CERTFRInvalidLinkError:
                        logger.error(f"{context}::Invalid CERTFR link {item_link.text} - continue")
                        continue

                if date_filter_str:
                    try:
                        valid_date_format = "%Y-%m-%d"
                        date_filter = datetime.strptime(date_filter_str, valid_date_format)

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
            logger.error(f"{context}::A parsing error occured for {target}: {e}")

        return self.fetch(filtered_feed, keywords)

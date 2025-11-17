"""CERTFR module to specifically handle CERTFR pages."""

import re
from typing import Any, override
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup
from bs4.element import PageElement, ResultSet, Tag

from oudjat.assets.network import URL_REGEX
from oudjat.control.vulnerability import CVE, CVE_REGEX
from oudjat.utils.color_print import ColorPrint

from ...connector_methods import ConnectorMethod
from ..risk_types import RiskType
from .certfr_page_types import CERTFRPageType
from .definitions import CERTFR_LINK_REGEX, CERTFR_REF_REGEX, REF_TYPES


def clean_str(str_to_clean: str) -> str:
    """
    Clean a string from unwanted characters.

    Args:
        str_to_clean (str) : string to clean

    Returns:
        str : cleaned string
    """

    return str_to_clean.replace("\r", "").strip()


class CERTFRPage:
    """Describe a CERTFR page."""

    # ****************************************************************
    # Attributes & Constructors

    BASE_LINK: str = "https://www.cert.ssi.gouv.fr"

    def __init__(self, ref: str) -> None:
        """
        Initialize a CERTFRPage instance.

        Args:
            ref (str): The reference string used to identify and validate the page content.

        Raises:
            ValueError: If the provided reference is invalid and cannot be validated through either `is_valid_ref` or `is_valid_link`.
        """

        if not self.is_valid_ref(ref) and not self.is_valid_link(ref):
            raise ValueError(f"{__class__.__name__}::Invalid CERTFR ref provided : {ref}")

        self._ref: str = ref if self.is_valid_ref(ref) else self.ref_from_link(ref)

        self._raw_content: BeautifulSoup | None = None
        self._title: str | None = None

        self._meta: CERTFRPageMeta | None = None
        self._content: CERTFRPageContent | None = None

        # Set page type
        ref_search = re.search(rf"(?:{REF_TYPES})", self._ref)

        if not ref_search:
            raise ValueError(
                f"{__class__.__name__}.__init__::Could not match any reference type to {self._ref}"
            )

        ref_type: str = ref_search.group(0)

        self._link: ParseResult = urlparse(f"{self.BASE_LINK}/{CERTFRPageType[ref_type].value}/{self._ref}/")

    # ****************************************************************
    # Methods

    @property
    def ref(self) -> str:
        """
        Getter for the reference of the CERTFRPage instance.

        Returns:
            str: The reference string associated with the CERTFRPage instance.
        """

        return self._ref

    @property
    def title(self) -> str | None:
        """
        Getter for the page title of the CERTFRPage instance.

        Returns:
            str: The title string of the page.
        """

        return self._title

    @property
    def cves(self) -> list["CVE"]:
        """
        Retrieve the CVEs from the content section and returns them as a list. If no CVEs are found, it returns an empty list.

        Returns:
            list[CVE]: A list of CVE objects if available, otherwise an empty list.
        """

        return list(self._content.cves.values()) if self._content else []

    def connect(self) -> None:
        """
        Connect to a CERTFR page based on the given reference (ref).

        This method attempts to fetch the content from the URL associated with the ref using an HTTP GET request.
        If the connection is successful and the status code is 200, it parses the HTML content.

        Raises:
            ConnectionError : An error message is printed if the connection fails or encounters a non-200 status code.
        """

        # Handle possible connection error
        try:
            req = ConnectorMethod.GET(self._link.geturl())

            if req.status_code != 200:
                raise ConnectionError(
                    f"{__class__.__name__}.connect::Error while trying to connect to {self.ref}"
                )

            self._raw_content = BeautifulSoup(req.content, "html.parser")

            title = self._raw_content.find_next("title")

            if title:
                self._title = title.text

            print(self._title)

        except ConnectionError:
            ColorPrint.red(
                f"{__class__.__name__}.connect::Error while requesting {
                    self._ref
                }. Make sure it is accessible"
            )

    def disconnect(self) -> None:
        """
        Reset the parsing state of the CERTFRPage instance by setting raw_content, meta, and content to None.
        """

        self._raw_content = None
        self._meta = None
        self._content = None

    def parse(self) -> None:
        """
        Parse the page content if not already parsed.

        This method first ensures that a connection has been made.
        It then extracts meta and content information from the HTML structure of the page, which are encapsulated in CERTFRPageMeta and CERTFRPageContent objects respectively.

        Raises:
            Exception : An error message is printed in case of any parsing errors.
        """

        if self._raw_content is None:
            self.connect()

        if self._raw_content:
            try:
                sections: ResultSet = self._raw_content.find_all("section")

                if len(sections) >= 2:
                    # Meta parsing
                    self._meta = CERTFRPageMeta(meta_section=sections[0])
                    self._meta.parse()

                    # Content parsing
                    self._content = CERTFRPageContent(content_section=sections[1])
                    self._content.parse()

            except Exception as e:
                ColorPrint.red(
                    f"{__class__.__name__}.parse::A parsing error occured for {self._ref}\n{e}"
                )

    @override
    def __str__(self) -> str:
        """
        Convert the current CERTFRPage instance to a string representation. The method returns a string in the format "ref: title", where ref is the reference and title is the page title.

        Returns:
            str: A formatted string representing the CERTFRPage instance.
        """

        return f"{self._ref}: {self._title}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current CERTFRPage instance into a dictionary representation. The method creates a dictionary containing the ref, title, and parsed meta and content information if available.

        Returns:
            dict[str, Any]: A dictionary containing the page information.
        """

        content_dict: dict[str, Any] = self._content.to_dict() if self._content else {}
        meta_dict: dict[str, Any] = self._meta.to_dict() if self._meta else {}

        page_dict: dict[str, Any] = {
            "ref": self._ref,
            "title": self._title,
            **meta_dict,
            **content_dict,
        }

        return page_dict

    # ****************************************************************
    # Static methods

    @staticmethod
    def is_valid_ref(ref: str) -> bool:
        """
        Return whether the ref is valid or not.

        This method uses a regular expression (regex) to check if the provided reference string matches
        the predefined pattern CERTFR_REF_REGEX. It returns True if it matches, otherwise False.

        Args:
            ref (str): The reference string to be validated.

        Returns:
            bool: True if the reference is valid according to the regex pattern, False otherwise.
        """

        return re.match(CERTFR_REF_REGEX, ref) is not None

    @staticmethod
    def is_valid_link(link: str) -> bool:
        """
        Return whether the link is valid or not.

        This method uses a regular expression (regex) to check if the provided link string matches
        the predefined pattern CERTFR_LINK_REGEX. It returns True if it matches, otherwise False.

        Args:
            link (str): The link string to be validated.

        Returns:
            bool: True if the link is valid according to the regex pattern, False otherwise.
        """

        return re.match(CERTFR_LINK_REGEX, link) is not None

    @staticmethod
    def ref_from_link(link: str) -> str:
        """
        Return a CERTFR ref based on a link.

        This method first checks if the provided link string matches the regex pattern CERTFR_LINK_REGEX.
        If it does not match, it raises a ValueError. If it does match, it then uses another regex (CERTFR_REF_REGEX) to extract and return the reference number from the link.

        Args:
            link (str): The link string from which to extract the reference number.

        Returns:
            str: The extracted reference number if valid, otherwise raises a ValueError.

        Raises:
            ValueError: If the provided link does not match the regex pattern for a valid CERTFR link.
        """

        if not re.match(CERTFR_LINK_REGEX, link):
            raise ValueError(
                f"{__class__.__name__}.ref_from_link::Invalid CERTFR link provided: {link}"
            )

        return re.findall(CERTFR_REF_REGEX, link)[0]


class CERTFRPageMeta:
    """
    CERTFR pages often start with a table containing meta data on the current page. This class handles meta data table parsing.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, meta_section: BeautifulSoup) -> None:
        """
        Initialize new CERTFR meta parser.

        Args:
            meta_section (element): A BeautifulSoup4 element containing the meta data in a table format.
        """

        self._meta_table: PageElement = meta_section.find_all("table")[0]
        self._data: dict[str, Any] = {}

    # ****************************************************************
    # Methods

    @property
    def date_initial(self) -> str | None:
        """
        Retrieve the initial release date from meta table, if not already set, and returns it.

        Returns:
            str: The initial date of the page or None if not available.
        """

        return self._data.get("Date de la première version", None)

    @property
    def date_last(self) -> str | None:
        """
        Retrieve the last change date from meta table, if not already set, and returns it.

        Returns:
            str: The last change date of the page or None if not available.
        """

        return self._data.get("Date de la dernière version", None)

    @property
    def sources(self) -> list[str]:
        """
        Retrieve the sources from metadata, if not already set, and returns them as a list of cleaned strings.

        Returns:
            list[str]: A list of sources or None if not available.
        """

        clean_sources: list[str] = self._data.get("Source(s)", "").split("\n")
        clean_sources = [
            re.sub(r"\s+", " ", line).strip()
            for line in clean_sources
            if re.sub(r"\s+", "", line).strip()
        ]

        return clean_sources

    def parse(self) -> None:
        """
        Parse the meta table to extract key-value pairs and store them in `data`. This method populates the `data` attribute with a dictionary of cleaned metadata keys and values.
        """

        meta = {}
        for row in self._meta_table.find_all_next("tr"):
            cells = row.find_all_next("td")
            c_name = cells[0].text.strip()
            c_value = cells[-1].text.strip()

            meta[clean_str(c_name)] = clean_str(c_value)

        self._data = meta

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the metadata of the instance into a dictionary format, including initial date, last change date, and sources.

        Returns:
            dict[str, Any]: A dictionary containing the parsed metadata or an empty dictionary if no data is available.
        """

        meta_dict: dict[str, Any] = {
            "date_initial": self.date_initial,
            "date_last": self.date_last,
            "sources": self.sources,
        }

        return meta_dict


class CERTFRPageContent:
    """Handle content section from CERTFR page."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, content_section: BeautifulSoup) -> None:
        """
        Initialize new CERTFR page content.

        Args:
            content_section (element): The HTML content section to be parsed and used within the class instance.
        """

        self._content: BeautifulSoup = content_section
        self._data: dict[str, Any] = {}

    # ****************************************************************
    # Methods

    @property
    def risks(self) -> set[RiskType]:
        """
        Getter / parser for the list of risks.

        Args:
            short (bool): A flag to indicate if the risk information should be brief. Default is True.

        Returns:
            set: A set of RiskType objects parsed from the content.
        """

        risk_set: set[RiskType] = set()

        for risk in RiskType:
            if risk.value["fr"].lower() in [r.lower() for r in self._data.get("Risques", [])]:
                risk_set.add(risk)

        return risk_set

    @property
    def products(self) -> list[str]:
        """
        Getter / parser for affected products.

        Returns:
            list: A list of product names identified as affected by the issues in the content.
        """

        return self._data.get("Systèmes affectés", [])

    @property
    def description(self) -> str | None:
        """
        Getter / parser for description.

        Returns:
            str: A detailed description extracted from the content, or None if not available.
        """

        return self._data.get("Résumé", None)

    @property
    def solutions(self) -> list[str]:
        """
        Getter / parser for solutions.

        Returns:
            str: Solutions to the issues discussed in the content, or None if not available.
        """

        return self._data.get("Solutions", [])

    @property
    def cves(self) -> dict[str, CVE]:
        """
        Return the refs of all the related CVEs.

        Returns:
            list: A list of CVE references that are linked in the content.
        """

        cves = {}

        for cve in self._data.get("CVEs", []):
            if cve not in cves.keys():
                cves[cve] = CVE(ref=cve)

        return cves

    @property
    def documentations(self) -> list[str]:
        """
        Return the documentation section of a CERTFR page.

        Args:
            doc_filter (str): A string to filter out certain documentation URLs. Default is None.

        Returns:
            list: A filtered or unfiltered list of URLs pointing to documentation from the content.
        """

        return self._data.get("Documentation", [])

    def filter_documentations(self, doc_filter: str) -> list[str]:
        """
        Return the documentation section of a CERTFR page.

        Args:
            doc_filter (str): A string to filter out certain documentation URLs. Default is None.

        Returns:
            list: A filtered or unfiltered list of URLs pointing to documentation from the content.
        """

        docs = self.documentations

        if doc_filter != "":
            docs = [d for d in docs if doc_filter not in d]

        return docs

    def parse(self) -> None:
        """
        Parse content section to extract structured data.

        This method processes the HTML content looking for hierarchical titles and their corresponding lists or paragraphs, which are then stored in a dictionary format.
        """

        data: dict[str, Any] = {}
        titles = self._content.find_all("h2")

        for t in titles:
            next_el = t.find_next_sibling()

            if isinstance(next_el, Tag):
                if next_el.name == "ul":
                    data[t.text] = [li.text for li in next_el.find_all_next("li")]

                else:
                    data[t.text] = next_el.text

        data["CVEs"] = set(re.findall(CVE_REGEX, self._content.text))
        data["Documentation"] = re.findall(URL_REGEX, self._content.text)

        self._data = data

    def to_dict(self) -> dict[str, Any]:
        """
        Convert current instance into a dictionary.

        Returns:
            dict: A dictionary representation of the class instance's state, including risks, products, description, CVEs, solutions, and documentations.
        """

        content_dict: dict[str, Any] = {
            "risks": list(map(RiskType.risk_name, self.risks)),
            "products": self.products,
            "description": self.description,
            "cves": [cve.ref for cve in self.cves.values()],
            "solutions": self.solutions,
            "documentations": self.filter_documentations(doc_filter="cve.org"),
        }

        return content_dict

import re
from typing import Dict, List, Set

import requests
from bs4 import BeautifulSoup, element

from oudjat.model.vulnerability.cve import CVE, CVE_REGEX
from oudjat.utils.color_print import ColorPrint

from ...risk_types import RiskType, risk_name
from .certfr_page import CERTFRPageType
from .definitions import CERTFR_LINK_REGEX, CERTFR_REF_REGEX, REF_TYPES, URL_REGEX


def clean_str(str_to_clean: str) -> str:
    """
    Cleans a string from unwanted characters

    Args:
        str_to_clean (str) : string to clean

    Returns:
        str : cleaned string
    """

    return str_to_clean.replace("\r", "").strip()


class CERTFRPage:
    """Describes a CERTFR page"""

    # ****************************************************************
    # Attributes & Constructors

    BASE_LINK = "https://www.cert.ssi.gouv.fr"

    def __init__(self, ref: str) -> None:
        """Constructor for initializing a CERTFRPage instance.

        Args:
            ref (str): The reference string used to identify and validate the page content.

        Raises:
            ValueError: If the provided reference is invalid and cannot be validated through either `is_valid_ref` or `is_valid_link`.
        """

        if not self.is_valid_ref(ref) and not self.is_valid_link(ref):
            raise ValueError(f"Invalid CERTFR ref provided : {ref}")

        self.ref = ref if self.is_valid_ref(ref) else self.get_ref_from_link(ref)

        self.raw_content: element = None
        self.title: str = None

        self.meta: CERTFRPageMeta = None
        self.content: CERTFRPageContent = None

        self.CVE_RESOLVED = False

        # Set page type
        ref_type = re.search(rf"(?:{REF_TYPES})", self.ref).group(0)
        self.page_type = CERTFRPageType[ref_type].value

        self.link = f"{self.BASE_LINK}/{self.page_type}/{self.ref}/"

    # ****************************************************************
    # Methods

    def get_ref(self) -> str:
        """
        Getter for the reference of the CERTFRPage instance.

        Returns:
            str: The reference string associated with the CERTFRPage instance.
        """
        return self.ref

    def get_title(self) -> str:
        """
        Getter for the page title of the CERTFRPage instance.

        Returns:
            str: The title string of the page.
        """
        return self.title

    def get_cves(self) -> List["CVE"]:
        """
        This method retrieves the CVEs from the content section and returns them as a list. If no CVEs are found, it returns an empty list.

        Returns:
            List["CVE"]: A list of CVE objects if available, otherwise an empty list.
        """
        cves = self.content.get_cves()

        if cves is not None:
            cves = cves.values()

        return cves

    def connect(self) -> None:
        """
        Connects to a CERTFR page based on the given reference (ref).

        This method attempts to fetch the content from the URL associated with the ref using an HTTP GET request.
        If the connection is successful and the status code is 200, it parses the HTML content.

        Raises:
            ConnectionError : An error message is printed if the connection fails or encounters a non-200 status code.
        """

        # Handle possible connection error
        try:
            req = requests.get(self.link)

            if req.status_code != 200:
                raise ConnectionError(f"Error while trying to connect to {self.ref}")

            self.raw_content = BeautifulSoup(req.content, "html.parser")
            self.title = self.raw_content.title.text

            print(self.title)

        except ConnectionError:
            ColorPrint.red(
                f"CERTFRPage::Error while requesting {self.ref}. Make sure it is accessible"
            )

    def disconnect(self) -> None:
        """
        Resets the parsing state of the CERTFRPage instance by setting raw_content, meta, and content to None.
        """

        self.raw_content = None
        self.meta = None
        self.content = None

    def parse(self) -> None:
        """
        Parses the page content if not already parsed.

        This method first ensures that a connection has been made.
        It then extracts meta and content information from the HTML structure of the page, which are encapsulated in CERTFRPageMeta and CERTFRPageContent objects respectively.

        Raises:
            Exception : An error message is printed in case of any parsing errors.
        """

        if self.raw_content is None:
            self.connect()

        try:
            sections = self.raw_content.article.find_all("section")

            # Meta parsing
            self.meta = CERTFRPageMeta(meta_section=sections[0])
            self.meta.parse()

            # Content parsing
            self.content = CERTFRPageContent(content_section=sections[1])
            self.content.parse()

        except Exception as e:
            ColorPrint.red(f"CERTFRPage::A parsing error occured for {self.ref}\n{e}")

    def __str__(self) -> str:
        """
        Converts the current CERTFRPage instance to a string representation.
        This method returns a string in the format "ref: title", where ref is the reference and title is the page title.

        Returns:
            str: A formatted string representing the CERTFRPage instance.
        """

        return f"{self.ref}: {self.title}"

    def to_dict(self) -> Dict:
        """
        Converts the current CERTFRPage instance into a dictionary representation.
        This method creates a dictionary containing the ref, title, and parsed meta and content information if available.

        Returns:
            Dict: A dictionary containing the page information.
        """

        page_dict = {}

        if self.meta is not None:
            page_dict = {
                "ref": self.ref,
                "title": self.title,
                **self.meta.to_dict(),
                **self.content.to_dict(),
            }

        return page_dict

    # ****************************************************************
    # Static methods

    @staticmethod
    def is_valid_ref(ref: str) -> bool:
        """
        Returns whether the ref is valid or not.

        This method uses a regular expression (regex) to check if the provided reference string matches
        the predefined pattern CERTFR_REF_REGEX. It returns True if it matches, otherwise False.

        Args:
            ref (str): The reference string to be validated.

        Returns:
            bool: True if the reference is valid according to the regex pattern, False otherwise.
        """

        return re.match(CERTFR_REF_REGEX, ref)

    @staticmethod
    def is_valid_link(link: str) -> bool:
        """
        Returns whether the link is valid or not.

        This method uses a regular expression (regex) to check if the provided link string matches
        the predefined pattern CERTFR_LINK_REGEX. It returns True if it matches, otherwise False.

        Args:
            link (str): The link string to be validated.

        Returns:
            bool: True if the link is valid according to the regex pattern, False otherwise.
        """

        return re.match(CERTFR_LINK_REGEX, link)

    @staticmethod
    def get_ref_from_link(link: str) -> str:
        """
        Returns a CERTFR ref based on a link.

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
            raise ValueError(f"Invalid CERTFR link provided: {link}")

        return re.findall(CERTFR_REF_REGEX, link)[0]


class CERTFRPageMeta:
    """
    CERTFR pages often start with a table containing meta data on the current page
    This class handles meta data table parsing
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, meta_section: element) -> None:
        """
        Constructor for MetaParser.

        Args:
            meta_section (element): A BeautifulSoup4 element containing the meta data in a table format.
        """

        self.meta_table = meta_section.find_all("table")[0]
        self.data = None

        self.date_initial: str = None
        self.date_last: str = None
        self.sources: List[str] = None

    # ****************************************************************
    # Methods

    def parse(self) -> None:
        """
        Parse the meta table to extract key-value pairs and store them in `data`.
        This method populates the `data` attribute with a dictionary of cleaned metadata keys and values.
        """

        meta = {}

        for row in self.meta_table.find_all("tr"):
            cells = row.find_all("td")
            c_name = cells[0].text.strip()
            c_value = cells[-1].text.strip()

            meta[clean_str(c_name)] = clean_str(c_value)

        self.data = meta

    def get_date_initial(self) -> str:
        """
        This method retrieves the initial release date from meta table, if not already set, and returns it.

        Returns:
            str: The initial date of the page or None if not available.
        """

        if self.data is not None and self.date_initial is None:
            self.date_initial = self.data.get("Date de la première version", None)

        return self.date_initial

    def get_date_last(self) -> str:
        """
        This method retrieves the last change date from meta table, if not already set, and returns it.

        Returns:
            str: The last change date of the page or None if not available.
        """

        if self.data is not None and self.date_last is None:
            self.date_last = self.data.get("Date de la dernière version", None)

        return self.date_last

    def get_sources(self) -> List[str]:
        """
        This method retrieves the sources from metadata, if not already set, and returns them as a list of cleaned strings.

        Returns:
            List[str]: A list of sources or None if not available.
        """

        if self.data is not None and self.sources is None:
            clean_sources = self.data.get("Source(s)", "").split("\n")
            clean_sources = [
                re.sub(r"\s+", " ", line).strip()
                for line in clean_sources
                if re.sub(r"\s+", "", line).strip()
            ]

            self.sources = clean_sources

        return self.sources

    def to_dict(self) -> Dict:
        """
        This method converts the metadata of the instance into a dictionary format, including initial date, last change date, and sources.

        Returns:
            Dict: A dictionary containing the parsed metadata or an empty dictionary if no data is available.
        """
        meta_dict = {}

        if self.data is not None:
            meta_dict = {
                "date_initial": self.get_date_initial(),
                "date_last": self.get_date_last(),
                "sources": self.get_sources(),
            }

        return meta_dict


class CERTFRPageContent:
    """Handles content section from CERTFR page"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, content_section: element) -> None:
        """
        Constructor to initialize new CERTFR page content

        Args:
            content_section (element): The HTML content section to be parsed and used within the class instance.
        """
        self.content = content_section
        self.data = None

        self.solutions = None
        self.description = None
        self.risks: Set[str] = None
        self.cves: Dict["CVE"] = None
        self.documentations: List[str] = None
        self.affected_products: List[str] = None

    # ****************************************************************
    # Methods

    def get_risks(self, short: bool = True) -> Set["RiskType"]:
        """
        Getter / parser for the list of risks.

        Args:
            short (bool): A flag to indicate if the risk information should be brief. Default is True.

        Returns:
            set: A set of RiskType objects parsed from the content.
        """

        if self.data is not None and self.risks is None:
            risk_set = set()

            for risk in list(RiskType):
                if risk.value["fr"].lower() in [r.lower() for r in self.data.get("Risques", [])]:
                    risk_set.add(risk)

            self.risks = risk_set

        return self.risks

    def get_products(self) -> List[str]:
        """
        Getter / parser for affected products.

        Returns:
            list: A list of product names identified as affected by the issues in the content.
        """

        if self.data is not None and self.affected_products is None:
            self.affected_products = self.data.get("Systèmes affectés", [])

        return self.affected_products

    def get_description(self) -> str:
        """
        Getter / parser for description.

        Returns:
            str: A detailed description extracted from the content, or None if not available.
        """

        if self.data is not None and self.description is None:
            self.description = self.data.get("Résumé", None)

        return self.description

    def get_solutions(self) -> str:
        """
        Getter / parser for solutions.

        Returns:
            str: Solutions to the issues discussed in the content, or None if not available.
        """

        if self.data is not None and self.solutions is None:
            self.solutions = self.data.get("Solutions", None)

        return self.solutions

    def get_cves(self) -> Dict[str, CVE]:
        """
        Returns the refs of all the related CVEs.

        Returns:
            list: A list of CVE references that are linked in the content.
        """

        if self.data is not None and self.cves is None:
            cves = {}

            for cve in self.data.get("CVEs", []):
                if cve not in cves.keys():
                    cves[cve] = CVE(ref=cve)

            self.cves = cves

        return self.cves

    def get_documentations(self, doc_filter: str = None) -> List[str]:
        """
        Getter for the documentations.

        Args:
            filter (str): A string to filter out certain documentation URLs. Default is None.

        Returns:
            list: A filtered or unfiltered list of URLs pointing to documentation from the content.
        """

        if self.data is not None and self.documentations is None:
            self.documentations = self.data.get("Documentation", [])

        docs = self.documentations

        if doc_filter is not None and doc_filter != "":
            docs = [d for d in self.documentations if filter not in d]

        return docs

    def parse(self) -> None:
        """
        Parse content section to extract structured data.

        This method processes the HTML content looking for hierarchical titles and their corresponding lists or paragraphs, which are then stored in a dictionary format.
        """

        data = {}

        titles = self.content.find_all("h2")

        for t in titles:
            next_el = t.find_next_sibling()

            if next_el.name == "ul":
                data[t.text] = [li.text for li in next_el.find_all("li")]

            else:
                data[t.text] = next_el.text

        data["CVEs"] = set(re.findall(CVE_REGEX, self.content.text))
        data["Documentation"] = re.findall(URL_REGEX, self.content.text)

        self.data = data

    def to_dict(self) -> Dict:
        """
        Converts current instance into a dictionary.

        Returns:
            dict: A dictionary representation of the class instance's state, including risks, products, description, CVEs, solutions, and documentations.
        """

        content_dict = {}

        if self.data is not None:
            content_dict = {
                "risks": list(map(risk_name, self.get_ris)),
                "products": self.get_products(),
                "description": self.get_description(),
                "cves": [cve.get_ref() for cve in self.get_cves().values()],
                "solutions": self.get_solutions(),
                "documentations": self.get_documentations(doc_filter="cve.org"),
            }

        return content_dict

"""Module that handles CVRF document manipulation."""

import json
import re
from typing import Any

from oudjat.connectors import ConnectorMethod
from oudjat.utils.color_print import ColorPrint

from .definitions import API_BASE_URL, API_REQ_HEADERS, CVRF_ID_REGEX
from .ms_product import MSProduct
from .ms_remed import MSRemed
from .ms_vuln import MSVuln


class MSCVRFDocument:
    """Class to manipulate MS CVRF documents."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, doc_id: str) -> None:
        """
        Create a new instance of MSCVRFDocument.

        Args:
            doc_id (str): The ID of the CVRF document, must follow the 'YYYY-MMM' format.

        Raises:
            ValueError: If the provided ID does not match the required regex pattern.
        """

        if not re.match(CVRF_ID_REGEX, doc_id):
            raise ValueError(f"{__class__.__name__}::CVRF ID must follow the 'YYYY-MMM' format !")

        self._id: str = doc_id
        self._url: str = f"{API_BASE_URL}cvrf/{self._id}"

        url_resp = ConnectorMethod.GET(self._url, headers=API_REQ_HEADERS)

        if url_resp.status_code != 200:
            raise ConnectionError(f"{__class__.__name__}::Could not connect to {self._url}")

        ColorPrint.green(f"{self._url}")

        self._content: dict[str, Any] = json.loads(url_resp.content)
        self._products: dict[str, "MSProduct"] = {}
        self._vulns: dict[str, "MSVuln"] = {}
        self._kbs: dict[int, "MSRemed"] = {}

    # ****************************************************************
    # Methods

    @property
    def id(self) -> str:
        """
        Getter for the document ID.

        Returns:
            str: The ID of the CVRF document.
        """

        return self._id

    @property
    def products(self) -> dict[str, MSProduct]:
        """
        Return the MS products mentioned in the document. If the product list is not already parsed, this method will trigger a parsing of the products from the document content.

        Returns:
            dict[str, MSProduct]: A dictionary containing the products keyed by their IDs.
        """

        if not self._products:
            self.parse_products()

        return self._products

    @property
    def vulnerabilities(self) -> dict[str, MSVuln]:
        """
        Return the vulnerabilities mentioned in the document. If the vulnerability list is not already parsed, this method will trigger a parsing of the vulnerabilities from the document content.

        Returns:
            Dict[str, MSVuln]: A dictionary containing the vulnerabilities keyed by their CVE IDs.
        """

        if not self._vulns:
            self.parse_vulnerabilities()

        return self._vulns

    @property
    def remediations(self) -> dict[int, MSRemed]:
        """
        Return the MS KBs mentioned in the document.

        If the KB list is not already parsed, this method will trigger a parsing of the KBs from the document content.
        Note that this method indirectly calls parse_vulnerabilities to ensure products are parsed before KBs.

        Returns:
            Dict[str, MSRemed]: A dictionary containing the KBs keyed by their numbers.
        """

        if not self._kbs:
            self.parse_vulnerabilities()

        return self._kbs

    def add_product(self, product: MSProduct) -> None:
        """
        Add a product to the list of products in the document.

        Args:
            product (MSProduct): The product to be added.
        """

        if product.pid not in self._products.keys():
            self._products[product.pid] = product

    def add_vuln(self, vuln: MSVuln) -> None:
        """
        Add a vulnerability to the list of vulnerabilities in the document.

        Args:
            vuln (MSVuln): The vulnerability to be added.
        """

        if vuln.cve not in self._vulns.keys():
            self._vulns[vuln.cve] = vuln

    def add_kb(self, kb: MSRemed) -> None:
        """
        Add a KB to the list of KBs in the document.

        Args:
            kb (MSRemed): The KB to be added.
        """

        if kb.number not in self._kbs.keys():
            self._kbs[kb.number] = kb

    def parse_products(self) -> None:
        """
        Parse the products from the document content and adds them to the internal product list.
        """

        prod_tree = self._content["ProductTree"]["Branch"][0]["Items"]
        for branch in prod_tree:
            for p in branch["Items"]:
                self.add_product(
                    MSProduct(pid=p["ProductID"], name=p["Value"], product_type=branch["Name"])
                )

    def parse_vulnerabilities(self) -> None:
        """
        Parse the vulnerabilities from the document content and adds them to the internal vulnerability list.
        """

        if not self._products:
            self.parse_products()

        for raw_vuln in self._content["Vulnerability"]:
            vuln = MSVuln(cve=raw_vuln["CVE"])

            for kb in raw_vuln["Remediations"]:
                kb_id = kb["Description"]["Value"]

                mskb = MSRemed(num=kb_id)
                mskb.set_products_from_list(
                    [self._products[pid] for pid in kb.get("ProductID", [])]
                )

                self.add_kb(mskb)
                vuln.add_kb(kb_id, mskb)

            self.add_vuln(vuln)

import json
import re
from typing import Dict

import requests

from oudjat.utils.color_print import ColorPrint

from .definitions import API_BASE_URL, API_REQ_HEADERS, CVRF_ID_REGEX
from .ms_product import MSProduct
from .ms_remed import MSRemed
from .ms_vuln import MSVuln


class MSCVRFDocument:
    """Class to manipulate MS CVRF documents"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, doc_id: str) -> None:
        """
        Constructor for the MSCVRFDocument class.

        Args:
            id (str): The ID of the CVRF document, must follow the 'YYYY-MMM' format.

        Raises:
            ValueError: If the provided ID does not match the required regex pattern.
        """

        if not re.match(CVRF_ID_REGEX, doc_id):
            raise ValueError(f"{__class__.__name__}::CVRF ID must follow the 'YYYY-MMM' format !")

        self.id = doc_id
        self.url = f"{API_BASE_URL}cvrf/{self.id}"

        url_resp = requests.get(self.url, headers=API_REQ_HEADERS)

        if url_resp.status_code != 200:
            raise ConnectionError(f"{__class__.__name__}::Could not connect to {self.url}")

        ColorPrint.green(f"{self.url}")
        self.content = json.loads(url_resp.content)

        self.products = {}
        self.vulns = {}
        self.kbs = {}

    # ****************************************************************
    # Methods

    def get_doc_id(self) -> str:
        """
        Getter for the document ID.

        Returns:
            str: The ID of the CVRF document.
        """

        return self.id

    def get_products(self) -> Dict[str, "MSProduct"]:
        """
        Returns the MS products mentioned in the document.
        If the product list is not already parsed, this method will trigger a parsing of the products from the document content.

        Returns:
            Dict[str, MSProduct]: A dictionary containing the products keyed by their IDs.
        """

        if not self.products:
            self.parse_products()

        return self.products

    def get_vulnerabilities(self) -> Dict[str, "MSVuln"]:
        """
        Returns the vulnerabilities mentioned in the document.
        If the vulnerability list is not already parsed, this method will trigger a parsing of the vulnerabilities from the document content.

        Returns:
            Dict[str, MSVuln]: A dictionary containing the vulnerabilities keyed by their CVE IDs.
        """

        if not self.vulns:
            self.parse_vulnerabilities()

        return self.vulns

    def get_kbs(self) -> Dict[str, "MSRemed"]:
        """
        Returns the MS KBs mentioned in the document.

        If the KB list is not already parsed, this method will trigger a parsing of the KBs from the document content.
        Note that this method indirectly calls parse_vulnerabilities to ensure products are parsed before KBs.

        Returns:
            Dict[str, MSRemed]: A dictionary containing the KBs keyed by their numbers.
        """

        if not self.kbs:
            self.parse_vulnerabilities()

        return self.kbs

    def add_product(self, product: "MSProduct") -> None:
        """
        Adds a product to the list of products in the document.

        Args:
            product (MSProduct): The product to be added.
        """

        if product.get_id() not in self.products.keys():
            self.products[product.get_id()] = product

    def add_vuln(self, vuln: "MSVuln") -> None:
        """
        Adds a vulnerability to the list of vulnerabilities in the document.

        Args:
            vuln (MSVuln): The vulnerability to be added.
        """

        if vuln.get_cve() not in self.vulns.keys():
            self.vulns[vuln.get_cve()] = vuln

    def add_kb(self, kb: "MSRemed") -> None:
        """
        Adds a KB to the list of KBs in the document.

        Args:
            kb (MSRemed): The KB to be added.
        """

        if kb.get_number() not in self.kbs.keys():
            self.kbs[kb.get_number()] = kb

    def parse_products(self) -> None:
        """
        Parses the products from the document content and adds them to the internal product list
        """

        prod_tree = self.content["ProductTree"]["Branch"][0]["Items"]
        for branch in prod_tree:
            for p in branch["Items"]:
                pid = p["ProductID"]
                prod = MSProduct(pid=pid, name=p["Value"], product_type=branch["Name"])
                self.add_product(prod)

    def parse_vulnerabilities(self) -> None:
        """
        Parses the vulnerabilities from the document content and adds them to the internal vulnerability list
        """

        if not self.products:
            self.parse_products()

        for v in self.content["Vulnerability"]:
            vuln = MSVuln(cve=v["CVE"])

            for kb in v["Remediations"]:
                kb_num = kb["Description"]["Value"]

                mskb = MSRemed(num=kb_num)
                mskb.set_products([self.products[pid] for pid in kb.get("ProductID", [])])

                self.add_kb(mskb)
                vuln.add_kb(kb_num=kb_num, kb=mskb)

            self.add_vuln(vuln)

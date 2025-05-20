import re
from typing import Any, Dict, List

from oudjat.utils.mappers import any_to_dict

from .definitions import CVE_REGEX
from .ms_product import MSProduct
from .ms_remed import MSRemed


class MSVuln:
    """Class to manipulate CVE data related to MS products"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, cve: str) -> None:
        """
        Creates a new instance of MSVuln

        Args:
            cve (str): The Common Vulnerabilities and Exposures identifier for the vulnerability.

        Raises:
            ValueError: If the provided CVE does not match the expected regex pattern.
        """

        if not re.match(CVE_REGEX, cve):
            raise ValueError(f"{__class__.__name__}::Invalid CVE provided: {cve}")

        self.cve = cve
        self.kbs: Dict[str, MSRemed] = {}
        self.products: Dict[str, MSProduct] = {}

    # ****************************************************************
    # Methods

    def get_cve(self) -> str:
        """
        Returns the CVE tied to the current vuln

        Returns:
            str: CVE reference
        """

        return self.cve

    def get_remediations(self) -> Dict[str, MSRemed]:
        """
        Returns the remediations for the current vuln

        Returns:
            Dict: a dictionary of MSRemed instances
        """

        return self.kbs

    def get_impacted_products(self) -> Dict[str, MSProduct]:
        """
        Returns the products impacted by the current vuln

        Returns:
            Dict: a dictionary of MSProduct instances
        """

        return self.products

    def add_kb(self, kb_num: int, kb: MSRemed) -> None:
        """
        Adds a KB to vuln KB list

        Args:
            kb_num (int): The number of the knowledge base article related to the vulnerability.
            kb (MSRemed): The remediation data for the given KB number.

        Raises:
            ValueError: If the provided KB number does not match the expected regex pattern.
        """

        if re.match(KB_NUM_REGEX, str(kb_num)) or re.match(r"(\w+)$", str(kb_num)):
            self.kbs[str(kb_num)] = kb

    def to_flat_dict(self) -> List[Dict]:
        """
        Converts kbs into dictionaries

        Returns:
            List[Dict]: A list of flattened dictionaries, each representing a KB and its related CVE.
        """

        return [
            {"cve": self.cve, **kb_dict}
            for kb_dict in [k.to_flat_dict() for k in self.kbs.values()]
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts current vuln into a dict

        Returns:
            Dict[str, Any]: A dictionary representation of the MSVuln object containing CVE and its associated KBs.
        """

        return {
            "cve": self.cve,
            "kbs": list(map(any_to_dict, self.kbs.values())),
        }

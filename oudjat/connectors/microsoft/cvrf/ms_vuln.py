"""A module to describe Vulnerabilities mentionned in a CVRF document."""

import re
from typing import Any

from oudjat.utils.mappers import any_to_dict

from .definitions import CVE_REGEX, KB_NUM_REGEX
from .ms_product import MSProduct
from .ms_remed import MSRemed


class MSVuln:
    """Class to manipulate CVE data related to MS products in a CVRF document."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, cve: str) -> None:
        """
        Create a new instance of MSVuln.

        Args:
            cve (str): The Common Vulnerabilities and Exposures identifier for the vulnerability.

        Raises:
            ValueError: If the provided CVE does not match the expected regex pattern.
        """

        if not re.match(CVE_REGEX, cve):
            raise ValueError(f"{__class__.__name__}::Invalid CVE provided: {cve}")

        self.cve: str = cve
        self.kbs: dict[int, MSRemed] = {}
        self.products: dict[str, MSProduct] = {}

    # ****************************************************************
    # Methods

    def get_cve(self) -> str:
        """
        Return the CVE tied to the current vuln.

        Returns:
            str: CVE reference
        """

        return self.cve

    def get_remediations(self) -> dict[int, MSRemed]:
        """
        Return the remediations for the current vuln.

        Returns:
            Dict: a dictionary of MSRemed instances
        """

        return self.kbs

    def get_impacted_products(self) -> dict[str, MSProduct]:
        """
        Return the products impacted by the current vuln.

        Returns:
            Dict: a dictionary of MSProduct instances
        """

        return self.products

    def add_kb(self, kb_num: int, kb: MSRemed) -> None:
        """
        Add a KB to vuln KB list.

        Args:
            kb_num (int): The number of the knowledge base article related to the vulnerability.
            kb (MSRemed): The remediation data for the given KB number.

        Raises:
            ValueError: If the provided KB number does not match the expected regex pattern.
        """

        if re.match(KB_NUM_REGEX, str(kb_num)) or re.match(r"(\w+)$", str(kb_num)):
            self.kbs[str(kb_num)] = kb

    def to_flat_dict(self) -> list[dict[str, Any]]:
        """
        Convert kbs into dictionaries.

        Returns:
            List[Dict]: A list of flattened dictionaries, each representing a KB and its related CVE.
        """

        return [
            {"cve": self.cve, **kb_dict}
            for kb_dict in [k.to_flat_dict() for k in self.kbs.values()]
        ]

        return [{"cve": self.cve, **kb_dict} for kb_dict in kb_dictionaries]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert current vuln into a dict.

        Returns:
            Dict[str, Any]: A dictionary representation of the MSVuln object containing CVE and its associated KBs.
        """

        return {
            "cve": self.cve,
            "kbs": list(map(any_to_dict, self.kbs.values())),
        }

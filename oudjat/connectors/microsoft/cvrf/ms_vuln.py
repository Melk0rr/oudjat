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
        Creates a new instance of MSVuln based on the provided CVE ref

        Args:
            cve (str): the cve reference this instance will be based on
        """

        if not re.match(CVE_REGEX, cve):
            raise (f"{__class__.__name__}::Invalid CVE provided: {cve}")

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

    def add_kb(self, kb: MSRemed) -> None:
        """
        Adds a new MSRemed instance to vuln KB list

        Args:
            kb (MSRemed): MSRemed instance to add
        """

        self.kbs[kb.get_number()] = kb

    def to_flat_dict(self) -> List[Dict]:
        """
        Converts kbs into dictionaries

        Returns:
            List[Dict]: a list of MSRemed dictionary representations
        """

        return [
            {"cve": self.cve, **kb_dict}
            for kb_dict in [k.to_flat_dict() for k in self.kbs.values()]
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts current vuln into a dict

        Returns:
            Dict: a dictionary representing the current instance
        """
        return {
            "cve": self.cve,
            "kbs": list(map(any_to_dict, self.kbs.values())),
        }

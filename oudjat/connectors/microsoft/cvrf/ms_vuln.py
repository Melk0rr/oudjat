import re
from typing import Any, Dict, List

from oudjat.utils.mappers import any_to_dict

from .definitions import CVE_REGEX, KB_NUM_REGEX
from .ms_product import MSProduct
from .ms_remed import MSRemed


class MSVuln:
    """Class to manipulate CVE data related to MS products"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, cve: str) -> None:
        """Constructor"""

        if not re.match(CVE_REGEX, cve):
            raise (f"Invalid CVE provided: {cve}")

        self.cve = cve
        self.kbs: Dict[str, MSRemed] = {}
        self.products: Dict[str, MSProduct] = {}

    # ****************************************************************
    # Methods

    def get_cve(self) -> str:
        """Getter for CVE"""

        return self.cve

    def get_remediations(self) -> Dict[str, MSRemed]:
        """Getter for KB list"""

        return self.kbs

    def get_remediation_numbers(self) -> List[int]:
        """Returns kb numbers"""

        return self.kbs.keys()

    def get_impacted_products(self) -> Dict[str, MSProduct]:
        """Getter for impacted product list"""
        return self.products

    def add_kb(self, kb_num: int, kb: MSRemed) -> None:
        """Adds a KB to vuln KB list"""

        if re.match(KB_NUM_REGEX, kb_num) or re.match(r"(\w+)$", kb_num):
            self.kbs[kb_num] = kb

    def to_flat_dict(self) -> List[Dict]:
        """Converts kbs into dictionaries"""

        return [
            {"cve": self.cve, **kb_dict}
            for kb_dict in [k.to_flat_dict() for k in self.kbs.values()]
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Converts current vuln into a dict"""
        return {
            "cve": self.cve,
            "kbs": list(map(any_to_dict, self.kbs.values())),
        }

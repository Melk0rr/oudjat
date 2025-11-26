"""A module to describe Vulnerabilities mentionned in a CVRF document."""

import re
from typing import Any

from oudjat.control.vulnerability import CVE_REGEX, InvalidCVERefError
from oudjat.utils import Context, DataType
from oudjat.utils.mappers import any_to_dict

from .cvrf_product import CVRFProduct
from .cvrf_remed import CVRFRemed
from .definitions import KB_NUM_REGEX


class CVRFVuln:
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
            raise InvalidCVERefError(f"{Context()}::Invalid CVE provided: {cve}")

        self._cve: str = cve
        self._kbs: dict[int, "CVRFRemed"] = {}
        self._products: dict[str, "CVRFProduct"] = {}

    # ****************************************************************
    # Methods

    @property
    def cve(self) -> str:
        """
        Return the CVE tied to the current vuln.

        Returns:
            str: CVE reference
        """

        return self._cve

    @property
    def remediations(self) -> dict[int, "CVRFRemed"]:
        """
        Return the remediations for the current vuln.

        Returns:
            dict[int, MSRemed]: A dictionary of MSRemed instances
        """

        return self._kbs

    @property
    def impacted_products(self) -> dict[str, "CVRFProduct"]:
        """
        Return the products impacted by the current vuln.

        Returns:
            dict[str, CVRFProduct]: A dictionary of CVRFProduct instances
        """

        return self._products

    def add_kb(self, kb_num: int, kb: "CVRFRemed") -> None:
        """
        Add a KB to vuln KB list.

        Args:
            kb_num (int): The number of the knowledge base article related to the vulnerability.
            kb (MSRemed): The remediation data for the given KB number.

        Raises:
            ValueError: If the provided KB number does not match the expected regex pattern.
        """

        if re.match(KB_NUM_REGEX, str(kb_num)) or re.match(r"(\w+)$", str(kb_num)):
            self._kbs[kb_num] = kb

    def to_flat_dict(self) -> "DataType":
        """
        Convert kbs into dictionaries.

        Returns:
            DataType: A list of flattened dictionaries, each representing a KB and its related CVE.
        """

        kb_dictionaries: "DataType" = []
        for k in self._kbs.values():
            kb_dictionaries.extend(k.to_flat_dict())

        return [{"cve": self.cve, **kb_dict} for kb_dict in kb_dictionaries]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert current vuln into a dict.

        Returns:
            dict[str, Any]: A dictionary representation of the MSVuln object containing CVE and its associated KBs.
        """

        return {
            "cve": self.cve,
            "kbs": list(map(any_to_dict, self._kbs.values())),
        }

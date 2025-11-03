"""A module to handle MS remediations mentionned in a CVRF document."""

import re
from enum import IntEnum

from oudjat.utils import DataType
from oudjat.utils.mappers import any_to_dict
from oudjat.utils.types import DatumType

from .definitions import KB_NUM_REGEX
from .ms_product import MSProduct


class MSRemedType(IntEnum):
    """An enumeration of remediation types."""

    KB = 0
    PATCH = 1


class MSRemed:
    """Class to manipulate MS KBs."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, num: int) -> None:
        """
        Create a new instance of the MSRemed class.

        Args:
            num (int): The number of the Microsoft Knowledge Base article.
        """

        self._number: int = num

        self._type: "MSRemedType" = MSRemedType.KB
        if not re.match(KB_NUM_REGEX, f"{self._number}"):
            self._type = MSRemedType.PATCH

        self._products: dict[str, "MSProduct"] = {}

    # ****************************************************************
    # Methods

    @property
    def products(self) -> dict[str, "MSProduct"]:
        """
        Return the products impacted by this remediation.

        Returns:
            dict[str, MSProduct]: dictionary of products
        """

        return self._products

    def set_products_from_list(self, products: list["MSProduct"]) -> None:
        """
        Setter for kb products.

        Args:
            products (List[MSProduct]): A list of MSProduct instances to be added or updated in the KB's product dictionary.

        Updates:
            self.products (Dict[str, MSProduct]): Adds or updates entries in the product dictionary with the provided products, ensuring no duplicates based on product ID.
        """

        self._products = {p.pid: p for p in products if p.pid not in self._products.keys()}

    @property
    def number(self) -> int:
        """
        Getter for kb number.

        Returns:
            int: The number of the KB article.
        """

        return self._number

    def to_flat_dict(self) -> "DataType":
        """
        Convert patched products into dictionaries.

        Returns:
            List[Dict]: A list of dictionaries where each dictionary contains the remed number, type, and product details flattened from the MSProduct instances.
        """

        return [
            {"remed": self._number, "remed_type": self._type, **p.to_dict()}
            for p in self._products.values()
        ]

    def to_dict(self) -> "DatumType":
        """
        Convert the current kb into a dict.

        Returns:
            Dict[str, Any]: A dictionary containing the remed number and a list of dictionaries representing the patched products, each converted from their MSProduct instances using `to_dict`.
        """

        return {
            "remed": self._number,
            "patched_products": list(map(any_to_dict, self._products.values())),
        }

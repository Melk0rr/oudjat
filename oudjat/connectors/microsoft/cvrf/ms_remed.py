"""A module to handle MS remediations mentionned in a CVRF document."""

import re
from enum import IntEnum
from typing import Any

from oudjat.utils.mappers import any_to_dict

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

    def __init__(self, num: int):
        """
        Create a new instance of the MSRemed class.

        Args:
            num (int): The number of the Microsoft Knowledge Base article.
        """

        self._number: int = num

        self.type: MSRemedType = MSRemedType.KB
        if not re.match(KB_NUM_REGEX, f"{self._number}"):
            self.type = MSRemedType.PATCH

        self.products: dict[str, MSProduct] = {}

    # ****************************************************************
    # Methods

    def set_products(self, products: list[MSProduct]) -> None:
        """
        Setter for kb products.

        Args:
            products (List[MSProduct]): A list of MSProduct instances to be added or updated in the KB's product dictionary.

        Updates:
            self.products (Dict[str, MSProduct]): Adds or updates entries in the product dictionary with the provided products, ensuring no duplicates based on product ID.
        """

        self.products = {p.get_id(): p for p in products if p.get_id() not in self.products.keys()}

    def get_number(self) -> int:
        """
        Getter for kb number.

        Returns:
            int: The number of the KB article.
        """

        return self.number

    def to_flat_dict(self) -> list[dict[str, Any]]:
        """
        Convert patched products into dictionaries.

        Returns:
            List[Dict]: A list of dictionaries where each dictionary contains the remed number, type, and product details flattened from the MSProduct instances.
        """

        return [
            {"remed": self.number, "remed_type": self.type, **p.to_dict()}
            for p in self.products.values()
        ]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current kb into a dict.

        Returns:
            Dict[str, Any]: A dictionary containing the remed number and a list of dictionaries representing the patched products, each converted from their MSProduct instances using `to_dict`.
        """

        return {
            "remed": self.number,
            "patched_products": list(map(any_to_dict, self.products.values())),
        }

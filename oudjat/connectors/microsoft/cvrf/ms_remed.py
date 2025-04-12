import re
from enum import Enum
from typing import Any, Dict, List

from oudjat.utils.mappers import any_to_dict

from .definitions import KB_NUM_REGEX
from .ms_product import MSProduct


class MSRemedType(Enum):
    """
    An enumeration of remediation types
    """

    KB = "KB"
    PATCH = "Patch"


class MSRemed:
    """Class to manipulate MS KBs"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, num: int):
        """
        Constructor for the MSRemed class.

        Args:
            num (int): The number of the Microsoft Knowledge Base article.
        """

        self.number = num

        self.type: MSRemedType = MSRemedType.KB
        if not re.match(KB_NUM_REGEX, self.number):
            self.type = MSRemedType.PATCH

        self.products: Dict[str, MSProduct] = {}

    # ****************************************************************
    # Methods

    def set_products(self, products: List[MSProduct]) -> None:
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

    def to_flat_dict(self) -> List[Dict]:
        """
        Converts patched products into dictionaries.

        Returns:
            List[Dict]: A list of dictionaries where each dictionary contains the remed number, type, and product details flattened from the MSProduct instances.
        """

        return [
            {"remed": self.number, "remed_type": self.type, **p.to_dict()}
            for p in self.products.values()
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the current kb into a dict.

        Returns:
            Dict[str, Any]: A dictionary containing the remed number and a list of dictionaries representing the patched products, each converted from their MSProduct instances using `to_dict`.
        """

        return {
            "remed": self.number,
            "patched_products": list(map(any_to_dict, self.products.values())),
        }

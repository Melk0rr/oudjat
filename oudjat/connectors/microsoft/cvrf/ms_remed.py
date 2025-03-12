import re
from typing import Any, Dict, List

from . import KB_NUM_REGEX, MSProduct


class MSRemed:
    """Class to manipulate MS KBs"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, num: int):
        """Constructor"""
        self.number = num

        self.type = "KB"
        if not re.match(KB_NUM_REGEX, self.number):
            self.type = "Patch"

        self.products = {}

    # ****************************************************************
    # Methods

    def set_products(self, products: List[MSProduct]) -> None:
        """Setter for kb products"""
        self.products = {p.get_id(): p for p in products if p.get_id() not in self.products.keys()}

    def get_number(self) -> int:
        """Getter for kb number"""
        return self.number

    def to_flat_dict(self) -> List[Dict]:
        """Converts patched products into dictionaries"""
        return [
            {"remed": self.number, "remed_type": self.type, **p.to_dict()}
            for p in self.products.values()
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Converts the current kb into a dict"""
        return {
            "remed": self.number,
            "patched_products": [p.to_dict() for p in self.products.values()],
        }


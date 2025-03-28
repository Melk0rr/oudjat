import re
from typing import Dict

from .definitions import MS_PRODUCT_REGEX


class MSProduct:
    """Class to manipulate MS product"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, pid: str, name: str, product_type: str):
        """Constructor"""

        if not re.match(MS_PRODUCT_REGEX, pid):
            raise ValueError(f"Invalid MS product ID: {pid}")

        self.pid = pid
        self.name = name
        self.type = product_type
        self.sub_type = self.type

        if self.type == "ESU" or self.type == "Windows":
            self.sub_type = "Workstation"

            if "Server" in self.name:
                self.sub_type = "Server"

    # ****************************************************************
    # Methods

    def get_id(self) -> str:
        """Getter for product id"""
        return self.pid

    def get_name(self) -> str:
        """Getter for product name"""
        return self.name

    def __str__(self) -> str:
        """Converts instance to string"""
        return f"{self.pid}: {self.name}"

    def to_dict(self) -> Dict[str, str]:
        """Converts instance to dict"""
        return {
            "product_id": self.pid,
            "product_name": self.name,
            "product_type": self.type,
            "product_subtype": self.sub_type,
        }


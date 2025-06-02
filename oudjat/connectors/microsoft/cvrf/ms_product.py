"""A module that handles MS products concerned by one or more vulnerabilities."""

import re
from typing import Dict

from .definitions import MS_PRODUCT_REGEX


class MSProduct:
    """Class to manipulate MS product."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, pid: str, name: str, product_type: str) -> None:
        """
        Create a new instance of the MSProduct.

        Args:
            pid (str)         : The unique identifier of the product.
            name (str)        : The name of the product.
            product_type (str): The type of the product.

        Raises:
            ValueError: If the provided product ID does not match the MS_PRODUCT_REGEX pattern.
        """

        if not re.match(MS_PRODUCT_REGEX, pid):
            raise ValueError(f"{__class__.__name__}::Invalid MS product ID: {pid}")

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
        """
        Getter for product id.

        Returns:
            str: The unique identifier of the product.
        """

        return self.pid

    def get_name(self) -> str:
        """
        Getter for product name.

        Returns:
            str: The name of the product.
        """

        return self.name

    def __str__(self) -> str:
        """
        Convert instance to string.

        Returns:
            str: A string representation of the product in the format "pid: name".
        """

        return f"{self.pid}: {self.name}"

    def to_dict(self) -> Dict[str, str]:
        """
        Convert instance to dict.

        Returns:
            Dict[str, str]: A dictionary representation of the product with keys "product_id", "product_name", "product_type", and "product_subtype".
        """

        return {
            "product_id": self.pid,
            "product_name": self.name,
            "product_type": self.type,
            "product_subtype": self.sub_type,
        }

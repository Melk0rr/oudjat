"""A module that handles MS products concerned by one or more vulnerabilities."""

import re
from typing import override

from oudjat.utils import Context

from .definitions import CVRF_PRODUCT_REGEX
from .exceptions import InvalidCVRFProductError


class CVRFProduct:
    """Class to manipulate MS product."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, pid: str, name: str, product_type: str) -> None:
        """
        Create a new instance of the CVRFProduct.

        Args:
            pid (str)         : The unique identifier of the product.
            name (str)        : The name of the product.
            product_type (str): The type of the product.

        Raises:
            ValueError: If the provided product ID does not match the MS_PRODUCT_REGEX pattern.
        """

        if not re.match(CVRF_PRODUCT_REGEX, pid):
            raise InvalidCVRFProductError(f"{Context()}::Invalid MS product ID: {pid}")

        self._pid: str = pid
        self._name: str = name
        self._type: str = product_type
        self._sub_type: str = self._type

        if self._type == "ESU" or self._type == "Windows":
            self._sub_type = "Workstation"

            if "Server" in self._name:
                self._sub_type = "Server"

    # ****************************************************************
    # Methods

    @property
    def pid(self) -> str:
        """
        Getter for product id.

        Returns:
            str: The unique identifier of the product.
        """

        return self._pid

    @property
    def name(self) -> str:
        """
        Getter for product name.

        Returns:
            str: The name of the product.
        """

        return self._name

    @override
    def __str__(self) -> str:
        """
        Convert instance to string.

        Returns:
            str: A string representation of the product in the format "pid: name".
        """

        return f"{self._pid}: {self._name}"

    def to_dict(self) -> dict[str, str]:
        """
        Convert instance to dict.

        Returns:
            dict[str, str]: A dictionary representation of the product
        """

        return {
            "productId": self._pid,
            "productName": self._name,
            "productType": self._type,
            "productSubtype": self._sub_type,
        }

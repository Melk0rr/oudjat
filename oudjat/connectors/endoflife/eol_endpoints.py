
from enum import Enum
from typing import override


class EndOfLifeEndpoint(Enum):
    """
    A helper enumeration of the endoflife.date API endpoints.
    """

    PRODUCTS = "products"
    CATEGORIES = "categories"
    TAGS = "tags"

    @override
    def __str__(self) -> str:
        """
        Convert an endoflife endpoint into a string.

        Returns:
            str: A string representation of the endpoint
        """

        return self._value_

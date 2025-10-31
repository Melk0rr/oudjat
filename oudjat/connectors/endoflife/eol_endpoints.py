
from enum import Enum


class EndOfLifeEndpoint(Enum):
    """
    A helper enumeration of the endoflife.date API endpoints.
    """

    PRODUCTS = "products"
    CATEGORIES = "categories"
    TAGS = "tags"

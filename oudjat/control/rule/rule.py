from typing import Dict, List, Union

from oudjat.control.data import DataFilter
from oudjat.control.risk import Risk


class Rule:
    """A class to describes rules"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        associatedRisks: List[Risk] = None,
        filters: Union[List[DataFilter], List[Dict]] = None,
    ):
        """Constructor"""
        self.id = id
        self.name = name
        self.description = description

    # ****************************************************************
    # Methods

    # ****************************************************************
    # Static methods

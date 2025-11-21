"""A module that describes the notion of software edition."""

import re
from typing import Any, NamedTuple, override


class SoftwareEdition(NamedTuple):
    """
    A class to handle software editions.

    A software often comes in different editions and with it, different releases, support, etc.
    """

    label: str
    category: str | None
    pattern: str | None

    def match_str(self, test_str: str) -> bool:
        """
        Check if provided string matches edition pattern.

        Args:
            test_str (str): The string to be matched against the edition pattern.

        Returns:
            bool: True if the string matches the pattern or if no pattern is set, False otherwise.
        """

        if self.pattern is None:
            return False

        return re.search(self.pattern, test_str) is not None

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string representation.

        Returns:
            str: The label of the software edition as its string representation.
        """

        return self.label

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current object into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the current object
        """

        return {
            "label": self.label,
            "category": self.category,
            "pattern": self.pattern,
        }


class SoftwareEditionDict(dict):
    """
    A dictionary-like class to handle multiple software editions.
    """

    @property
    def labels(self) -> list[str]:
        """
        Return a list of edition labels.

        Returns:
            list[str]: A list of the labels of all software editions in the dictionary.
        """

        return list(map(str, self.values()))

    def find_by_label(self, label: str) -> list["SoftwareEdition"]:
        """
        Return software editions for which the given label matches the pattern.

        Args:
            label (str): The label to match against the edition patterns.

        Returns:
            list[SoftwareEdition]: A list of SoftwareEdition instances that match the given label.
        """

        def filter_values(edition: "SoftwareEdition") -> bool:
            return edition.match_str(label)

        return list(filter(filter_values, self.values()))

    def filter_by_category(self, category: str | list[str]) -> "SoftwareEditionDict":
        """
        Filter the current dictionary based on provided category.

        Return a new software edition dictionary with only editions matching the provided category

        Args:
            category (str | list[str]): category of the final editions

        Returns:
            SoftwareEditionDict: new software edition dictionary that contains only editions with the provided category
        """

        return SoftwareEditionDict(
            **{edi_k: edi for edi_k, edi in self.items() if edi.category in category}
        )

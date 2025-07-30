"""A module that describes the notion of software edition."""

import re
from typing import override


class SoftwareEdition:
    """
    A class to handle software editions.

    A software often comes in different editions and with it, different releases, support, etc.
    """

    def __init__(self, label: str, category: str | None = None, pattern: str | None = None) -> None:
        """
        Create a new SoftwareEdition.

        Args:
            label (str)             : The name or identifier of the software edition.
            category (str, optional): The category that the software edition belongs to. Defaults to None.
            pattern (str, optional) : A regex pattern used for matching strings against this edition. Defaults to None.
        """

        self.label: str = label
        self.category: str | None = category
        self.pattern: str | None = pattern

    def get_label(self) -> str:
        """
        Getter for edition label.

        Returns:
            str: The label of the software edition.
        """

        return self.label

    def get_category(self) -> str | None:
        """
        Getter for edition category.

        Returns:
            str: The category of the software edition.
        """

        return self.category

    def get_pattern(self) -> str | None:
        """
        Getter for edition pattern.

        Returns:
            str: The regex pattern used for matching strings against this edition.
        """

        return self.pattern

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


class SoftwareEditionDict(dict):
    """
    A dictionary-like class to handle multiple software editions.
    """

    def get_matching_editions(self, label: str) -> list[SoftwareEdition]:
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

    def get_edition_labels(self) -> list[str]:
        """
        Return a list of edition labels.

        Returns:
            list[str]: A list of the labels of all software editions in the dictionary.
        """

        return list(map(str, self.values()))

    def get_editions_per_ctg(self, category: str) -> list[str]:
        """
        Return a sub-dictionary of software editions based on category value.

        Args:
            category (str): The category to filter the software editions by.

        Returns:
            SoftwareEditionDict: A dictionary containing only the SoftwareEdition instances that belong to the specified category.
        """

        def filter_values(edition: "SoftwareEdition") -> bool:
            return edition.get_category() == category

        return list(map(str, filter(filter_values, self.values())))


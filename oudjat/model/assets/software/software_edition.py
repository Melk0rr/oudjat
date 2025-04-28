import re
from typing import List


class SoftwareEdition:
    """
    A class to handle software editions.

    A software often comes in different editions and with it, different releases, support, etc.
    """

    def __init__(self, label: str, category: str = None, pattern: str = None):
        """
        Constructor for SoftwareEdition class.

        Args:
            label (str): The name or identifier of the software edition.
            category (str, optional): The category that the software edition belongs to. Defaults to None.
            pattern (str, optional): A regex pattern used for matching strings against this edition. Defaults to None.
        """

        self.label = label
        self.category = category
        self.pattern = pattern

    def get_label(self) -> str:
        """
        Getter for edition label.

        Returns:
            str: The label of the software edition.
        """

        return self.label

    def get_category(self) -> str:
        """
        Getter for edition category.

        Returns:
            str: The category of the software edition.
        """

        return self.category

    def get_pattern(self) -> str:
        """
        Getter for edition pattern.

        Returns:
            str: The regex pattern used for matching strings against this edition.
        """

        return self.pattern

    def match_str(self, test_str: str) -> bool:
        """
        Checks if provided string matches edition pattern.

        Args:
            test_str (str): The string to be matched against the edition pattern.

        Returns:
            bool: True if the string matches the pattern or if no pattern is set, False otherwise.
        """

        return self.pattern is None or re.search(self.pattern, test_str)

    def __str__(self) -> str:
        """
        Converts the current instance into a string representation.

        Returns:
            str: The label of the software edition as its string representation.
        """

        return self.label


class SoftwareEditionDict(dict):
    """
    A dictionary-like class to handle multiple software editions.
    """

    def get_matching_editions(self, label: str) -> List[SoftwareEdition]:
        """
        Returns software editions for which the given label matches the pattern.

        Args:
            label (str): The label to match against the edition patterns.

        Returns:
            List[SoftwareEdition]: A list of SoftwareEdition instances that match the given label.
        """


        def filter_values(edition: "SoftwareEdition") -> bool:
            return edition.match_str(label)

        return list(filter(filter_values, self.values()))

    def get_edition_labels(self) -> List[str]:
        """
        Returns a list of edition labels.

        Returns:
            List[str]: A list of the labels of all software editions in the dictionary.
        """

        return map(str, self.values())

    def get_editions_per_ctg(self, category: str) -> "SoftwareEditionDict":
        """
        Returns a sub-dictionary of software editions based on category value.

        Args:
            category (str): The category to filter the software editions by.

        Returns:
            SoftwareEditionDict: A dictionary containing only the SoftwareEdition instances that belong to the specified category.
        """

        def filter_values(edition: "SoftwareEdition") -> bool:
            return edition.get_category() == category

        return list(map(str, filter(filter_values, self.values())))

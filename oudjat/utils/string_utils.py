"""
A module that provides string utilities.
"""

import re


class StringUtils:
    """
    A utility class that provides some useful string transformations.
    """

    # ****************************************************************
    # Static methods

    @staticmethod
    def camelize(s: str) -> str:
        """
        Return a camelized version of the provided string.

        Args:
            s (str): The string to camelize

        Returns:
            str: The camelized string

        Example:
            camelize("First Name") -> firstName
        """

        base = re.sub(r"[\W]([a-zA-Z])", lambda x: x[1].upper(), s)
        return f"{base[0].lower()}{base[1:]}"

    @staticmethod
    def jsonify(s: str) -> str:
        """
        Ensure the provided string is a valid json string.

        Args:
            s (str): string to JSONify

        Returns:
            str: Valid JSON string
        """

        return re.sub(r'(\w+)(?=\s*:)', r'"\1"', s)


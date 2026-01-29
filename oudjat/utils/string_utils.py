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

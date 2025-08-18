"""A helper module that brings some list utilities."""

from abc import ABC


class MyList(list, ABC):
    """
    A helper class to provide some qol methods to lists.
    """

    def is_empty(self) -> bool:
        """
        Return wheither or not the list is empty.

        Returns:
            bool: True if the list is empty. False otherwise.
        """

        return len(self) == 0

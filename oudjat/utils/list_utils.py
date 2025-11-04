"""A helper module that brings some list utilities."""

from typing import Any


class UtilsList(list):
    """
    A helper class to provide some qol methods to lists.
    """

    # ****************************************************************
    # Methods

    def is_empty(self) -> bool:
        """
        Return wheither or not the list is empty.

        Returns:
            bool: True if the list is empty. False otherwise.
        """

        return len(self) == 0


    # ****************************************************************
    # Static methods

    @staticmethod
    def append_flat(append_list: list[Any], new_element: Any | list[Any]) -> None:
        """
        Append a new element into a given list by handling the list nature of the new element.

        If the new element is a list, the base list will extend it.
        If not, the new element will just be appended to the list.

        Args:
            append_list (list[Any])      : The list the new element will be appended to
            new_element (Any | list[Any]): The element to append to the list

        Returns:
            list[Any]: The base list appended with the new element
        """

        if isinstance(new_element, list):
            append_list.extend(new_element)

        else:
            append_list.append(new_element)

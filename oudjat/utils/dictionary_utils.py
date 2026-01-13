"""A module that gather dictionary utilities."""

from typing import Any, Callable


class UtilsDict(dict):
    """Custom overload of the base dictionary."""

    # ****************************************************************
    # Methods

    def join_items(self, char: str) -> str:
        """
        Join dictionary items with the provided character.

        Args:
            char (str): The character to use for joining the keys and values.

        Returns:
            str: A string where each item in the dictionary is joined by the specified character, formatted as "key: value".

        Example:
            >>> my_custom_dict = CustomDict(**{'a': 1, 'b': 2})
            >>> my_custom_dict.join_items(':')
            'a: 1: b: 2'
        """

        return char.join(f"{k}: {v}" for k, v in self.items())

    def join_values(self, char: str) -> str:
        """
        Join dictionary values with the provided character.

        Args:
            char (str): The character to use for joining the values.

        Returns:
            str: A string where each value in the dictionary is joined by the specified character.

        Example:
            >>> my_custom_dict = CustomDict(**{'a': 1, 'b': 2})
            >>> my_custom_dict.join_values(',')
            '1, 2'
        """

        return char.join(map(str, self.values()))

    # ****************************************************************
    # Static methods

    @staticmethod
    def join_dictionary_items(dictionary: dict[str, Any], char: str) -> str:
        """
        Join dictionary items with the provided character.

        Args:
            dictionary (dict[str, Any]): The input dictionary containing key-value pairs.
            char (str)                 : The character to use for joining the keys and values.

        Returns:
            str: A string where each item in the dictionary is joined by the specified character, formatted as "key: value".

        Example:
            >>> join_dictionary_items({'a': 1, 'b': 2}, ':')
            'a: 1: b: 2'
        """

        return char.join(f"{k}: {v}" for k, v in dictionary.items())

    @staticmethod
    def join_dictionary_values(dictionary: dict[str, Any], char: str) -> str:
        """
        Join dictionary values with the provided character.

        Args:
            dictionary (dict[str, Any]): The input dictionary containing key-value pairs.
            char (str)                 : The character to use for joining the values.

        Returns:
            str: A string where each value in the dictionary is joined by the specified character.

        Example:
            >>> join_dictionary_values({'a': 1, 'b': 2}, ',')
            '1, 2'
        """

        return char.join(map(str, dictionary.values()))

    @staticmethod
    def map_list_to_dict(
        list_to_map: list[dict[str, Any]],
        key: str,
        key_callback: Callable[[str], str] | None = None,
    ) -> dict[Any, dict[str, Any]]:
        """
        Map a list into a dictionary using the provided key.

        Args:
            list_to_map (list[dict[str, Any]]) : The input list of dictionaries or objects that have the specified key.
            key (str)                          : The key to use for mapping values in the list to a new dictionary.
            key_callback (Callable[[str], str]): Optional callback to transform the key

        Returns:
            dict[Any, dict[str, Any]]: A dictionary where each element in the list is mapped by the specified key as the key and the entire element as the value.

        Example:
            >>> map_list_to_dict([{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}], 'id')
            {1: {'id': 1, 'name': 'Alice'}, 2: {'id': 2, 'name': 'Bob'}}
        """

        return {(key_callback(el[key]) if key_callback else el[key]): el for el in list_to_map}

    @staticmethod
    def from_tuple(
        input_tuple: tuple[str], parent: tuple[str], res: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Convert a nested tuple into a dictionary recursively.

        Args:
            input_tuple (tuple[str]): The input tuple to be converted into a dictionary.
            parent (tuple[str])     : The parent tuple from which the current element is taken.
            res (dict[str, Any])    : A dictionary to store intermediate results. Defaults to an empty dictionary.

        Returns:
            dict[str, Any]: A nested dictionary where each key-value pair represents an element and its corresponding parent index.
        """

        if res is None:
            res = {}

        for el in input_tuple:
            if isinstance(el, tuple):
                return UtilsDict.from_tuple(el, input_tuple, res)
            else:
                # Assuming that the first element of each sub-tuple is the key and the second is the value
                res[el] = parent[0][1]

        return res

    @staticmethod
    def merge_dictionaries(d1: dict[str, Any], d2: dict[str, Any]) -> dict[str, Any]:
        """
        Merge two dictionaries.

        Args:
            d1 (dict[str, Any]): The initial dictionary
            d2 (dict[str, Any]): The dictionary to merge

        Returns:
            dict[str, Any]: Merged custom attributes dictionary
        """

        for k, v in d2:
            if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
                return UtilsDict.merge_dictionaries(d1[k], v)

            else:
                d1[k] = v

        return d1

    @staticmethod
    def flatten_dict(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
        """
        Flatten a given dictionary based on the provided separator.

        The method joins the sub dictionaries keys like this
        <parent_key><separator><key>

        The method joins the sub lists elements like this
        <parent_key><separator><index>

        Args:
            d (dict[str, Any]): The dictionary to flatten
            parent_key (str)  : The parent key to prepend to the new key
            sep (str)         : The separator to join the parent key and the current key

        Returns:
            dict[str, Any]: Flattened dictionary
        """

        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(UtilsDict.flatten_dict(v, new_key, sep).items())

            elif isinstance(v, list):
                for i, el in enumerate(v):
                    list_key = f"{new_key}{sep}{i}"
                    if isinstance(el, dict):
                        items.extend(UtilsDict.flatten_dict(el, list_key, sep).items())

                    else:
                        items.append((list_key, el))

            else:
                items.append((new_key, v))

        return dict(items)

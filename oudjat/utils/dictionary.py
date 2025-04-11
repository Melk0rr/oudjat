# INFO: Helper functions to play with dictionaries

from typing import Dict, List


def join_dictionary_items(dictionary: Dict, char: str) -> str:
    """
    Join dictionary items with the provided character.

    Args:
        dictionary (Dict): The input dictionary containing key-value pairs.
        char (str): The character to use for joining the keys and values.

    Returns:
        str: A string where each item in the dictionary is joined by the specified character, formatted as "key: value".

    Example:
        >>> join_dictionary_items({'a': 1, 'b': 2}, ':')
        'a: 1: b: 2'
    """

    return char.join(f"{k}: {v}" for k, v in dictionary.items())


def join_dictionary_values(dictionary: Dict, char: str) -> str:
    """
    Join dictionary values with the provided character.

    Args:
        dictionary (Dict): The input dictionary containing key-value pairs.
        char (str): The character to use for joining the values.

    Returns:
        str: A string where each value in the dictionary is joined by the specified character.

    Example:
        >>> join_dictionary_values({'a': 1, 'b': 2}, ',')
        '1, 2'
    """

    return char.join(f"{v}" for v in dictionary.values())


def map_list_to_dict(list_to_map: List, key: str) -> Dict:
    """
    Maps a list into a dictionary using the provided key.

    Args:
        list_to_map (List): The input list of dictionaries or objects that have the specified key.
        key (str)         : The key to use for mapping values in the list to a new dictionary.

    Returns:
        Dict: A dictionary where each element in the list is mapped by the specified key as the key and the entire element as the value.

    Example:
        >>> map_list_to_dict([{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}], 'id')
        {1: {'id': 1, 'name': 'Alice'}, 2: {'id': 2, 'name': 'Bob'}}
    """

    return {el[key]: el for el in list_to_map}

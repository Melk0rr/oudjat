from typing import Any, Dict


def any_to_dict(element: Any) -> Dict:
    """
    Calls the to_dict method on the provided element

    Args:
        element (Any) : element to convert into a dict using 'to_dict' method

    Returns:
        Dict : element converted into a dictionary
    """

    if not hasattr(element, "to_dict"):
        raise ValueError("any_to_dict::You must provide an element that has a 'to_dict' method")

    return element.to_dict()

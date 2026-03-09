"""
Some enumeration utilities.
"""

from enum import Enum
from typing import Callable, TypeVar, cast

E = TypeVar("E", bound="Enum")

def combine_enums(name: str, *enums: type["E"], base: type["E"] = Enum) -> type["E"]:
    """
    Combine multiple enums into a single one based on a provided base.

    Args:
        name (str)         : The name of the new enum
        *enums (type[Enum]): Enums to combine
        base (type[Enum])  : The base enum for behavior

    Returns:
        type[Enum]: New combined enum
    """

    members = {}
    for enum_cls in enums:
        members.update({m.name: m.value for m in enum_cls})

    return cast(type["E"], base(name, members))


def extend_enum(parent: type["E"], base: type["E"] = Enum) -> Callable[[type["E"]], type["E"]]:
    """
    Provide a function to extend the provided base enumeration with another one.

    Args:
        parent (type[E]): The base enumeration to extend
        base (type[E])  : The base enum type to wrap the extended enumeration

    Returns:
        Callable[[type[E]], type[E]]: A wrapper function that merges the base enumeration with another one
    """

    def wrapper(extended: type["E"]) -> type["E"]:
        members = {m.name: m.value for m in (*parent, *extended)}
        return cast(type["E"], base(extended.__name__, members))

    return wrapper

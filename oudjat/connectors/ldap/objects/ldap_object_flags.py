"""
A simple module to enumerate some LDAP object flags.
"""

from enum import Enum
from typing import Any, Callable, TypeAlias

from .ldap_object import LDAPObject

LDAPFlagValue: TypeAlias = tuple[Callable[..., bool]] | tuple[Callable[..., bool], Any]

class LDAPObjectFlag(Enum):
    """Specific flags for ldap objects."""

    def __call__(self, obj: "LDAPObject") -> bool:
        """
        Call the check function.

        Args:
            obj (LDAPObject): Passed object to run the check on

        Returns:
            bool: True if the check passed. False otherwise
        """

        fn = self._value_
        args = []
        if len(fn) > 1:
            fn, args = self._value_

        return fn(obj, *args)

    @classmethod
    def flags(cls, obj: "LDAPObject") -> list[str]:
        """
        Return matching flags for the provided object.

        Args:
            obj (LDAPObject): The object to check against the flags

        Returns:
            list[str]: A list of flag names that match the provided object
        """

        return [ flag._name_ for flag in cls if flag(obj) ]


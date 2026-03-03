"""
A simple module to enumerate some LDAP object flags.
"""

from enum import Enum
from typing import Generic

from .objects.ldap_object import LDAPObjectBoundType


# TODO: Change into an enum of callbacks
class LDAPFlag(Enum, Generic["LDAPObjectBoundType"]):
    """A simple enumeration of some custom flags that may be assigned to LDAP objects."""

    # OLD_PASSWORD = lambda acc: acc.pwd_last_set_in_days >= 180
    # VERY_OLD_PASSWORD = lambda acc: acc.pwd_last_set_in_days >= 1095
    # POTENTIAL_CLEARTXT_PWD = 4
    # WEAK_ENCRYPTION_SUPPORTED = 8
    # IS_ADMIN = 16

    def __call__(self, obj: "LDAPObjectBoundType") -> bool:
        return self._value_(obj)

    @classmethod
    def flags(cls, obj: "LDAPObjectBoundType") -> None:
        for flag in cls:
            if flag(obj):
                obj.flags.add(flag._name_)


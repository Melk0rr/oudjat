"""
A helper module that provides common utilities to LDAP objects.
"""

from typing import TYPE_CHECKING, NamedTuple, TypeVar

from oudjat.utils.types import StrType

if TYPE_CHECKING:
    from .ldap_object import LDAPObject


LDAPObjectBoundType = TypeVar("LDAPObjectBoundType", bound=LDAPObject)

class LDAPObjectTypeProps(NamedTuple):
    """
    A helper class to properly handle LDAPObjectType properties.

    Attributes:
        object_cls (str)                      : the name of the LDAP object class used in and LDAP filter
        filter (str)                          : the LDAP filter used to retrieve objects of this type
        attributes (list[str])                : the object attributes to retrieve
    """

    object_cls: str
    filter: str
    attributes: StrType

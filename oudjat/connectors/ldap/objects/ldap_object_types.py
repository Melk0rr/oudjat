"""A module to list some attributes and infos related to different LDAP object types."""

from enum import Enum
from typing import Any, NamedTuple

from oudjat.utils.types import StrType

from ..ldap_filter import LDAPFilter, LDAPFilterObjectCls, LDAPFilterObjectCtg, LDAPFilterStr


class LDAPObjectTypeProps(NamedTuple):
    """
    A helper class to properly handle LDAPObjectType properties.

    Attributes:
        object_cls (str)      : The name of the LDAP object class used in and LDAP filter
        filter (str)          : The LDAP filter used to retrieve objects of this type
        attributes (list[str]): The object attributes to retrieve
    """

    object_cls: str
    filter: "LDAPFilter"
    attributes: StrType


class LDAPObjectType(Enum):
    """These are the default LDAP search parameters per object type."""

    DEFAULT = LDAPObjectTypeProps(
        object_cls="*", filter=LDAPFilter(LDAPFilterStr.CLS("*")), attributes="*"
    )

    COMPUTER = LDAPObjectTypeProps(
        object_cls="computer",
        filter=LDAPFilter(LDAPFilterStr.CTG(LDAPFilterObjectCtg.COMPUTER.value)),
        attributes=[
            "accountExpires",
            "cn",
            "description",
            "distinguishedName",
            "dNSHostName",
            "ipHostNumber",
            "lastLogonTimestamp",
            "memberOf",
            "name",
            "objectClass",
            "objectGUID",
            "objectSid",
            "operatingSystem",
            "operatingSystemVersion",
            "pwdLastSet",
            "sAMAccountName",
            "userAccountControl",
            "whenChanged",
            "whenCreated",
        ],
    )

    GPO = LDAPObjectTypeProps(
        object_cls="groupPolicyContainer",
        filter=LDAPFilter(LDAPFilterStr.CLS(LDAPFilterObjectCls.GPO.value)),
        attributes=[
            "displayName",
            "gPCFileSysPath",
            "gPCUserExtensionNames",
            "gPCMachineExtensionNames",
            "gPCWQLFilter",
            "name",
            "objectClass",
            "objectGUID",
            "versionNumber",
            "whenChanged",
            "whenCreated",
        ],
    )

    GROUP = LDAPObjectTypeProps(
        object_cls="group",
        filter=LDAPFilter(LDAPFilterStr.CTG(LDAPFilterObjectCtg.GROUP.value)),
        attributes=[
            "cn",
            "description",
            "groupType",
            "member",
            "memberOf",
            "name",
            "objectClass",
            "objectGUID",
            "objectSid",
            "whenChanged",
            "whenCreated",
        ],
    )

    OU = LDAPObjectTypeProps(
        object_cls="organizationalUnit",
        filter=LDAPFilter(LDAPFilterStr.CLS(LDAPFilterObjectCls.OU.value)),
        attributes=[
            "description",
            "gpLink",
            "name",
            "objectClass",
            "objectGUID",
            "objectSid",
            "whenChanged",
            "whenCreated",
        ],
    )

    SUBNET = LDAPObjectTypeProps(
        object_cls="subnet",
        filter=LDAPFilter(LDAPFilterStr.CLS(LDAPFilterObjectCls.SUBNET.value)),
        attributes=[
            "cn",
            "description",
            "distinguishedName",
            "location",
            "name",
            "objectGUID",
            "whenChanged",
            "whenCreated",
        ],
    )

    USER = LDAPObjectTypeProps(
        object_cls="user",
        filter=(
            LDAPFilter(LDAPFilterStr.CTG(LDAPFilterObjectCtg.PERSON.value))
            & LDAPFilter(LDAPFilterStr.CLS(LDAPFilterObjectCls.USER.value))
        ),
        attributes=[
            "accountExpires",
            "adminCount",
            "cn",
            "description",
            "distinguishedName",
            "employeeID",
            "givenName",
            "lastLogonTimestamp",
            "mail",
            "manager",
            "memberOf",
            "msDS-User-Account-Control-Computed",
            "msExchRecipientTypeDetails",
            "name",
            "objectClass",
            "objectGUID",
            "objectSid",
            "pwdLastSet",
            "sn",
            "sAMAccountName",
            "title",
            "userAccountControl",
            "userPrincipalName",
            "whenChanged",
            "whenCreated",
        ],
    )

    # ****************************************************************
    # Attributes

    @property
    def object_cls(self) -> str:
        """
        Return the objectClass property of an LDAPObjectType. This function is used to make LDAP queries.

        Returns:
            str: the LDAP object class tide to this type
        """

        return self._value_.object_cls

    @property
    def filter(self) -> "LDAPFilter":
        """
        Return the filter property of an LDAPObjectType. This property is used to make LDAP queries.

        Returns:
            str: LDAP filter matching this type
        """

        return self._value_.filter

    @property
    def attributes(self) -> StrType:
        """
        Return the attributes property of an LDAPObjectType.

        Returns:
            list[str]: a list of attributes to include in the results when searching for this type
        """

        return self._value_.attributes

    # ****************************************************************
    # Static methods

    @staticmethod
    def from_object_cls(entry: dict[str, Any]) -> "LDAPObjectType":
        """
        Return an LDAPObjectType based on a given LDAP entry.

        Args:
            entry (dict[str, Any]): LDAP entry the LDAPObjectType will be deduced from

        Returns:
            LDAPObjectType: object type that corresponds to the provided LDAP entry
        """

        def object_cls_is(object_type: "LDAPObjectType") -> bool:
            return object_type.object_cls == entry.get("attributes", {}).get("objectClass", [])[-1]

        return next(filter(object_cls_is, LDAPObjectType))

    @staticmethod
    def resolve_entry_cls(entry: dict[str, Any]) -> str:
        """
        Determine the object class of an LDAP entry based on its "objectClass" attribute.

        Args:
            entry (dict[str, Any]): LDAP entry the LDAPObjectType will be deduced from

        Returns:
            str: The name of the object class, or None if no matching class is found.
        """

        entry_obj_cls: list[str] = entry.get("attributes", {}).get("objectClass", [])

        return next(
            (t.name for t in LDAPObjectType if entry_obj_cls and entry_obj_cls[-1] == t.object_cls),
            "*",
        )

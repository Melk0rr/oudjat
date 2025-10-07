"""A module to list some attributes and infos related to different LDAP object types."""

from enum import Enum
from typing import NamedTuple

from oudjat.utils.types import StrType

from .account.group.ldap_group import LDAPGroup
from .account.ldap_computer import LDAPComputer
from .account.ldap_user import LDAPUser
from .gpo.ldap_gpo import LDAPGroupPolicyObject
from .ldap_object import LDAPObject
from .ou.ldap_ou import LDAPOrganizationalUnit
from .subnet.ldap_subnet import LDAPSubnet


class LDAPObjectTypeProps(NamedTuple):
    """
    A helper class to properly handle LDAPObjectType properties.

    Attributes:
        python_cls (type[LDAPObject]): the class associated with an LDAPObjectType
        object_cls (str)             : the name of the LDAP object class used in and LDAP filter
        filter (str)                 : the LDAP filter used to retrieve objects of this type
        attributes (list[str])       : the object attributes to retrieve
    """

    python_cls: type[LDAPObject]
    object_cls: str
    filter: str
    attributes: StrType


class LDAPObjectType(Enum):
    """These are the default LDAP search parameters per object type."""

    DEFAULT = LDAPObjectTypeProps(
        python_cls=LDAPObject, object_cls="*", filter="(objectClass=*)", attributes="*"
    )

    COMPUTER = LDAPObjectTypeProps(
        python_cls=LDAPComputer,
        object_cls="computer",
        filter="(objectClass=computer)",
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
        python_cls=LDAPGroupPolicyObject,
        object_cls="groupPolicyContainer",
        filter="(objectClass=groupPolicyContainer)",
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
        python_cls=LDAPGroup,
        object_cls="group",
        filter="(objectClass=group)",
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
        python_cls=LDAPOrganizationalUnit,
        object_cls="organizationalUnit",
        filter="(objectClass=organizationalUnit)",
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
        python_cls=LDAPSubnet,
        object_cls="subnet",
        filter="(objectClass=subnet)",
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
        python_cls=LDAPUser,
        object_cls="user",
        filter="(&(objectClass=user)(!(objectClass=computer)))",
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
    def python_cls(self) -> type[LDAPObject]:
        """
        Return the pythonClass property of an LDAPObjectType.

        This property is used to dynamically instanciate any class that inherits from LDAPObject.

        Returns:
            LDAPObject: an LDAPObject inheriting class
        """

        return self._value_.python_cls

    @property
    def object_cls(self) -> str:
        """
        Return the objectClass property of an LDAPObjectType. This function is used to make LDAP queries.

        Returns:
            str: the LDAP object class tide to this type
        """

        return self._value_.object_cls

    @property
    def filter(self) -> str:
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
            List[atr]: a list of attributes to include in the results when searching for this type
        """

        return self._value_.attributes

    # ****************************************************************
    # Static methods

    @staticmethod
    def from_object_cls(object_cls: str) -> "LDAPObjectType":
        """
        Return an LDAPObjectType based on a given python class name.

        Args:
            object_cls (str): python LDAP class name of an object type

        Returns:
            LDAPObjectType: object type that corresponds to the provided object class, if any
        """

        def object_cls_is(object_type: LDAPObjectType) -> bool:
            return object_type.object_cls == object_cls

        return next(filter(object_cls_is, LDAPObjectType))

    @staticmethod
    def get_ldap_class(object_type: str) -> type[LDAPObject]:
        """
        Return an LDAPObject derivated class matching the provided type.

        Args:
            object_type (str): object type to search

        Returns:
            LDAPObject: LDAPObject derivated class
        """

        return LDAPObjectType[object_type.upper()].python_cls

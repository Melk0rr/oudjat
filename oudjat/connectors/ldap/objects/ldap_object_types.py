from enum import Enum
from typing import List

from .account.group.ldap_group import LDAPGroup
from .account.ldap_computer import LDAPComputer
from .account.ldap_user import LDAPUser
from .gpo.ldap_gpo import LDAPGroupPolicyObject
from .ldap_object import LDAPObject
from .ou.ldap_ou import LDAPOrganizationalUnit
from .subnet.ldap_subnet import LDAPSubnet


class LDAPObjectType(Enum):
    """These are the default LDAP search parameters per object type"""

    DEFAULT = {"objectClass": "*", "filter": "(objectClass=*)", "attributes": "*"}

    COMPUTER = {
        "pythonClass": LDAPComputer,
        "objectClass": "computer",
        "filter": "(objectClass=computer)",
        "attributes": [
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
    }

    GPO = {
        "pythonClass": LDAPGroupPolicyObject,
        "objectClass": "groupPolicyContainer",
        "filter": "(objectClass=groupPolicyContainer)",
        "attributes": [
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
    }

    GROUP = {
        "pythonClass": LDAPGroup,
        "objectClass": "group",
        "filter": "(objectClass=group)",
        "attributes": [
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
    }

    OU = {
        "pythonClass": LDAPOrganizationalUnit,
        "objectClass": "organizationalUnit",
        "filter": "(objectClass=organizationalUnit)",
        "attributes": [
            "description",
            "gpLink",
            "name",
            "objectClass",
            "objectGUID",
            "objectSid",
            "whenChanged",
            "whenCreated",
        ],
    }

    SUBNET = {
        "pythonClass": LDAPSubnet,
        "objectClass": "subnet",
        "filter": "(objectClass=subnet)",
        "attributes": [
            "cn",
            "description",
            "distinguishedName",
            "location",
            "name",
            "objectGUID",
            "whenChanged",
            "whenCreated",
        ],
    }

    USER = {
        "pythonClass": LDAPUser,
        "objectClass": "user",
        "filter": "(&(objectClass=user)(!(objectClass=computer)))",
        "attributes": [
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
    }

    # ****************************************************************
    # Attributes

    @property
    def python_cls(self) -> "LDAPObject":
        """
        Returns the pythonClass property of an LDAPObjectType
        This property is used to dynamically instanciate any class that inherits from LDAPObject

        Returns:
            LDAPObject: an LDAPObject inheriting class
        """

        return self._value_["pythonClass"]

    @property
    def object_cls(self) -> str:
        """
        Returns the objectClass property of an LDAPObjectType
        This function is used to make LDAP queries

        Returns:
            str: the LDAP object class tide to this type
        """

        return self._value_["objectClass"]

    @property
    def filter(self) -> str:
        """
        Returns the filter property of an LDAPObjectType
        This property is used to make LDAP queries

        Returns:
            str: LDAP filter matching this type
        """

        return self._value_["filter"]

    @property
    def attributes(self) -> List[str]:
        """
        Returns the attributes property of an LDAPObjectType

        Returns:
            List[atr]: a list of attributes to include in the results when searching for this type
        """

        return self._value_.get("attributes", "*")

    # ****************************************************************
    # Static methods

    @staticmethod
    def object_cls_is(object_type: str, value: str) -> bool:
        """
        Checks if the provided LDAPObjectType objectClass attribute is equal to the given value
        This method is used as a filter function for LDAPObjectType.from_object_cls method

        Args:
            object_type (str): element of the LDAPObjectType enumearation
            value (str)      : value to compare to the objectClass attribute of the provided LDAPObjectType

        Returns:
            bool: True if the value is equal to the objectClass attribute of the provided LDAPObjectType
        """

        return LDAPObjectType[object_type.upper()].object_cls == value

    @staticmethod
    def from_object_cls(object_cls: str) -> "LDAPObjectType":
        return next(
            filter(
                LDAPObjectType.object_cls_is,
                LDAPObjectType._member_names_,
                [object_cls] * len(LDAPObjectType._member_names_),
            )
        )

    @staticmethod
    def get_ldap_class(object_type: str) -> LDAPObject:
        """
        Returns an LDAPObject derivated class matching the provided type

        Args:
            object_type (str): object type to search

        Returns:
            LDAPObject: LDAPObject derivated class
        """

        return LDAPObjectType[object_type.upper()].python_cls

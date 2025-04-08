from enum import Enum

from .account.group.ldap_group import LDAPGroup
from .account.ldap_computer import LDAPComputer
from .account.ldap_user import LDAPUser
from .gpo.ldap_gpo import LDAPGroupPolicyObject
from .ldap_object import LDAPObject
from .ou.ldap_ou import LDAPOrganizationalUnit
from .subnet import LDAPSubnet


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


def get_ldap_class(object_type: str) -> LDAPObject:
    """Returns an ldap object instance based on given type"""
    return LDAPObjectType[object_type.upper()].value["pythonClass"]

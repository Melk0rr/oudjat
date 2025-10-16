"""
A helper module that defines some useful types for LDAP modules.
"""

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .objects.account.group.ldap_group import LDAPGroup
    from .objects.account.ldap_computer import LDAPComputer
    from .objects.account.ldap_user import LDAPUser
    from .objects.gpo.ldap_gpo import LDAPGroupPolicyObject
    from .objects.ldap_object import LDAPObject
    from .objects.ou.ldap_ou import LDAPOrganizationalUnit
    from .objects.subnet.ldap_subnet import LDAPSubnet

LDAPObjListTypeAlias: TypeAlias = list[
    LDAPObject
    | LDAPComputer
    | LDAPGroupPolicyObject
    | LDAPGroup
    | LDAPOrganizationalUnit
    | LDAPSubnet
    | LDAPUser
]

LDAPObjTypeAlias: TypeAlias = (
    type[LDAPObject]
    | type[LDAPComputer]
    | type[LDAPGroupPolicyObject]
    | type[LDAPGroup]
    | type[LDAPOrganizationalUnit]
    | type[LDAPSubnet]
    | type[LDAPUser]
)


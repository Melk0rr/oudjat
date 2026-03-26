"""
A simple module to enumerate some LDAP account flags.
"""

from typing import TYPE_CHECKING

from oudjat.utils.enum_utils import extend_enum

from ...ldap_object_flags import LDAPObjectFlag
from ..ldap_account_flags import LDAPAccountFlag

if TYPE_CHECKING:
    from .ldap_user import LDAPUser


def _is_adm_check(acc: "LDAPUser") -> bool:
    return acc.is_admin

@extend_enum(LDAPAccountFlag, LDAPObjectFlag)
class LDAPUserFlag(LDAPObjectFlag):
    """Specific flags for ldap accounts."""

    IS_ADMIN = _is_adm_check,



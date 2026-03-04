"""
A simple module to enumerate some LDAP computer flags.
"""

from oudjat.utils.enum_utils import extend_enum

from ...ldap_object_flags import LDAPObjectFlag
from ..ldap_account_flags import LDAPAccountFlag


@extend_enum(LDAPAccountFlag, LDAPObjectFlag)
class LDAPComputerFlag(LDAPObjectFlag):
    """Specific flags for ldap accounts."""



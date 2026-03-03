"""
A simple module to enumerate some LDAP object flags.
"""

from oudjat.utils.bit_flag import BitFlag


class LDAPObjectFlag(BitFlag):
    """A simple enumeration of some custom flags that may be assigned to LDAP objects."""

    OLD_PASSWORD = 1
    POTENTIAL_CLEARTXT_PWD = 2
    WEAK_ENCRYPTION_SUPPORTED = 4

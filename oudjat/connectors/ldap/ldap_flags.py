"""
A simple module to enumerate some LDAP object flags.
"""

from oudjat.utils.bit_flag import BitFlag


class LDAPFlag(BitFlag):
    """A simple enumeration of some custom flags that may be assigned to LDAP objects."""

    OLD_PASSWORD = 1
    VERY_OLD_PASSWORD = 2
    POTENTIAL_CLEARTXT_PWD = 4
    WEAK_ENCRYPTION_SUPPORTED = 8
    IS_ADMIN = 16

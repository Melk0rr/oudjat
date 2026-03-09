"""
A simple module to enumerate some LDAP account flags.
"""

from typing import TYPE_CHECKING

from ..ldap_object_flags import LDAPObjectFlag
from .ad_encryption_types import ADEncryptionType

if TYPE_CHECKING:
    from .ldap_account import LDAPAccount


def _pwd_age_check(acc: "LDAPAccount", age: int) -> bool:
    return acc.pwd_last_set_in_days >= age


def _enc_check(acc: "LDAPAccount", enc: int) -> bool:
    enc_details = acc.supported_encryption
    return enc_details["value"] is not None and bool(
        ADEncryptionType.check_flag(enc_details["value"], enc)
    )

def _clr_txt_pwd_check(acc: "LDAPAccount") -> bool:
    return acc.search_clear_txt_pwd()

class LDAPAccountFlag(LDAPObjectFlag):
    """Specific flags for ldap accounts."""

    OLD_PASSWORD = _pwd_age_check, 180
    VERY_OLD_PASSWORD = _pwd_age_check, 1095
    POTENTIAL_CLEARTXT_PWD = _clr_txt_pwd_check,
    WEAK_ENCRYPTION_SUPPORTED = _enc_check, 7


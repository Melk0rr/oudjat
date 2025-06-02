"""A package focuses on Group policy objects and their manipulation through LDAP."""

from .ldap_gpo import LDAPGroupPolicyObject
from .ms_gppref import MS_GPPREF

__all__ = ["MS_GPPREF", "LDAPGroupPolicyObject"]

from typing import TYPE_CHECKING

from ..ldap_object import LDAPObject

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry

class LDAPOrganizationalUnit(LDAPObject):
    """A class to handle LDAP Organizational Units"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry"):
        """Constructor"""
        super().__init__(ldap_entry=ldap_entry)

    # ****************************************************************
    # Methods

    # TODO: Get OU members
    # TODO: Get sub OU

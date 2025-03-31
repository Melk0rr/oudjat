from typing import TYPE_CHECKING

from ..ldap_object import LDAPObject

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry


class LDAPOrganizationalUnit(LDAPObject):
    """A class to handle LDAP Organizational Units"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry") -> None:
        """
        Initializes a new instance of LDAP OU

        Args:
            ldap_entry (LDAPEntry) : ldap entry instance to be used to populate object data
        """

        super().__init__(ldap_entry=ldap_entry)


    # ****************************************************************
    # Methods

    # TODO: Get OU members with filter per object type
    # TODO: Get sub OU
    # TODO: Get GPOs that applies on current OU

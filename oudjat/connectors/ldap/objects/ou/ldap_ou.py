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

    def get_gplink(self) -> str:
        """
        Returns the gpLink property of the OU

        Returns:
            str : gpLink attribute containing links to group policy objects
        """

        return self.entry.get("gpLink")

    def is_protected_from_deletion(self) -> bool:
        """
        Returns whether the OU is protected from accidental deletion

        Returns:
            bool: True if the OU is protected; False otherwise
        """

        return self.entry.get("protectedFromAccidentalDeletion")

    # TODO: Get OU members with filter per object type
    # TODO: Get sub OU
    # TODO: Get GPOs that applies on current OU

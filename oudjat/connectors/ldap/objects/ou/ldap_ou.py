from typing import TYPE_CHECKING, Dict, List

from ..ldap_object import LDAPObject

if TYPE_CHECKING:
    from ...ldap_connector import LDAPConnector
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

    # TODO: Get OU members with filter per object type
    def get_objects(self, ldap_connector: "LDAPConnector") -> List["LDAPEntry"]:
        """
        Returns the objects contained in the current OU

        Args:
            ldap_connector (LDAPConnector) : connector used for the query

        Returns:
            List[LDAPEntry] : entries of the objects contained in the OU
        """

        return ldap_connector.get_ou_objects(ldap_ou=self)

    # TODO: Get sub OU
    # TODO: Get GPOs that applies on current OU

    def to_dict(self) -> Dict:
        """
        Converts the current instance into a dictionary.

        Returns:
            dict: A dictionary containing the attributes of the LDAP ou in a structured format
        """

        return {
            **super().to_dict(),
            "gpLink": self.get_gplink()
        }

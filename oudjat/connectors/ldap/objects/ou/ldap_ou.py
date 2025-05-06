import re
from typing import TYPE_CHECKING, Dict, List

from ..definitions import UUID_REG
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

    def get_objects(
        self, ldap_connector: "LDAPConnector", object_types: List[str] = None
    ) -> List["LDAPEntry"]:
        """
        Returns the objects contained in the current OU

        Args:
            ldap_connector (LDAPConnector) : connector used for the query

        Returns:
            List[LDAPEntry] : entries of the objects contained in the OU
        """

        return ldap_connector.get_ou_objects(ldap_ou=self, object_types=object_types)

    # TODO: Get sub OU
    def get_sub_ous(self, ldap_connector: "LDAPConnector") -> List["LDAPEntry"]:
        """
        Returns only sub OUs from the ou objects

        Args:
            ldap_connector (LDAPConnector): connector used for the query

        Returns:
            List[LDAPEntry]: list of sub OUs
        """

        return ldap_connector.get_ou(search_base=self.dn)

    # TODO: Get GPOs that applies on current OU
    def get_gpo_from_gplink(self, ldap_connector: "LDAPConnector") -> List["LDAPObject"]:
        """
        This method extracts the GPO references (UUIDs) present in the current OU gpLink
        It then uses it to retrieve corresponding LDAP GPO instances

        Args:
            ldap_connector (LDAPConnector): the LDAP connector used to retrieve the GPOs

        Returns:
            List[LDAPObject]: a list of LDAPGroupPolicyObject instances based on the UUIDs in thecurrent OU gpLink attribute
        """

        gpo_refs = re.search(UUID_REG, self.get_gplink())
        return [ldap_connector.get_gpo(name=link) for link in gpo_refs]

    def to_dict(self) -> Dict:
        """
        Converts the current instance into a dictionary.

        Returns:
            dict: A dictionary containing the attributes of the LDAP ou in a structured format
        """

        return {**super().to_dict(), "gpLink": self.get_gplink()}

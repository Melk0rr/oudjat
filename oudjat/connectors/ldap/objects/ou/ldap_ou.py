"""Main module to handle LDAP Organizational Unit stuff."""

import re
from typing import TYPE_CHECKING, Any, override

from ..definitions import UUID_REG

if TYPE_CHECKING:
    from ...ldap_connector import LDAPConnector
    from ..gpo.ldap_gpo import LDAPGroupPolicyObject
    from ..ldap_entry import LDAPEntry
    from ..ldap_object import LDAPObject

class LDAPOrganizationalUnit(LDAPObject):
    """
    A class to handle LDAP Organizational Units.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry") -> None:
        """
        Initialize a new instance of LDAP OU.

        Args:
            ldap_entry (LDAPEntry) : ldap entry instance to be used to populate object data
        """

        super().__init__(ldap_entry=ldap_entry)

    # ****************************************************************
    # Methods

    def get_gplink(self) -> str:
        """
        Return the gpLink property of the OU.

        Returns:
            str : gpLink attribute containing links to group policy objects
        """

        return self.entry.get("gPLink")

    def get_objects(
        self, ldap_connector: "LDAPConnector", object_types: list[str] | None = None
    ) -> list["LDAPEntry"]:
        """
        Return the objects contained in the current OU.

        Args:
            ldap_connector (LDAPConnector) : connector used for the query
            object_types (List[str]): specific object types to include in the result

        Returns:
            List[LDAPEntry] : entries of the objects contained in the OU
        """

        return ldap_connector.get_ou_objects(ldap_ou=self, object_types=object_types)

    def get_sub_ous(self, ldap_connector: "LDAPConnector") -> list["LDAPOrganizationalUnit"]:
        """
        Return only sub OUs from the ou objects.

        Args:
            ldap_connector (LDAPConnector): connector used for the query

        Returns:
            List[LDAPEntry]: list of sub OUs
        """

        return ldap_connector.get_ou(search_base=self.dn)

    def get_gpo_from_gplink(self, ldap_connector: "LDAPConnector") -> list["LDAPGroupPolicyObject"]:
        """
        Extract the GPO references (UUIDs) present in the current OU gpLink.

        It then uses it to retrieve corresponding LDAP GPO instances.

        Args:
            ldap_connector (LDAPConnector): the LDAP connector used to retrieve the GPOs

        Returns:
            List[LDAPObject]: a list of LDAPGroupPolicyObject instances based on the UUIDs in thecurrent OU gpLink attribute
        """

        gpo_refs = re.search(UUID_REG, self.get_gplink())
        gpo_refs_str = gpo_refs.group() if gpo_refs is not None else []

        return list(map(lambda link: ldap_connector.get_gpo(name=link)[0], gpo_refs_str))

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict: A dictionary containing the attributes of the LDAP ou in a structured format
        """

        return {**super().to_dict(), "gpLink": self.get_gplink()}

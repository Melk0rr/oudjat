"""A module to handle subnet objects in LDAP."""
from typing import TYPE_CHECKING

from oudjat.assets.network.subnet import Subnet

from ..ldap_object import LDAPObject

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry


class LDAPSubnet(LDAPObject, Subnet):
    """A class to describe LDAP subnet objects."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry"):
        """
        Create a new instance of LDAPSubnet.

        Args:
            ldap_entry (LDAPEntry): base dictionary entry
        """

        super().__init__(ldap_entry=ldap_entry)
        Subnet.__init__(
            self,
            address=ldap_entry.get("name"),
            name=ldap_entry.get("location"),
            description=" ".join(ldap_entry.get("description")),
        )

    # ****************************************************************
    # Methods

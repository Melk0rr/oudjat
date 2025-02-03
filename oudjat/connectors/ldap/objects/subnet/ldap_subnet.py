from oudjat.model.assets.network import Subnet
from ..ldap_object import LDAPObject


class LDAPSubnet(LDAPObject, Subnet):
    """A class to describe LDAP subnet objects"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry"):  # noqa: F821
        """Constructor"""
        super().__init__(ldap_entry=ldap_entry)
        Subnet.__init__(
            self,
            addr=ldap_entry.get("name"),
            name=ldap_entry.get("location"),
            description=" ".join(ldap_entry.get("description")),
        )

    # ****************************************************************
    # Methods

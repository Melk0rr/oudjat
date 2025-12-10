"""A module to handle subnet objects in LDAP."""

from typing import TYPE_CHECKING, Any, override

from oudjat.core.network.subnet import Subnet

from ..ldap_object import LDAPObject

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry
    from ..ldap_object import LDAPCapabilities


class LDAPSubnet(LDAPObject):
    """A class to describe LDAP subnet objects."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry", capabilities: "LDAPCapabilities") -> None:
        """
        Create a new instance of LDAPSubnet.

        Args:
            ldap_entry (LDAPEntry)         : Base dictionary entry
            capabilities (LDAPCapabilities): LDAP capabilities which provide ways for an LDAP object to interact with an LDAP server through an LDAPConnector
        """

        super().__init__(ldap_entry, capabilities)
        self._subnet: "Subnet" = Subnet(
            address=ldap_entry.get("name"),
            name=ldap_entry.get("location"),
            description=" ".join(ldap_entry.get("description")),
        )

    # ****************************************************************
    # Methods

    def to_subnet(self) -> "Subnet":
        """
        Convert the current LDAPSubnet into a regular Subnet instance.

        Returns:
            Subnet: A regular subnet instance based on the current LDAPSubnet
        """

        net = self._subnet
        net.add_custom_attr("ldap", super().to_dict())

        return net

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: string representation of the current instance
        """

        return str(self._subnet)

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: dictionary representation of the current instance
        """

        return {
            **super().to_dict(),
            **self._subnet.to_dict()
        }

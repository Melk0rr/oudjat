"""
A class that describes Network interfaces.
"""

from dataclasses import dataclass
from typing import Any, override

from oudjat.core import GenericIdentifiable
from oudjat.core.network.ip import IP
from oudjat.core.network.mac import MAC


@dataclass
class NetInterfaceIP:
    """
    A simple data class to group network interface ip versions together.

    Attributes:
        ipv4 (IP | None): IPv4 of the interface
        ipv6 (IP | None): IPv6 of the interface
    """

    ipv4: "IP | None"
    ipv6: "IP | None"

class NetInterface(GenericIdentifiable):
    """
    A class to describe Network interfaces.
    """

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self, net_id: int | str, name: str, ipv4: "IP | None", ipv6: "IP | None", physical: "str | MAC | None"
    ) -> None:
        """
        Create a new network interface.

        Args:
            net_id (int | str)  : Interface ID
            name (str)          : Interface name
            ipv4 (IP | None)    : IPv4 of the interface
            ipv6 (IP | None)    : IPv6 of the interface
            physical (str | MAC): MAC address bound to the interface
        """

        super().__init__(gid=net_id, name=name)

        self._physical: "MAC | None" = None
        if physical is not None:
            self._physical = MAC(physical) if not isinstance(physical, MAC) else physical

        self._ip: "NetInterfaceIP" = NetInterfaceIP(ipv4=ipv4, ipv6=ipv6)

    # ****************************************************************
    # Methods

    @property
    def physical(self) -> "MAC | None":
        """
        Return the physical address of the interface.

        Returns:
            MAC | None: The physical address of the interface if any
        """

        return self._physical

    @property
    def ip(self) -> "NetInterfaceIP":
        """
        Return the network interface ip.

        Returns:
            NetInterfaceIP: The network interface ip
        """

        return self._ip

    @override
    def __str__(self) -> str:
        return f"{self._id}"

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the instance
        """

        return {
            **super().to_dict(),
            "ip": {
                "ipv4": self._ip.ipv4,
                "ipv6": self._ip.ipv6
            },
            "physical": str(self._physical)
        }

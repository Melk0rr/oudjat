"""A module that handle Subnets."""

from typing import Any, override

from oudjat.utils import Context
from oudjat.utils.operators.logical_operators import LogicalOperation

from ..generic_identifiable import GenericIdentifiable
from .ip import IP
from .netmask import NetMask


class Subnet(GenericIdentifiable):
    """A class to handle subnets."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        address: "int | str | IP",
        name: str,
        mask: "NetMask | None" = None,
        description: str | None = None,
        hosts: list["IP"] | None = None,
    ) -> None:
        """
        Initialize a Subnet object.

        Args:
            address (int | str | IPv4): The network address in string format or an IPv4 object representing the base IP address of the subnet.
            name (str)                : A descriptive name for the subnet.
            mask (IPv4Mask | None)    : The subnet mask. Can be provided as a CIDR notation string, an integer representing the number of leading 1-bits in the netmask, or a custom IPv4Mask object. I
                                        If not provided, it will be determined from the address if possible (e.g., "192.168.1.0/24").
            description (str | None)  : A brief description of the subnet, useful for administrative notes.
            hosts (list[IPv4] | None) : An optional list of IP addresses or strings representing host IPs that are part of this subnet. Each element can be an IPv4 object or a string representation of an IP address.
        """

        context = Context()

        self._mask: "NetMask"

        # NOTE: Try to extract mask if provided as CIDR notation along with the address as a string
        cidr: int
        if isinstance(address, str) and ("/" in address):
            address, cidr_str = address.split("/")
            cidr = int(cidr_str)
            mask = NetMask.from_cidr(cidr)

        if not isinstance(address, IP):
            address = IP(address)

        if mask is None:
            raise ValueError(f"{context}::Provided net address has no mask set: {address.value}")

        self._mask = mask

        # NOTE: Assures the address is a valid subnet address
        self._address: "IP" = IP(
            address=LogicalOperation.logical_and(int(address), int(self._mask))
        )

        super().__init__(gid=str(self), name=name, description=description)

        self._hosts: dict[str, "IP"] = {}

        if hosts is not None:
            for ip in hosts:
                self.add_host(ip)

    # ****************************************************************
    # Methods

    @property
    def address(self) -> IP:
        """
        Return subnet address.

        Returns:
            IPv4: The IP address of the subnet.
        """

        return self._address

    @property
    def mask(self) -> NetMask:
        """
        Return ip mask instance.

        Returns:
            IPv4Mask: The netmask or CIDR notation of the subnet.
        """

        return self._mask

    @mask.setter
    def mask(self, new_mask: NetMask) -> None:
        """
        Set the ip mask.

        Args:
            new_mask (IPv4Mask): The new subnet mask or CIDR notation to set.
        """

        self._mask = new_mask

    @property
    def broadcast(self) -> IP:
        """
        Return the broadcast address of the current subnet.

        Returns:
            IPv4: The broadcast IP address of the subnet.
        """

        broadcast_int: int = LogicalOperation.logical_or(int(self.mask.wildcard), int(self.address))

        return IP(IP.ip_int_to_str(broadcast_int))

    def contains(self, ip: "int | str | IP") -> bool:
        """
        Check whether the provided IP is in the current subnet.

        Args:
            ip (Union[str, IPv4]): The IP address to check.

        Returns:
            bool: True if the IP is within the subnet, False otherwise.
        """

        if not isinstance(ip, IP):
            ip = IP(ip)

        mask_address: int = int(self.mask)
        return LogicalOperation.logical_and(int(ip), mask_address) == LogicalOperation.logical_and(
            int(self.address), mask_address
        )

    def list_addresses(self) -> list[str]:
        """
        List all possible hosts in the subnet.

        Returns:
            list[str]: A list of IP addresses representing the host range in the subnet.
        """
        start = self.address.value + 1
        end = int(self.broadcast)

        return [f"{IP.ip_int_to_str(i)}/{self.mask.cidr}" for i in range(start, end)]

    def add_host(self, host: IP) -> None:
        """
        Add a new host to the subnet.

        Args:
            host (Union[str, IPv4]): The IP address of the host to be added.
        """

        if (
            self.contains(host)
            and int(host) != int(self._address)
            and int(host) != int(self.broadcast)
        ):
            self._hosts[str(host)] = host

    @override
    def __str__(self) -> str:
        """
        Return a string based on the current instance.

        Returns:
            str: A string representation of the subnet, including its address and mask.
        """
        return f"{self.address}/{self.mask.cidr}"

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current subnet instance into a dictionary.

        Returns:
            dict: A dictionary representation of the subnet
        """

        base = super().to_dict()
        _ = base.pop("id")

        return {
            "address": str(self.address),
            "mask": self._mask.to_dict(),
            **base,
            "hosts": {h_k: h.to_dict() for h_k, h in self._hosts.items()},
            "broadcast": str(self.broadcast),
        }

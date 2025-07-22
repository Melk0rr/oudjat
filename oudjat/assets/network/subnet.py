"""A module that handle Subnets."""

from typing import Any, override

from oudjat.utils.logical_operations import LogicalOperation

from .definitions import ip_int_to_str
from .ipv4 import IPv4, IPv4Mask


class Subnet:
    """A class to handle subnets."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        address: int | str | IPv4,
        name: str,
        mask: IPv4Mask | None = None,
        description: str | None = None,
        hosts: list[IPv4] | None = None,
    ):
        """
        Initialize a Subnet object.

        Args:
            address (Union[str, IPv4])                    : The network address in string format or an IPv4 object representing the base IP address of the subnet.
            name (str)                                    : A descriptive name for the subnet.
            mask (Union[int, str, IPv4Mask], optional)    : The subnet mask. Can be provided as a CIDR notation string, an integer representing the number of leading 1-bits in the netmask, or a custom IPv4Mask object. If not provided, it will be determined from the address if possible (e.g., "192.168.1.0/24").
            description (str, optional)                   : A brief description of the subnet, useful for administrative notes.
            hosts (Union[List[IPv4], List[str]], optional): An optional list of IP addresses or strings representing host IPs that are part of this subnet. Each element can be an IPv4 object or a string representation of an IP address.
        """

        self._mask: IPv4Mask

        # NOTE: Try to extract mask if provided as CIDR notation along with the address as a string
        cidr: int
        if isinstance(address, str) and ("/" in address):
            address, cidr_str = address.split("/")
            cidr = int(cidr_str)
            mask = IPv4Mask.from_cidr(cidr)

        if not isinstance(address, IPv4):
            address = IPv4(address)

        if mask is None:
            raise ValueError(
                f"{__class__.__name__}.__init__::Provided net address has no mask set: {address.address}"
            )

        self.mask = mask

        # NOTE: Assures the address is a valid subnet address
        self._address: IPv4 = IPv4(
            address=LogicalOperation.logical_and(int(address), int(self._mask))
        )

        self._name: str = name
        self._description: str | None = description
        self._hosts: dict[str, IPv4] = {}

        if hosts is not None:
            for ip in hosts:
                self.add_host(ip)

    # ****************************************************************
    # Methods

    @property
    def name(self) -> str:
        """
        Return the name of this subnet instance.

        Returns:
             str: name of the subnet as a string
        """

        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """
        Set a new name for the current subnet.

        Args:
            new_name (str): new name for the subnet
        """

        self._name = new_name

    @property
    def description(self) -> str | None:
        """
        Return the name of this subnet instance.

        Returns:
             str: name of the subnet as a string
        """

        return self._description

    @description.setter
    def description(self, new_description: str) -> None:
        """
        Set a new description for the current subnet.

        Args:
            new_description (str): new description for the subnet
        """

        self._description = new_description

    @property
    def address(self) -> IPv4:
        """
        Return subnet address.

        Returns:
            IPv4: The IP address of the subnet.
        """

        return self._address

    @property
    def mask(self) -> IPv4Mask:
        """
        Return ip mask instance.

        Returns:
            IPv4Mask: The netmask or CIDR notation of the subnet.
        """

        return self._mask

    @mask.setter
    def mask(self, new_mask: IPv4Mask) -> None:
        """
        Set the ip mask.

        Args:
            new_mask (IPv4Mask): The new subnet mask or CIDR notation to set.
        """

        self._mask = new_mask

    @property
    def broadcast(self) -> IPv4:
        """
        Return the broadcast address of the current subnet.

        Returns:
            IPv4: The broadcast IP address of the subnet.
        """

        broadcast_int: int = LogicalOperation.logical_or(
            int(self.mask.get_wildcard()), int(self.address)
        )

        return IPv4(ip_int_to_str(broadcast_int))

    def contains(self, ip: IPv4) -> bool:
        """
        Check whether the provided IP is in the current subnet.

        Args:
            ip (Union[str, IPv4]): The IP address to check.

        Returns:
            bool: True if the IP is within the subnet, False otherwise.
        """

        mask_address: int = int(self.mask)
        return LogicalOperation.logical_and(int(ip), mask_address) == LogicalOperation.logical_and(
            int(self.address), mask_address
        )

    def list_addresses(self) -> list[str]:
        """
        List all possible hosts in the subnet.

        Returns:
            List[str]: A list of IP addresses representing the host range in the subnet.
        """
        start = self.address.address + 1
        end = int(self.broadcast)

        return [f"{ip_int_to_str(i)}/{self.mask.cidr}" for i in range(start, end)]

    def add_host(self, host: IPv4) -> None:
        """
        Add a new host to the subnet.

        Args:
            host (Union[str, IPv4]): The IP address of the host to be added.
        """

        if (
            self.contains(host)
            and int(host) != int(self.address)
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

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current subnet instance into a dictionary.

        Returns:
            dict: A dictionary representation of the subnet
        """

        return {
            "net_address": str(self.address),
            "net_mask": str(self.mask),
            "net_mask_cidr": self.mask.__str__(cidr=True),
            "hosts": self._hosts,
            "broadcast_address": str(self.broadcast),
        }

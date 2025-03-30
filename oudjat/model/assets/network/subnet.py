from typing import Dict, List, Union

from oudjat.utils import i_and, i_or

from .ipv4 import IPv4, IPv4Mask, ip_int_to_str


class Subnet:
    """A class to handle subnets"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        address: Union[str, IPv4],
        name: str,
        mask: Union[int, str, IPv4Mask] = None,
        description: str = None,
        hosts: Union[List[IPv4], List[str]] = None,
    ):
        """Constructor for initializing a Subnet object.

        Args:
            address (Union[str, IPv4]): The network address in string format or an IPv4 object representing the base IP address of the subnet.
            name (str): A descriptive name for the subnet.
            mask (Union[int, str, IPv4Mask], optional): The subnet mask. Can be provided as a CIDR notation string, an integer representing the number of leading 1-bits in the netmask, or a custom IPv4Mask object. If not provided, it will be determined from the address if possible (e.g., "192.168.1.0/24").
            description (str, optional): A brief description of the subnet, useful for administrative notes.
            hosts (Union[List[IPv4], List[str]], optional): An optional list of IP addresses or strings representing host IPs that are part of this subnet. Each element can be an IPv4 object or a string representation of an IP address.

        Attributes:
            mask (IPv4Mask) : The netmask associated with the subnet, which is derived from the provided address and mask parameters. If not explicitly set during initialization, it will be determined based on the network prefix length implied by the given address.
            address (IPv4)  : The base IP address of the subnet after applying any provided mask.
            broadcast (IPv4): The calculated broadcast address for this subnet. This is derived from the network address and the netmask.
            name (str)      : A user-defined name or identifier for the subnet.
            description (str, optional): A textual description associated with the subnet; can be used to provide details such as purpose, location, etc.
            hosts (dict)    : A dictionary where keys are host IP addresses and values could represent various attributes of these hosts in the network like MAC address or hostname. This is initially an empty dict that will store host information if provided during initialization.
        """

        self.mask: IPv4Mask = None

        # Try to extract mask if provided as CIDR notation
        cidr = None
        if (type(address) is str) and ("/" in address):
            address, cidr = address.split("/")
            cidr = int(cidr)

            if cidr is not None:
                mask = IPv4Mask.get_netmask(cidr)

        if not isinstance(address, IPv4):
            address = IPv4(address)

        if mask is None:
            raise ValueError(
                f"Subnet::Provided net address has no mask set: {address.get_address()}"
            )

        self.set_mask(mask)

        self.address: IPv4 = IPv4(address=i_and(int(address), int(self.mask)))
        self.broadcast = self.get_broadcast_address()

        self.name = name
        self.description = description

        self.hosts = {}

        if hosts is not None:
            for ip in hosts:
                self.add_host(ip)

    # ****************************************************************
    # Methods

    def get_name(self) -> str:
        """Getter for the subnet name.

        Returns:
            str: The name of the subnet (not implemented in this example).
        """
        return self.name

    def get_description(self) -> str:
        """Getter for the subnet description.

        Returns:
            str: A brief description of the subnet (not implemented in this example).
        """
        return self.description

    def get_address(self) -> IPv4:
        """Getter for subnet address.

        Returns:
            IPv4: The IP address of the subnet.
        """
        return self.address

    def get_mask(self) -> IPv4Mask:
        """Getter for ip mask instance.

        Returns:
            IPv4Mask: The netmask or CIDR notation of the subnet.
        """
        return self.mask

    def get_broadcast_address(self) -> IPv4:
        """Returns the broadcast address of the current subnet.

        Returns:
            IPv4: The broadcast IP address of the subnet.
        """
        broadcast_int = i_or(int(self.mask.get_wildcard()), int(self.address))
        return IPv4(ip_int_to_str(broadcast_int))

    def set_mask(self, mask: Union[int, str, IPv4Mask]) -> None:
        """Setter for ip mask.

        Args:
            mask (Union[int, str, IPv4Mask]): The new subnet mask or CIDR notation to set.
        """
        if not isinstance(mask, IPv4Mask):
            mask = IPv4Mask(mask)
        self.mask = mask

    def contains(self, ip: Union[str, IPv4]) -> bool:
        """Checks whether the provided IP is in the current subnet.

        Args:
            ip (Union[str, IPv4]): The IP address to check.

        Returns:
            bool: True if the IP is within the subnet, False otherwise.
        """
        if not isinstance(ip, IPv4):
            ip = IPv4(ip)
        mask_address = int(self.mask)
        return i_and(int(ip), mask_address) == i_and(int(self.address), mask_address)

    def list_addresses(self) -> List[str]:
        """Lists all possible hosts in the subnet.

        Returns:
            List[str]: A list of IP addresses representing the host range in the subnet.
        """
        start = self.address.get_address() + 1
        end = int(self.broadcast)
        return [f"{ip_int_to_str(i)}/{self.mask.get_cidr()}" for i in range(start, end)]

    def add_host(self, host: Union[str, IPv4]) -> None:
        """Adds a new host to the subnet.

        Args:
            host (Union[str, IPv4]): The IP address of the host to be added.
        """
        if not isinstance(host, IPv4):
            host = IPv4(host)
        if (
            self.contains(host)
            and int(host) != int(self.address)
            and int(host) != int(self.broadcast)
        ):
            self.hosts[str(host)] = host

    def __str__(self) -> str:
        """Returns a string based on the current instance.

        Returns:
            str: A string representation of the subnet, including its address and mask.
        """
        return f"{self.address}/{self.mask.get_cidr()}"

    def to_dict(self) -> Dict:
        """Converts the current subnet instance into a dictionary.

        Returns:
            Dict: A dictionary representation of the subnet
        """
        return {
            "net_address": str(self.get_address()),
            "net_mask": str(self.get_mask()),
            "net_mask_cidr": self.get_mask().__str__(as_cidr=True),
            "hosts": self.hosts,
            "broadcast_address": str(self.get_broadcast_address()),
        }

"""A module that describes IP addresses."""

import re
import socket
from enum import Enum
from typing import NamedTuple, override

from oudjat.utils import ColorPrint

from .definitions import cidr_to_int, count_1_bits, ip_int_to_str, ip_not, ip_str_to_int
from .port import Port


class IPVersionProps(NamedTuple):
    """
    A helper class to properly and conveniently handle IP version properties ant typing.
    """

    pattern: str


class IPVersion(Enum):
    """Enumeration representing different versions of IP addresses based on a regex pattern."""

    IPV4 = IPVersionProps(
        r"^(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$"
    )

    IPV6 = IPVersionProps(
        r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"
    )

    @property
    def pattern(self) -> str:
        """
        Get the regex pattern for the IP version.

        Returns:
            str: The regex pattern as a string.
        """

        return self._value_.pattern


# TODO: Handle IP version properly
# TODO: Centralize some static functions
class IPv4:
    """Simple Class providing tools to manipulate IPv4 addresses."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, address: int | str) -> None:
        """
        Create a new instance of IP address.

        Args:
            address (Union[int, str]): The IP address to be initialized. Can be either an integer or a string.

        Raises:
            ValueError: If the provided address is not a valid IPv4 or IPv6 address.
        """

        if isinstance(address, int):
            address = ip_int_to_str(address)

        self._version: IPVersion
        if re.match(IPVersion.IPV4.pattern, address):
            self._version = IPVersion.IPV4

        elif re.match(IPVersion.IPV6.pattern, address):
            self._version = IPVersion.IPV6

        else:
            raise ValueError(f"{__class__.__name__}::Invalid IPv4 address provided: '{address}'")

        self._address: int = ip_str_to_int(address)
        self._ports: dict[int, Port] = {}

    # ****************************************************************
    # Methods

    @property
    def address(self) -> int:
        """
        Getter for ip string address.

        Returns:
            int: The integer representation of the IP address.
        """

        return self._address

    @property
    def version(self) -> IPVersion:
        """
        Return the version of the current ip address.

        Returns:
            IPVersion: version of this ip address (IPVersion.IPv4 or IPVersion.IPV6)
        """

        return self._version

    def get_port_numbers(self) -> list[int]:
        """
        Getter for the Port numbers.

        Returns:
            List[int]: A list of integers representing the port numbers.
        """

        return list(self._ports.keys())

    def get_port_strings(self) -> list[str]:
        """
        Getter for the Port strings.

        Returns:
            List[str]: A list of strings representing the port numbers converted to string format.
        """

        return list(map(str, self._ports.values()))

    def clear_ports(self) -> None:
        """
        Clear the ports.

        This method removes all entries from the `ports` dictionary.
        """

        for port in list(self._ports.keys()):
            del self._ports[port]

    def set_open_ports(self, ports: list[Port]) -> None:
        """
        Set the open ports.

        Args:
            ports (Union[List[int], List[Port]]): A list of integers or Port objects representing the ports to be set.

        This method first clears the existing ports and then adds the new ports provided in the argument.
        """

        self.clear_ports()
        for p in ports:
            self.append_open_port(p)

    def is_port_in_list(self, port: int) -> bool:
        """
        Check if the given port is in the list of ports.

        Args:
            port (Union[int, Port]): A port number or a Port object to be checked.

        Returns:
            bool: True if the port is found in the `ports` dictionary, False otherwise.

        This method first converts the given argument to an integer representation of a port and then checks its presence in the `ports` dictionary.
        """

        return port in self._ports.keys()

    def append_open_port(self, port: Port, force: bool = False) -> None:
        """
        Append the port to the list of open ports.

        Args:
            port (Port)          : The port to be appended.
            force (bool, optional): If set to True, will replace the existing port in the list wheither it already exists or not. Defaults to False.

        Raises:
            ValueError: If the provided port is neither an instance of Port nor an integer, a ValueError is raised.
        """

        if not self.is_port_in_list(port.number) or force:
            self._ports[port.number] = port

        else:
            print(f"{port} is already in the list of open ports")

    def remove_port(self, port: int) -> None:
        """
        Remove the port from the list of open ports.

        Args:
            port (int): The port number to be removed from the list.
        """

        del self._ports[port]

    def __int__(self) -> int:
        """
        Convert the current IP address into an integer.

        Returns:
            int: The integer representation of the IP address.
        """

        return self._address

    @override
    def __str__(self) -> str:
        """
        Convert the current IP address into a string.

        Returns:
            str: The string representation of the IP address.
        """

        return ip_int_to_str(self._address)

    @staticmethod
    def resolve_from_hostname(hostname: str) -> str | None:
        """
        Resolve the IP address for the given hostname.

        Args:
            hostname (str): The hostname to be resolved.

        Returns:
            str: The resolved IP address.
        """

        ip = None
        try:
            ip = socket.gethostbyname(hostname)

        except Exception as e:
            ColorPrint.red(f"{hostname}: could not resolve IP address\n{e}")

        return ip


class IPv4Mask(IPv4):
    """Simple Class providing tools to manipulate IPv4 mask."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, mask: int | str) -> None:
        """
        Create a new instance of IPMask.

        This method initializes the object with either a CIDR notation value or an integer/string representation of a netmask.

        Args:
            mask (Union[int, str])  : The netmask value as an integer or string.
            cidr (int)              : The network prefix length in CIDR notation.

        Raises:
            ValueError: If both `mask` and `cidr` are None, or if `cidr` is not between 1 and 32, or if `mask` is neither an integer nor a string.
        """

        if type(mask) is not int and type(mask) is not str:
            raise ValueError(
                f"{__class__.__name__}::Invalid mask provided : {mask}. You must provide a string or an integer !"
            )

        super().__init__(mask)

        self._cidr: int = count_1_bits(self.address)

    # ****************************************************************
    # Methods

    @property
    def cidr(self) -> int:
        """
        Return the cidr notation of the current mask.

        Returns:
            int: current mask instance as CIDR notation
        """

        return self._cidr

    def cidr_to_int(self) -> int:
        """
        Return the current mask as an integer.

        This method converts the network mask in CIDR notation to its integer representation.

        Returns:
            int: The netmask as an integer
        """

        return cidr_to_int(self._cidr)

    def get_wildcard(self) -> IPv4:
        """
        Return mask wildcard.

        This method calculates and returns the wildcard address for the current network mask.

        Returns:
            IPv4: The wildcard address as an IPv4 object
        """

        return IPv4(ip_not(self._address))

    @override
    def __str__(self, cidr: bool = False) -> str:
        """
        Convert the current instance into a string.

        Args:
            cidr (bool): Determines whether to return the CIDR notation or the default string representation of the netmask.

        Returns:
            str: The string representation of the netmask, either in CIDR notation if `as_cidr` is True, or the default format otherwise.
        """

        return f"/{self._cidr}" if cidr else str(self)

    # ****************************************************************
    # Static methods

    @staticmethod
    def check_cidr(cidr: int) -> bool:
        """
        Return wheither or not the provided CIDR notation is correct.

        CIDR notation values must be between 0 and 32.

        Args:
            cidr (int): CIDR notation to check

        Returns:
            bool: True if the provided CIDR is valid. False otherwise
        """

        return 0 <= cidr <= 32

    @staticmethod
    def from_cidr(cidr: int) -> "IPv4Mask":
        """
        Create a new IPv4Mask instance based on a CIDR integer.

        Detailed description.

        Args:
            cidr (int): net mask as a CIDR notation

        Returns:
            IPv4Mask: ipv4 mask instance based on the CIDR value provided

        Example:
            mask = IPv4Mask.from_cidr(24)
        """

        if not IPv4Mask.check_cidr(cidr):
            raise ValueError(f"{__class__.__name__}.from_cidr::Mask CIDR value must be between 1 and 32!")

        return IPv4Mask(cidr_to_int(cidr))

    @staticmethod
    def get_netcidr(mask: str) -> int:
        """
        Return CIDR notation for a given mask.

        Args:
            mask (str): The netmask in string format.

        Returns:
            int: The CIDR notation of the provided netmask.

        Raises:
            ValueError: If the provided mask is not valid
        """

        if mask not in IPv4Mask.get_valid_mask():
            raise ValueError(f"{__class__.__name__}.get_netcidr::Invalid mask provided: {mask}")

        return count_1_bits(IPv4(mask).address)

    @staticmethod
    def get_valid_mask() -> list[str]:
        """
        List all valid netmask strings for CIDR notation from 1 to 32.

        Returns:
            List[str]: A list of valid netmask strings
        """

        return list(map(IPv4Mask.get_netmask, range(1, 33)))

    @staticmethod
    def get_netmask(network_length: int) -> str:
        """
        Return an ipv4 mask string based on a network length.

        Args:
            network_length (int): The length of the network in CIDR notation.

        Returns:
            str: The netmask as a string.

        Raises:
            ValueError: If the provided network length is not an integer or outside the range 1 to 32
        """

        return ip_int_to_str(int(IPv4Mask.from_cidr(network_length)))

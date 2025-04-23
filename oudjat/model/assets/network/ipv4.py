import re
import socket
from enum import Enum
from typing import TYPE_CHECKING, List, Union

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.logical_operations import logical_and

from .definitions import cidr_to_int, count_1_bits, ip_int_to_str, ip_not, ip_str_to_int
from .port import Port

if TYPE_CHECKING:
    from .subnet import Subnet


class IPVersion(Enum):
    """
    Enumeration representing different versions of IP addresses.

    Attributes:
        IPV4 (dict): A dictionary with a regex pattern for IPv4 addresses.
        IPV6 (dict): A dictionary with a regex pattern for IPv6 addresses.
    """

    IPV4 = {
        "pattern": r"^(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$"
    }
    IPV6 = {
        "pattern": r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"
    }

    @property
    def pattern(self) -> str:
        """
        Get the regex pattern for the IP version

        Returns:
            str: The regex pattern as a string.
        """
        return self._value_["pattern"]


class IPv4:
    """Simple Class providing tools to manipulate IPv4 addresses"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, address: Union[int, str]) -> None:
        """
        Constructor for the IPAddress class.

        Args:
            address (Union[int, str]): The IP address to be initialized. Can be either an integer or a string.

        Raises:
            ValueError: If the provided address is not a valid IPv4 or IPv6 address.
        """

        if type(address) is int:
            address = ip_int_to_str(address)

        if re.match(IPVersion.IPV4.pattern, address):
            self.version = IPVersion.IPV4

        elif re.match(IPVersion.IPV6.pattern, address):
            self.version = IPVersion.IPV6

        else:
            raise ValueError(f"Invalid IPv4 address provided: '{address}'")

        self.address: int = ip_str_to_int(address)
        self.ports = {}

    # ****************************************************************
    # Methods

    def get_address(self) -> int:
        """
        Getter for ip string address.

        Returns:
            int: The integer representation of the IP address.
        """

        return self.address

    def get_port_numbers(self) -> List[int]:
        """
        Getter for the Port numbers.

        Returns:
            List[int]: A list of integers representing the port numbers.
        """

        return list(self.ports.keys())

    def get_port_strings(self) -> List[str]:
        """
        Getter for the Port strings.

        Returns:
            List[str]: A list of strings representing the port numbers converted to string format.
        """

        return [str(p) for p in self.ports.values()]

    def clear_ports(self) -> None:
        """
        Clears the ports.

        This method removes all entries from the `ports` dictionary.
        """

        for port in list(
            self.ports.keys()
        ):  # Making a copy of keys to avoid RuntimeError during modification
            del self.ports[port]

    def set_open_ports(self, ports: Union[List[int], List[Port]]):
        """
        Set the open ports.

        Args:
            ports (Union[List[int], List[Port]]): A list of integers or Port objects representing the ports to be set.

        This method first clears the existing ports and then adds the new ports provided in the argument.
        """

        self.clear_ports()
        for p in ports:
            self.append_open_port(p)

    def is_port_in_list(self, port: Union[int, Port]) -> bool:
        """
        Check if the given port is in the list of ports.

        Args:
            port (Union[int, Port]): A port number or a Port object to be checked.

        Returns:
            bool: True if the port is found in the `ports` dictionary, False otherwise.

        This method first converts the given argument to an integer representation of a port and then checks its presence in the `ports` dictionary.
        """

        port_number = port

        if isinstance(port, Port):
            port_number = port.get_number()

        return port_number in self.ports.keys()

    def append_open_port(self, port: Union[int, Port], force: bool = False):
        """Append the port to the list of open ports.

        Args:
            port (Union[int, Port]) : The port to be appended. It can be either an integer representing a port number or an instance of the Port class.
            force (bool, optional)  : If set to True, it will replace the existing port in the list if it already exists. Defaults to False.

        Raises:
            ValueError: If the provided port is neither an instance of Port nor an integer, a ValueError is raised.
        """

        is_port = isinstance(port, Port)
        is_number = isinstance(port, int)

        if not (is_port or is_number):
            raise ValueError("Provided port must be an instance of class Port or an integer")

        if is_number:
            port = Port(port_number=port)

        if not self.is_port_in_list(port) or force:
            self.ports[port.get_number()] = port

        else:
            print(f"{port} is already in the list of open ports")

    def remove_port(self, port: int) -> None:
        """Remove the port from the list of open ports.

        Args:
            port (int): The port number to be removed from the list.
        """

        del self.ports[port]

    def is_in_subnet(self, net: "Subnet") -> bool:
        """Checks if the current IP address is in the provided subnet.

        Args:
            net (Subnet): The subnet to check against.

        Returns:
            bool: True if the IP is within the subnet, False otherwise.
        """

        return logical_and(int(self), int(net.get_mask())) == logical_and(
            int(net.get_address()), int(net.get_mask())
        )

    def __int__(self) -> int:
        """
        Converts the current IP address into an integer.

        Returns:
            int: The integer representation of the IP address.
        """

        return self.address

    def __str__(self) -> str:
        """
        Converts the current IP address into a string.

        Returns:
            str: The string representation of the IP address.
        """

        return ip_int_to_str(self.address)

    @staticmethod
    def resolve_from_hostname(hostname: str) -> str:
        """
        Resolves the IP address for the given hostname.

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
    """Simple Class providing tools to manipulate IPv4 mask"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, mask: Union[int, str] = None, cidr: int = None):
        """
        Constructor for initializing a network mask.

        This method initializes the object with either a CIDR notation value or an integer/string representation of a netmask.

        Args:
            mask (Union[int, str])  : The netmask value as an integer or string.
            cidr (int)              : The network prefix length in CIDR notation.

        Raises:
            ValueError: If both `mask` and `cidr` are None, or if `cidr` is not between 1 and 32, or if `mask` is neither an integer nor a string.
        """

        if mask is None and cidr is None:
            raise ValueError(
                "Please provide either a CIDR mask or a mask value as integer or string"
            )

        if cidr is not None:
            if not 1 < cidr < 33:
                raise ValueError("Mask CIDR value must be between 1 and 32!")

            mask = cidr_to_int(cidr)

        if type(mask) is not int and type(mask) is not str:
            raise ValueError(
                f"Invalid mask provided : {mask}. You must provide a string or an integer !"
            )

        super().__init__(mask)
        self.cidr = count_1_bits(self.address)

    # ****************************************************************
    # Methods

    def get_cidr(self) -> int:
        """
        Getter for mask CIDR.
        Returns the current netmask's CIDR notation value
        """

        return self.cidr

    def cidr_to_int(self) -> int:
        """
        Returns the current mask as an integer.
        This method converts the network mask in CIDR notation to its integer representation.

        Returns:
            int: The netmask as an integer
        """

        return cidr_to_int(self.cidr)

    def get_wildcard(self) -> IPv4:
        """
        Returns mask wildcard.
        This method calculates and returns the wildcard address for the current network mask.

        Returns:
            IPv4: The wildcard address as an IPv4 object
        """

        return IPv4(ip_not(self.address))

    def __str__(self, as_cidr: bool = False) -> str:
        """
        Converts the current instance into a string.

        Args:
            as_cidr (bool): Determines whether to return the CIDR notation or the default string representation of the netmask.

        Returns:
            str: The string representation of the netmask, either in CIDR notation if `as_cidr` is True, or the default format otherwise.
        """

        if as_cidr:
            return f"{self.cidr}"

        return super().__str__()

    # ****************************************************************
    # Static methods

    @staticmethod
    def get_netcidr(mask: str) -> int:
        """
        Static method to return CIDR notation for a given mask.

        Args:
            mask (str): The netmask in string format.

        Returns:
            int: The CIDR notation of the provided netmask.

        Raises:
            ValueError: If the provided mask is not valid
        """

        if mask not in IPv4Mask.get_valid_mask():
            raise ValueError(f"Invalid mask provided: {mask}")

        base = IPv4(mask)
        return "".join(base.to_binary_array()).count("1")

    @staticmethod
    def get_valid_mask():
        """
        Static method to list all valid netmask strings for CIDR notation from 1 to 32.

        Returns:
            List[str]: A list of valid netmask strings
        """

        return list(map(IPv4Mask.get_netmask, range(1, 33)))

    @staticmethod
    def get_netmask(network_length: int) -> str:
        """
        Static method to return an ipv4 mask based on a network length.

        Args:
            network_length (int): The length of the network in CIDR notation.

        Returns:
            str: The netmask as a string.

        Raises:
            ValueError: If the provided network length is not an integer or outside the range 1 to 32
        """

        if type(network_length) is not int:
            raise ValueError("Network length must be an integer")

        if not 0 < network_length < 33:
            raise ValueError("Network length value must be between 1 and 32!")

        return ip_int_to_str(cidr_to_int(network_length))

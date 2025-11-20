"""A module that describes IP addresses."""

import re
import socket
from typing import override

from oudjat.utils import ColorPrint, Context, LogicalOperator

from .ipversions import IPVersion
from .port import Port


class IP:
    """Simple Class providing tools to manipulate IPv4 addresses."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, address: int | str, version: "IPVersion | None" = None) -> None:
        """
        Create a new instance of IP address.

        Args:
            address (int | str): The IP address to be initialized. Can be either an integer or a string.
            version (IPVersion): The version of the IP address. Must be provided if the initial address value is an integer

        Raises:
            ValueError: If the provided address is an integer and no version is specified
            ValueError: If the provided address is an integer and its value does not fit the maximum value associated with the provided version
            ValueError: If the provided address is not a valid IPv4 or IPv6 address.
        """

        context = Context.caller_infos()

        self._version: "IPVersion"
        if isinstance(address, int):
            if version is None:
                raise ValueError(
                    f"{context['qualname']}::When initializing a new IP with integer value, you must provide the IP version"
                )

            if not (0 <= address < (1 << version.bit_count)):
                raise ValueError(
                    f"{context['qualname']}::Invalid address value provided. The integer value you provided does not match the provided version {version}"
                )

            self._version = version
            self._address = address
            address = IP.ip_int_to_str(address, version)

        else:
            if re.match(IPVersion.IPV4.pattern, address):
                self._version = IPVersion.IPV4

            elif re.match(IPVersion.IPV6.pattern, address):
                self._version = IPVersion.IPV6

            else:
                raise ValueError(
                    f"{Context.caller_infos()['qualname']}::Invalid IPv4 address provided: '{address}'"
                )

            self._address: int = IP.ip_str_to_int(address, self._version)

        self._ports: dict[int, "Port"] = {}

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
    def version(self) -> "IPVersion":
        """
        Return the version of the current ip address.

        Returns:
            IPVersion: version of this ip address (IPVersion.IPv4 or IPVersion.IPV6)
        """

        return self._version

    @property
    def port_numbers(self) -> list[int]:
        """
        Getter for the Port numbers.

        Returns:
            list[int]: A list of integers representing the port numbers.
        """

        return list(self._ports.keys())

    @property
    def port_strings(self) -> list[str]:
        """
        Getter for the Port strings.

        Returns:
            list[str]: A list of strings representing the port numbers converted to string format.
        """

        return list(map(str, self._ports.values()))

    @property
    def bytes(self) -> list[int]:
        """
        Return current address bytes as a list of integers.

        Returns:
            list[int]: A list of the current address bytes
        """

        return IP.ip_bytes(int(self), self._version)

    def clear_ports(self) -> None:
        """
        Clear the ports.

        This method removes all entries from the `ports` dictionary.
        """

        for port in list(self._ports.keys()):
            del self._ports[port]

    def set_open_ports(self, ports: list["Port"]) -> None:
        """
        Set the open ports.

        Args:
            ports (list[Port]): A list of integers or Port objects representing the ports to be set.

        This method first clears the existing ports and then adds the new ports provided in the argument.
        """

        self.clear_ports()
        for p in ports:
            self.append_open_port(p)

    def _is_port_in_list(self, port: "int | Port") -> bool:
        """
        Check if the given port is in the list of ports.

        This method first converts the given argument to an integer representation of a port and then checks its presence in the `ports` dictionary.

        Args:
            port (int | Port): A port number or a Port object to be checked.

        Returns:
            bool: True if the port is found in the `ports` dictionary, False otherwise.
        """

        return int(port) in self._ports.keys()

    def append_open_port(self, port: Port, force: bool = False) -> None:
        """
        Append the port to the list of open ports.

        Args:
            port (Port)        : The port to be appended.
            force (bool | None): If set to True, will replace the existing port in the list wheither it already exists or not. Defaults to False.

        Raises:
            ValueError: If the provided port is neither an instance of Port nor an integer, a ValueError is raised.
        """

        if not self._is_port_in_list(port.number) or force:
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

        return IP.ip_int_to_str(self._address, self._version)

    def str_compress(self, compress: bool = True) -> str:
        """
        Return a compress string version of the current IP.

        If the version of the current IP is IPv4, it just returns the IP string
        If the version of the current IP is IPv6, it compresses its zeros

        Returns:
            str: The string representation of the current IP address, with compressed zeros if IPv6

        Example:
            ip = IP("2001:0:0:0:1A12:0:0:1A13")
            print(ip.compress()) => "2001::1A12:0:0:1A13"
        """

        if self._version == IPVersion.IPV4:
            return str(self)

        return IP.ip_int_to_str(self._address, compress=compress)

    # ****************************************************************
    # Static methods

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

    @staticmethod
    def _compress_ipv6(ip: int | str) -> str:
        """
        Return a compressed IPv6 string.

        The compression follows the 3 IPv6 compression rules:
        R1 - When only 0 (zero) is available in a field then it is removed from the IPv6 address notation
        R2 - When continuous 0s (zeros) are available in IPv6 address notation then all zeros are replaced by '::'
        R3 - When zeros are present in discontinuous places then, 0s (zeros) are replaced by '::' at only one junction

        Args:
            ip (int | str): An integer representation of the IPv6 address

        Returns:
            str: A string representation of the IPv6 address based on compression rules
        """

        if isinstance(ip, str):
            ip = IP.ip_str_to_int(ip, IPVersion.IPV6)

        groups = IP.ip_bytes(ip, IPVersion.IPV6)
        joined_ipv6 = ":".join(f"{g:x}" for g in groups)

        # Compressing IPv6
        longest_zero_suite = max(
            re.finditer(r"(?:^|:)(0(?::0)+)(?=:|$)", joined_ipv6),
            key=lambda m: len(m.group(1)) if m else 0,
            default=None,
        )

        if longest_zero_suite:
            suite_start, suite_end = longest_zero_suite.span()
            joined_ipv6 = joined_ipv6[:suite_start] + "::" + joined_ipv6[suite_end:]
            joined_ipv6 = re.sub(r"(:)\1+", r"\1\1", joined_ipv6)

        ip_str = joined_ipv6.lower()

        return ip_str

    @staticmethod
    def ip_str_to_int(ip: str, ip_version: "IPVersion" = IPVersion.IPV4) -> int:
        """
        Convert an IP address string into an integer.

        Args:
            ip (str)              : A string representing the IP address in dot-decimal notation.
            ip_version (IPVersion): The version of IP to use for conversion

        Returns:
            int: The equivalent integer representation of the IP address.
        """

        if re.match(ip_version.pattern, ip) is None:
            raise ValueError(
                f"{Context.caller_infos()['qualname']}::The provided IP {ip} does not match {ip_version} pattern"
            )

        ip_int: int
        if ip_version == IPVersion.IPV4:
            ip_int = int("".join([bin(int(x) + 256)[3:] for x in ip.split(".")]), 2)

        elif ip_version == IPVersion.IPV6:

            def expand_ipv6(addr: str) -> list[str]:
                if "::" in addr:
                    head, sep, tail = addr.partition("::")
                    head_parts = head.split(":") if head else []
                    tail_parts = tail.split(":") if tail else []
                    missing = 8 - (len(head_parts) + len(tail_parts))
                    new_parts = head_parts + (["0"] * missing) + tail_parts

                else:
                    new_parts = addr.split(":")

                return [part.zfill(4) for part in new_parts]

            ip_groups = expand_ipv6(ip.lower())
            ip_int = 0
            for g in ip_groups:
                ip_int = (ip_int << 16) + int(g, 16)

        return ip_int

    @staticmethod
    def ip_int_to_str(
        ip: int, ip_version: "IPVersion" = IPVersion.IPV4, compress: bool = True
    ) -> str:
        """
        Convert an IP address integer into a string.

        Args:
            ip (int)              : An integer representing the IP address.
            ip_version (IPVersion): The version of IP to use for conversion
            compress (bool)       : Whether to compress the IPv6

        Returns:
            str: The equivalent dot-decimal notation string of the IP address.
        """

        ip_str: str
        if ip_version == IPVersion.IPV4:
            ip_str = ".".join(map(str, IP.ip_bytes(ip, ip_version)))

        elif ip_version == IPVersion.IPV6:
            if compress:
                ip_str = IP._compress_ipv6(ip)

            else:
                groups = IP.ip_bytes(ip, IPVersion.IPV6)
                ip_str = ":".join(f"{g:x}" for g in groups).lower()

        return ip_str

    @staticmethod
    def ip_bytes(ip: int, ip_version: "IPVersion" = IPVersion.IPV4) -> list[int]:
        """
        Return a list of byte integer values based on a provided ip integer value and an IP version.

        The function returns a size variable list:
        If IPv4, a list of 4 byte integers
        If IPv6, a list of 8 byte integers

        Args:
            ip (int)              : An integer representation of an IP address
            ip_version (IPVersion): The IP version to use for the conversion

        Returns:
            list[int]: A list of IP bytes represented as integers (4 if IPv4, 8 if IPv6)
        """

        return [
            (
                ip >> (int(ip_version.bit_count / ip_version.byte_count) * i)
                & ip_version.max_byte_value
            )
            for i in range(ip_version.byte_count - 1, -1, -1)
        ]

    @staticmethod
    def ip_not(ip: int | str, ip_version: "IPVersion" = IPVersion.IPV4) -> int:
        """
        Do a NOT operation on an IP address.

        Args:
            ip (int)              : The IP address represented by an integer
            ip_version (IPVersion): The version of IP to use for conversion

        Returns:
            int: new ip address after the NOT operation
        """

        if isinstance(ip, str):
            ip = IP.ip_str_to_int(ip, ip_version)

        return LogicalOperator.NOT(ip) & ip_version.max_value

    @staticmethod
    def count_1_bits(val: int) -> int:
        """
        Count the number of bits set to 1 in the binary representation of an integer.

        This function takes an integer `val` and returns the count of bits that are set to 1 using its binary representation.

        Args:
            val (int): The integer to count the number of bits set to 1.

        Returns:
            int: The count of bits with value 1 in the given integer.
        """

        return bin(val).count("1")


class NetMask(IP):
    """Simple Class providing tools to manipulate IPv4 mask."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, mask: int | str) -> None:
        """
        Create a new instance of IPMask.

        This method initializes the object with either a CIDR notation value or an integer/string representation of a netmask.

        Args:
            mask (int | str): The netmask value as an integer or string.

        Raises:
            ValueError: If both `mask` and `cidr` are None, or if `cidr` is not between 1 and 32, or if `mask` is neither an integer nor a string.
        """

        if type(mask) is not int and type(mask) is not str:
            raise ValueError(
                f"{__class__.__name__}::Invalid mask provided : {mask}. You must provide a string or an integer !"
            )

        super().__init__(mask)

    # ****************************************************************
    # Methods

    @property
    def cidr(self) -> int:
        """
        Return the cidr notation of the current mask.

        Returns:
            int: current mask instance as CIDR notation
        """

        return IP.count_1_bits(self._address)

    @property
    def wildcard(self) -> IP:
        """
        Return mask wildcard.

        This method calculates and returns the wildcard address for the current network mask.

        Returns:
            IPv4: The wildcard address as an IPv4 object
        """

        return IP(IP.ip_not(self._address))

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
    def from_cidr(cidr: int) -> "NetMask":
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

        if not NetMask.check_cidr(cidr):
            raise ValueError(
                f"{__class__.__name__}.from_cidr::Mask CIDR value must be between 1 and 32!"
            )

        return NetMask(NetMask.cidr_to_mask_int(cidr))

    @staticmethod
    def netcidr(mask: str) -> int:
        """
        Return CIDR notation for a given mask.

        Args:
            mask (str): The netmask in string format.

        Returns:
            int: The CIDR notation of the provided netmask.

        Raises:
            ValueError: If the provided mask is not valid
        """

        if mask not in NetMask.valid_mask():
            raise ValueError(f"{__class__.__name__}.get_netcidr::Invalid mask provided: {mask}")

        return IP.count_1_bits(IP(mask).address)

    @staticmethod
    def cidr_to_mask_int(cidr: int, ip_version: "IPVersion" = IPVersion.IPV4) -> int:
        """
        Return a mask integer value based on the given network length.

        Args:
            cidr (int)            : The network prefix length from which to calculate the netmask.
            ip_version (IPVersion): The version of IP to use for conversion

        Returns:
            int: An integer representation of the netmask, based on the provided CIDR and IP version
        """

        if not (0 <= cidr <= ip_version.bit_count):
            raise ValueError(
                f"{Context.caller_infos()['qualname']}::Invalid cidr value provided. CIDR must be between 0 and {ip_version.bit_count}"
            )

        return (ip_version.max_value << (ip_version.bit_count - cidr)) & ip_version.max_value

    @staticmethod
    def valid_mask(ip_version: "IPVersion" = IPVersion.IPV4) -> list[str]:
        """
        List all valid netmask strings for CIDR notation.

        Returns:
            list[str]: A list of valid netmask strings
        """

        return list(map(NetMask.netmask, range(1, ip_version.bit_count + 1)))

    @staticmethod
    def netmask(network_length: int) -> str:
        """
        Return an ipv4 mask string based on a network length.

        Args:
            network_length (int): The length of the network in CIDR notation.

        Returns:
            str: The netmask as a string.

        Raises:
            ValueError: If the provided network length is not an integer or outside the range 1 to 32
        """

        return IP.ip_int_to_str(int(NetMask.from_cidr(network_length)))

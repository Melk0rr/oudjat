"""
A module that deals with subnet masks.
"""

from typing import Any, override

from oudjat.utils.context import Context

from .ip import IP
from .ipversions import IPVersion


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

        return IP.count_1_bits(self._value)

    @property
    def wildcard(self) -> "IP":
        """
        Return mask wildcard.

        This method calculates and returns the wildcard address for the current network mask.

        Returns:
            IPv4: The wildcard address as an IPv4 object
        """

        return IP(IP.ip_not(self._value))

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current net mask into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the current subnet mask
        """

        address_dict = super().to_dict()
        _ = address_dict.pop("ports")

        return {
            **address_dict,
            "cidr": self.cidr,
            "wildcard": self.wildcard
        }


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

        return IP.count_1_bits(IP(mask).value)

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
    def valid_mask() -> list[str]:
        """
        List all valid netmask strings for CIDR notation from 1 to 32.

        Returns:
            list[str]: A list of valid netmask strings
        """

        return list(map(NetMask.netmask, range(1, 33)))

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

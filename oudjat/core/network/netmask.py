"""
A module that deals with subnet masks.
"""

from typing import Any, override

from oudjat.utils.context import Context

from .exceptions import NetMaskInvalidCIDRError
from .ip import IP
from .ipversions import IPVersion


class NetMask(IP):
    """Simple Class providing tools to manipulate IPv4 mask."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, mask: int | str, ip_version: "IPVersion" = IPVersion.IPV4) -> None:
        """
        Create a new instance of NetMast.

        This method initializes the object with either a CIDR notation value or an integer/string representation of a netmask.

        Args:
            mask (int | str)      : The netmask value. If the value is an integer, it is expected to be a valid CIDR value.
            ip_version (IPVersion): The IP version

        Raises:
            ValueError: If both `mask` and `cidr` are None, or if `cidr` is not between 1 and 32, or if `mask` is neither an integer nor a string.
        """

        mask_addr = mask
        if isinstance(mask, int):
            if not NetMask.check_cidr(mask, ip_version):
                raise ValueError(
                    f"{Context()}::Invalid mask provided: {mask}. Mask integer value must be between 0 and {ip_version.bit_count}"
                )

            else:
                mask_addr = NetMask.cidr_to_mask_int(mask, ip_version)

        super().__init__(mask_addr)

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

        return {**address_dict, "cidr": self.cidr, "wildcard": self.wildcard}

    # ****************************************************************
    # Static methods

    @staticmethod
    def check_cidr(cidr: int, ip_version: "IPVersion" = IPVersion.IPV4) -> bool:
        """
        Return wheither or not the provided CIDR notation is correct.

        CIDR notation values must be between 0 and 32.

        Args:
            cidr (int)            : CIDR notation to check
            ip_version (IPVersion): The version of IP to use for conversion

        Returns:
            bool: True if the provided CIDR is valid. False otherwise
        """

        return 0 <= cidr <= ip_version.bit_count

    @staticmethod
    def from_cidr(cidr: int, ip_version: "IPVersion" = IPVersion.IPV4) -> "NetMask":
        """
        Create a new IPv4Mask instance based on a CIDR integer and IP version.

        Args:
            cidr (int)            : Net mask as a CIDR notation
            ip_version (IPVersion): The version of IP to use for conversion

        Returns:
            IPv4Mask: ipv4 mask instance based on the CIDR value provided

        Example:
            mask = IPv4Mask.from_cidr(24)
        """

        if not NetMask.check_cidr(cidr, ip_version):
            raise ValueError(
                f"{Context()}::Mask CIDR value must be between 0 and {ip_version.bit_count}!"
            )

        return NetMask(NetMask.cidr_to_mask_int(cidr, ip_version))

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
            raise ValueError(f"{Context()}.get_netcidr::Invalid mask provided: {mask}")

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

        if not NetMask.check_cidr(cidr, ip_version):
            raise NetMaskInvalidCIDRError(
                f"{Context()}::Invalid CIDR value provided. CIDR must be between 0 and {ip_version.bit_count}"
            )

        return (ip_version.max_value << (ip_version.bit_count - cidr)) & ip_version.max_value

    @staticmethod
    def valid_mask(ip_version: "IPVersion" = IPVersion.IPV4) -> list[str]:
        """
        List all valid netmask strings for CIDR notation from 1 to 32.

        Returns:
            list[str]: A list of valid netmask strings
        """

        def netmask(length: int) -> str:
            return NetMask.mask_str(length, ip_version)

        return list(map(netmask, range(1, ip_version.bit_count + 1)))

    @staticmethod
    def mask_str(network_length: int, ip_version: "IPVersion" = IPVersion.IPV4) -> str:
        """
        Return an IP net mask string based on a network length.

        Args:
            network_length (int)  : The length of the network in CIDR notation.
            ip_version (IPVersion): The version of IP to use for conversion

        Returns:
            str: The netmask as a string.
        """

        return IP.ip_int_to_str(int(NetMask.from_cidr(network_length, ip_version)))

"""A module that centralize package global variables."""

from oudjat.utils.logical_operations import LogicalOperation

URL_REGEX = r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

def ip_str_to_int(ip: str) -> int:
    """
    Convert an IP address string into an integer.

    Args:
        ip (str): A string representing the IP address in dot-decimal notation.

    Returns:
        int: The equivalent integer representation of the IP address.
    """

    return int("".join([bin(int(x) + 256)[3:] for x in ip.split(".")]), 2)


def ip_int_to_str(ip: int) -> str:
    """
    Convert an IP address integer into a string.

    Args:
        ip (int): An integer representing the IP address.

    Returns:
        str: The equivalent dot-decimal notation string of the IP address.
    """

    return ".".join([str((ip >> i) & 0xFF) for i in (24, 16, 8, 0)])


def cidr_to_int(cidr: int) -> int:
    """
    Return a mask integer value based on the given network length.

    Args:
        cidr (int): The network prefix length from which to calculate the netmask.

    Returns:
        int: The netmask as an integer, where bits 0-31 represent the mask.
    """

    return (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF


def ip_not(ip: int) -> int:
    """
    Do a NOT operation on an IP address.

    Args:
        ip (int): the IP address represented by an integer

    Returns:
        int: new ip address after the NOT operation
    """

    return LogicalOperation.logical_not(ip) & 0xFFFFFFFF


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


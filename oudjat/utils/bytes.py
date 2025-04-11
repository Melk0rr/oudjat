# INFO: Helper functions to handle bit operations


def i_not(val: int) -> int:
    """
    Performs a bitwise NOT operation on an integer.

    This function takes an integer `val` and returns its bitwise NOT result, ensuring that it wraps around using a 32-bit unsigned representation by applying the mask 0xFFFFFFFF.

    Args:
        val (int): The integer to perform the bitwise NOT on.

    Returns:
        int: The result of the bitwise NOT operation wrapped in a 32-bit unsigned format.
    """

    return ~val & 0xFFFFFFFF


def i_and(val1: int, val2: int) -> int:
    """
    Performs a bitwise AND operation on two integers.

    This function takes two integers `val1` and `val2` and returns the result of their bitwise AND operation.

    Args:
        val1 (int): The first integer for the bitwise AND operation.
        val2 (int): The second integer for the bitwise AND operation.

    Returns:
        int: The result of the bitwise AND operation between `val1` and `val2`.
    """

    return val1 & val2


def i_or(val1: int, val2: int) -> int:
    """
    Performs a bitwise OR operation on two integers.

    This function takes two integers `val1` and `val2` and returns the result of their bitwise OR operation.

    Args:
        val1 (int): The first integer for the bitwise OR operation.
        val2 (int): The second integer for the bitwise OR operation.

    Returns:
        int: The result of the bitwise OR operation between `val1` and `val2`.
    """

    return val1 | val2


def i_xor(val1: int, val2: int) -> int:
    """
    Performs a bitwise XOR operation on two integers.

    This function takes two integers `val1` and `val2` and returns the result of their bitwise XOR operation.

    Args:
        val1 (int): The first integer for the bitwise XOR operation.
        val2 (int): The second integer for the bitwise XOR operation.

    Returns:
        int: The result of the bitwise XOR operation between `val1` and `val2`.
    """

    return val1 ^ val2


def count_1_bits(val: int) -> int:
    """
    Counts the number of bits set to 1 in the binary representation of an integer.

    This function takes an integer `val` and returns the count of bits that are set to 1 using its binary representation.

    Args:
        val (int): The integer to count the number of bits set to 1.

    Returns:
        int: The count of bits with value 1 in the given integer.
    """

    return bin(val).count("1")

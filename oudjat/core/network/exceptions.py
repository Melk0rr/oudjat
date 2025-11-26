"""
A helper module to define IP specific exceptions.
"""


class NetMaskInvalidCIDRError(ValueError):
    """
    A helper class to handle invalid CIDR value errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of NetMaskInvalidCIDRError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

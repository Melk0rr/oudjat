"""
A helper module to define SCCM specific errors.
"""


class SCCMServerConnectionError(ConnectionError):
    """
    A helper class to handle an SCCM connection error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of SCCMServerConnectionError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class SCCMQueryError(Exception):
    """
    A helper class to handle an SCCM query error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of SCCMQueryError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

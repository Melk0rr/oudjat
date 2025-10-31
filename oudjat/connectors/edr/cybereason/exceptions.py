"""
A helper module to declare some useful exceptions.
"""


class CybereasonAPIRequestError(Exception):
    """
    A helper error class to handle request errors to the Cybereason API.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of CybereasonAPIRequestError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class CybereasonAPIConnectionError(ConnectionError):
    """
    A helper error class to handle request errors to the Cybereason API.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of CybereasonAPIRequestError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

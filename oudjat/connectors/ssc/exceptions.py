"""
A helper module to define Security Score Card exceptions.
"""

class SSCAPIConnectionError(ConnectionError):
    """
    A helper error class to handle request errors to the SSC API.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of SSCAPIConnectionError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

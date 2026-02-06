"""
A helper module to define S1 exceptions.
"""

class SentinelOneAPIConnectionError(ConnectionError):
    """
    A helper error class to handle request errors to the SentinelOne API.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of SentinelOneAPIConnectionError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

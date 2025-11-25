"""
A helper module to define CVE connectors specific errors.
"""


class CVEDatabaseConnectionError(ConnectionError):
    """
    A helper class to handle a CVE database connection error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of CVEDatabaseConnectionError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


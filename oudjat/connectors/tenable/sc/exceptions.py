"""
A helper module to define tenable.sc specific errors.
"""


class TenableSCConnectionError(ConnectionError):
    """
    A helper class to handle a TenableSC API connection error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of TenableSCConnectionError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class TenableSCInvalidAnalysisTool(ValueError):
    """
    A helper class to handle a TenableSC invalid analysis tool value.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of TenableSCInvalidAnalysisTool.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

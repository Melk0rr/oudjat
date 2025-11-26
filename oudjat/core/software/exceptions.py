"""
A helper module to define asset exceptions.
"""


class SoftwareReleaseSupportInvalidEndDate(ValueError):
    """
    A helper class to handle invalid SoftwareSupport end date.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of SoftwareSupportInvalidEndDate.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


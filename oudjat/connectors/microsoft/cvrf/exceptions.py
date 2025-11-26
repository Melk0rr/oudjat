"""
A helper module to define asset exceptions.
"""


class InvalidCVRFProductError(ValueError):
    """
    A helper class to handle invalid CVRF product id errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of InvalidCVRFProductError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


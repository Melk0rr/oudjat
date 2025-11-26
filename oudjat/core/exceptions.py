"""
A helper module to define asset exceptions.
"""


class CustomAttributeError(ValueError):
    """
    A helper class to handle invalid custom attribute errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of CustomAttributeError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class InvalidAssetTypeError(ValueError):
    """
    A helper class to handle invalid asset type errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of InvalidAssetTypeError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

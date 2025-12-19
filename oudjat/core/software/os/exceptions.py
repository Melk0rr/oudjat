"""
A helper module to define OS exceptions.
"""


class NotImplementedOSOption(KeyError):
    """
    A helper class to handle not implemented os option.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of NotImplementedOSOption.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

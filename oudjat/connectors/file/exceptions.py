"""
A helper module to declare FileConnector specifig exceptions.
"""


class FileTypeError(ValueError):
    """
    A helper error class to handle file type errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of FileTypeError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

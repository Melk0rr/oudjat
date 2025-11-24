"""
A helper module to define CERTFR exceptions.
"""

class CERTFRParsingError(Exception):
    """
    A helper class to handle the absence of credentials.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of NoCredentialsError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class CERTFRReferenceError(Exception):
    """
    A helper class to handle the absence of credentials.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of NoCredentialsError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class CERTFRInvalidLinkError(Exception):
    """
    A helper class to handle the absence of credentials.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of NoCredentialsError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

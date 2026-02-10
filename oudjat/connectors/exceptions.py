"""
A helper module to define shared Connector exceptions.
"""

from oudjat.utils.credentials import InvalidCredentialsError


class ConnectorCredentialError(InvalidCredentialsError):
    """
    A helper error class to handle the absence of credentials for a connector when performing a connect operation.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of ConnectorCredentialError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

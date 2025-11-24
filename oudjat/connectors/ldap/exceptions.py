"""
A helper module to define LDAP specific errors.
"""


class LDAPInvalidEntryError(ValueError):
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

class LDAPConnectionError(ConnectionError):
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

class LDAPUnreachableServerError(LDAPConnectionError):
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

class LDAPSchemaError(LDAPConnectionError):
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

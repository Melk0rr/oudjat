"""
A helper module to define LDAP specific errors.
"""


class InvalidLDAPEntryError(ValueError):
    """
    A helper class to handle an invalid LDAP entry error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of InvalidLDAPEntryError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class LDAPConnectionError(ConnectionError):
    """
    A helper class to handle an LDAP connection error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of LDAPConnectionError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class LDAPUnreachableServerError(LDAPConnectionError):
    """
    A helper class to handle an unreachable LDAP server error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of LDAPUnreachableServerError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class LDAPSchemaError(LDAPConnectionError):
    """
    A helper class to handle an LDAP schema error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of LDAPSchemaError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class InvalidLDAPFilterString(ValueError):
    """
    A helper class to handle an invalid LDAP filter string.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of InvalidLDAPFilterString.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class InvalidLDAPFilterCmpOperator(ValueError):
    """
    A helper class to handle an invalid LDAP filter comparison operator.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of InvalidLDAPFilterCmpOperator.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

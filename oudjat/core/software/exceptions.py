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

class SoftwareReleaseVersionSplittingError(ValueError):
    """
    A helper class to handle errors occuring while trying to split a software release version string.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of SoftwareReleaseVersionSplittingError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class InvalidSoftwareVersionError(ValueError):
    """
    A helper class to handle invalid software version errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of InvalidSoftwareVersionError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class UnknownSoftwareReleaseVersionError(KeyError):
    """
    A helper class to handle unknown software release version errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of UnknownSoftwareReleaseVersionError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class EmptyReleaseCandidatesError(ValueError):
    """
    A helper class to handle empty SoftwareReleaseResolver candidates error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of EmptyReleaseCandidatesError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class AmbiguousReleaseException(Exception):
    """
    A helper class to handle ambiguous SoftwareRelease resolution.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of AmbiguousReleaseException.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

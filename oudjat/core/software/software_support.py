"""A module that describes the notion of software support."""

from datetime import datetime
from enum import IntEnum
from typing import TypedDict, override

from oudjat.utils.time_utils import TimeConverter


class SoftwareReleaseSupportDetailsDict(TypedDict):
    """
    A helper class to properly handle SoftwareReleaseSupport details dictionary types.

    Attributes:
        start (str)   : Details about the start of the support
        end (str)     : Details about the end of the support
        duration (int): Duration of the support
    """

    start: str
    end: str
    duration: int

class SoftwareReleaseSupportDict(TypedDict):
    """
    A helper class to properly handle support dictionary types.

    Attributes:
        channel (str)                       : The support channel of the support
        supportFrom (str)                   : The start date of the support
        activeSupport (str)                 : The activeSupport date as a string
        securitySupport (str)               : The securitySupport date as a string
        extendedSecuritySupport (str | None): The extendedSecuritySupport date as a string
        status (str)                        : The support status (SoftwareReleaseSupportStatus) as a string
        lts (bool)                          : Whether the support is LTS or not
        details (str)                       : Support details string
    """

    channel: str
    supportFrom: str
    activeSupport: str
    securitySupport: str
    extendedSecuritySupport: str | None
    status: str
    lts: bool
    details: "SoftwareReleaseSupportDetailsDict"


class SoftwareReleaseSupportStatus(IntEnum):
    """
    A simple enumeration to handle software release support status.

    Attributes:
        RETIRED: The release support is retired
        ONGOING: The release support is still ongoing
    """

    UPCOMING = -1
    RETIRED = 0
    ONGOING = 1

    @override
    def __str__(self) -> str:
        """
        Convert a SoftwareReleaseSupportStatus into a string.

        Returns:
            str: A string representation of the support status
        """

        return self._name_


class SoftwareReleaseSupport:
    """A class to handle software release support concept."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        channel: str,
        support_from: str | datetime,
        active_support: str | datetime,
        security_support: str | datetime | None = None,
        extended_security_support: str | datetime | None = None,
        long_term_support: bool = False,
    ) -> None:
        """
        Create a new instance SoftwareReleaseSupport.

        Args:
            channel (str)                                    : The support channel name
            support_from (str | datetime)                    : The start date of the support
            active_support (str | datetime | None)           : The date when regular support ends. Can be a string with 'YYYY-MM-DD' format.
            security_support (str | datetime | None)         : The date when security support ends. Can be a string with 'YYYY-MM-DD' format.
            extended_security_support (str | datetime | None): The date when extended security support ends. Can be a string with 'YYYY-MM-DD' format.
            edition (list[str] | None)                       : A list of software editions supported by the release.
            long_term_support (bool | None)                  : Whether the release has long term support.
        """

        self._channel: str = channel
        self._support_from: datetime = SoftwareReleaseSupport._support_date_fmt(support_from)

        if security_support is None:
            security_support = active_support

        # Handling none support values
        self._active_support: datetime = SoftwareReleaseSupport._support_date_fmt(active_support)
        self._security_support: datetime = SoftwareReleaseSupport._support_date_fmt(
            security_support
        )

        self._extended_security_support: datetime | None = None
        if extended_security_support is not None:
            self._extended_security_support = SoftwareReleaseSupport._support_date_fmt(
                extended_security_support
            )

        self._lts: bool = long_term_support

    # ****************************************************************
    # Methods

    @property
    def status(self) -> "SoftwareReleaseSupportStatus":
        """
        Return a string representing the current support status.

        Returns:
            str: "Ongoing" if support is ongoing, otherwise "Retired".
        """

        if TimeConverter.days_diff(self._support_from) < 0:
            return SoftwareReleaseSupportStatus.UPCOMING

        return SoftwareReleaseSupportStatus(int(self.is_ongoing))

    @property
    def is_ongoing(self) -> bool:
        """
        Check if the current support period is ongoing.

        Returns:
            bool: True if the support period is ongoing, False otherwise.
        """

        return (
            TimeConverter.days_diff(self._support_from) > 0
            and TimeConverter.days_diff(self._security_support, reverse=True) > 0
        )

    @property
    def duration(self) -> int:
        """
        Return how long the support is ongoing.

        Returns:
            int: The number of support days
        """

        return (self._security_support - self._support_from).days

    @property
    def support_details(self) -> "SoftwareReleaseSupportDetailsDict":
        """
        Return some details about the start and end of the support.

        Returns:
            dict[str, str]: A dictionary with start and end details
        """

        from_days = TimeConverter.days_diff(self._support_from)
        start = f"{abs(from_days)} days"
        start = f"Started {start} ago" if from_days > 0 else f"Starts in {start}"

        support_days = TimeConverter.days_diff(self._security_support, reverse=True)
        end = f"{abs(support_days)} days"
        end = f"Ends in {end}" if support_days > 0 else f"Ended {end} ago"

        return {
            "start": start,
            "end": end,
            "duration": self.duration
        }

    @property
    def lts(self) -> bool:
        """
        Check if the release has long term support.

        Returns:
            bool: True if the release has long term support, False otherwise.
        """

        return self._lts

    @override
    def __str__(self) -> str:
        """
        Convert the current support instance into a string.

        Returns:
            str: a string representing the software support
        """

        return f"{self.status}{' - LTS' if self._lts else ''}"

    def to_dict(self) -> "SoftwareReleaseSupportDict":
        """
        Convert the current support instance into a dict.

        Returns:
            dict : dictionary containing software support key attributes
        """

        esu = (
            TimeConverter.date_to_str(self._security_support)
            if self._extended_security_support
            else None
        )

        return {
            "channel": self._channel,
            "supportFrom": TimeConverter.date_to_str(self._support_from),
            "activeSupport": TimeConverter.date_to_str(self._active_support),
            "securitySupport": TimeConverter.date_to_str(self._security_support),
            "extendedSecuritySupport": esu,
            "status": str(self.status),
            "lts": self._lts,
            "details": self.support_details,
        }

    # ****************************************************************
    # Class methods

    @classmethod
    def from_dict(cls, support_dict: "SoftwareReleaseSupportDict") -> "SoftwareReleaseSupport":
        """
        Create a new instance of SoftwareReleaseSupport from a dictionary.

        The provided dictionary must follow the SoftwareReleaseSupportDict model

        Args:
            support_dict (SoftwareReleaseSupportDict): The dictionary the new instance will be based on

        Returns:
            SoftwareReleaseSupport: A new instance of SoftwareReleaseSupport based on the provided dictionary
        """

        return cls(
            channel=support_dict["channel"],
            support_from=support_dict["supportFrom"],
            active_support=support_dict["activeSupport"],
            security_support=support_dict["securitySupport"],
            extended_security_support=support_dict["extendedSecuritySupport"],
            long_term_support=support_dict["lts"],
        )

    # ****************************************************************
    # Static methods

    @staticmethod
    def _support_date_fmt(date_to_fmt: str | datetime) -> datetime:
        """
        Format the provided date as a datetime if needed.

        Args:
            date_to_fmt (str | datetime): The date to format if needed

        Returns:
            datetime: Formated datetime
        """

        return (
            TimeConverter.str_to_date(date_to_fmt)
            if not isinstance(date_to_fmt, datetime)
            else date_to_fmt
        )

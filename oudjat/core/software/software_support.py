"""A module that describes the notion of software support."""

from datetime import datetime
from enum import IntEnum
from typing import TypedDict, override

from oudjat.utils.time import TimeConverter


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
        channel (str)       : The support channel of the support
        start   (str)       : The start date of the support
        eoas    (str)       : The activeSupport date as a string
        eol     (str)       : The securitySupport date as a string
        eoes    (str | None): The extendedSecuritySupport date as a string
        status  (str)       : The support status (SoftwareReleaseSupportStatus) as a string
        details (str)       : Support details string
    """

    channel: str
    start: str
    eoas: str
    eol: str
    eoes: str | None
    status: str
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
        start: str | datetime,
        eoas: str | datetime,
        eol: str | datetime | None = None,
        eoes: str | datetime | None = None,
    ) -> None:
        """
        Create a new instance SoftwareReleaseSupport.

        Args:
            channel (str)                  : The support channel name
            start   (str | datetime)       : The start date of the support
            eoas    (str | datetime | None): The date when regular support ends. Can be a string with 'YYYY-MM-DD' format.
            eol     (str | datetime | None): The date when security support ends. Can be a string with 'YYYY-MM-DD' format.
            eoes    (str | datetime | None): The date when extended security support ends. Can be a string with 'YYYY-MM-DD' format.
        """

        self._channel: str = channel
        self._start: datetime = SoftwareReleaseSupport._support_date_fmt(start)

        if eol is None:
            eol = eoas

        self._eoas: datetime = SoftwareReleaseSupport._support_date_fmt(eoas)
        self._eol: datetime = SoftwareReleaseSupport._support_date_fmt(eol)

        self._eoes: datetime | None = None
        if eoes is not None:
            self._eoes = SoftwareReleaseSupport._support_date_fmt(eoes)

    # ****************************************************************
    # Methods

    @property
    def channel(self) -> str:
        """
        Return the support channel name.

        Returns:
            str: The name of the channel associated with the current support
        """

        return self._channel

    @property
    def status(self) -> "SoftwareReleaseSupportStatus":
        """
        Return the current support status

        - UPCOMING: the support has not started yet
        - ONGOING : the support is still ongoing
        - RETIRED : the support has ended

        Returns:
            SoftwareReleaseSupportStatus: The current status of the support as a SoftwareReleaseSupportStatus enum element
        """

        if TimeConverter.days_diff(self._start) < 0:
            return SoftwareReleaseSupportStatus.UPCOMING

        status = SoftwareReleaseSupportStatus.RETIRED

        if (
            TimeConverter.days_diff(self._eol) < 0
            or self._eoes is not None
            and TimeConverter.days_diff(self._eoes) < 0
        ):
            status = SoftwareReleaseSupportStatus.ONGOING

        return status

    @property
    def is_ongoing(self) -> bool:
        """
        Check if the current support period is ongoing.

        Returns:
            bool: True if the support period is ongoing, False otherwise.
        """

        return self.status is SoftwareReleaseSupportStatus.ONGOING

    @property
    def duration(self) -> int:
        """
        Return for how long the support is ongoing.

        Returns:
            int: The number of support days
        """

        return (self._eol - self._start).days

    @property
    def support_details(self) -> "SoftwareReleaseSupportDetailsDict":
        """
        Return some details about the start and end of the support.

        Returns:
            dict[str, str]: A dictionary with start and end details
        """

        from_days = TimeConverter.days_diff(self._start)
        start = f"{abs(from_days)} days"
        start = f"Started {start} ago" if from_days > 0 else f"Starts in {start}"

        support_days = TimeConverter.days_diff(self._eol, reverse=True)
        end = f"{abs(support_days)} days"
        end = f"Ends in {end}" if support_days > 0 else f"Ended {end} ago"

        return {"start": start, "end": end, "duration": self.duration}

    @property
    def is_lts(self) -> bool:
        """
        Check if the release has long term support.

        Returns:
            bool: True if the release has long term support, False otherwise.
        """

        return self._eoes is not None and TimeConverter.days_diff(self._eoes) > 0

    @override
    def __str__(self) -> str:
        """
        Convert the current support instance into a string.

        Returns:
            str: a string representing the software support
        """

        return str(self.status)

    def to_dict(self) -> "SoftwareReleaseSupportDict":
        """
        Convert the current support instance into a dict.

        Returns:
            SoftwareReleaseSupportDict: dictionary containing software support key attributes
        """

        esu = TimeConverter.date_to_str(self._eol) if self._eoes else None

        return {
            "channel": self._channel,
            "start": TimeConverter.date_to_str(self._start),
            "eoas": TimeConverter.date_to_str(self._eoas),
            "eol": TimeConverter.date_to_str(self._eol),
            "eoes": esu,
            "status": str(self.status),
            "details": self.support_details,
        }

    # ****************************************************************
    # Class methods

    @classmethod
    def from_dict(
        cls, support_dict: "SoftwareReleaseSupportDict"
    ) -> "SoftwareReleaseSupport":
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
            start=support_dict["start"],
            eoas=support_dict["eoas"],
            eol=support_dict["eol"],
            eoes=support_dict["eoes"],
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

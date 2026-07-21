"""A module that describes the notion of software support."""

from datetime import datetime, timezone
from enum import IntEnum
from typing import Any, TypedDict, override

from oudjat.utils.time import TimeConverter


class SupportDetailsDict(TypedDict):
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


class SupportDict(TypedDict):
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
    details: "SupportDetailsDict"


class SupportPhaseType(IntEnum):
    ACTIVE_SUPPORT = 0
    SECURITY_SUPPORT = 1
    EXTENDED_SUPPORT = 2

    def __str__(self) -> str:
        """
        Convert a PhaseType element into a string.

        Returns:
            str: A string representation of the PhaseType
        """

        return self._name_


class SupportStatus(IntEnum):
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


class SupportPhase:
    """A class that describes a phase of the support of a software release."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        phase_type: "SupportPhaseType",
        start: str | datetime,
        end: str | datetime,
        name: str = "",
    ) -> None:
        """
        Create a new instance of SupportPhase.

        Args:
            phase_type (SupportPhaseType): The type of the phase
            start      (str | datetime)  : The start of the phase
            end        (str | datetime)  : The end of the phase
            name       (str)             : The name of the phase
        """

        self._type = phase_type
        self._name = name

        self._start: datetime = SoftwareReleaseSupport._support_date_fmt(start)
        self._end: datetime = SoftwareReleaseSupport._support_date_fmt(end)

    # ****************************************************************
    # Methods

    @property
    def duration(self) -> int:
        """
        Return the duration in days of the current support phase.

        Returns:
            int: The number of days the phase lasts
        """

        return (self._end - self._start).days

    @property
    def status(self) -> "SupportStatus":
        """
        Return the status of the current support phase.

        Returns:
            SupportStatus: UPCOMING if the support phase has not started yet. RETIRED if it ended. Otherwise, ONGOING
        """

        today = datetime.now(timezone.utc)

        if today < self._start:
            status = SupportStatus.UPCOMING

        elif today > self._end:
            status = SupportStatus.RETIRED

        else:
            status = SupportStatus.ONGOING

        return status

    @property
    def is_ongoing(self) -> bool:
        """
        Check if the current support phase is ongoing.

        Returns:
            bool: True if the support phase is ongoing, False otherwise.
        """

        return self.status is SupportStatus.ONGOING

    @property
    def description(self) -> str:
        """
        Return a brief description of the phase.

        Returns:
            str: A string that describes the status of the phase.
        """

        today = datetime.now(timezone.utc)

        if today <= self._start:
            delta = TimeConverter.days_diff(self._start)
            description = f"Starts in {abs(delta)} days"

        else:
            delta = TimeConverter.days_diff(self._end, reverse=True)
            delta_str = f"{abs(delta)} days"
            description = (
                f"Ends in {delta_str}" if delta > 0 else f"Ended {delta_str} ago"
            )

        return description

    @override
    def __str__(self) -> str:
        """
        Convert the current support phase instance into a string.

        Returns:
            str: a string representing the software support
        """

        return str(self.status)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": str(self._type),
            "name": self._name,
            "start": TimeConverter.date_to_str(self._start),
            "end": TimeConverter.date_to_str(self._end),
            "status": str(self),
            "description": self.description,
        }


class SupportPhaseDict:
    """A class to handle software release support concept."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, name: str) -> None:
        """
        Create a new instance SoftwareReleaseSupport.

        Args:
            name (str): The name of the channel
        """

        self._phases: dict[str, "SupportPhase"] = {}

    # ****************************************************************
    # Methods

    @property
    def status(self, hasExtendedSupport: bool = False) -> "SupportStatus":
        """
        Return the current support status.

        - UPCOMING: the support has not started yet
        - ONGOING : the support is still ongoing
        - RETIRED : the support has ended

        Returns:
            SoftwareReleaseSupportStatus: The current status of the support as a SoftwareReleaseSupportStatus enum element
        """

    @property
    def is_ongoing(self) -> bool:
        """
        Check if the current support period is ongoing.

        Returns:
            bool: True if the support period is ongoing, False otherwise.
        """

        return self.status is SupportStatus.ONGOING

    @property
    def duration(self) -> int:
        """
        Return for how long the support is ongoing.

        Returns:
            int: The number of support days
        """

        return (self._eol - self._start).days

    @property
    def has_extended_support(self) -> bool:
        """
        Return wheither the current support has an extended period available.

        The extended support is usually a period of the support that comes at a cost.
        During this period some critical security updates and bugfixes are distributed by the editor (depending on the software).

        Args:
            argument_name: type and description.

        Returns:
            bool: True, the support include an extended period. False otherwise
        """

        return str(SupportPhaseType.EXTENDED) in self._phases

    @property
    def is_lts(self) -> bool:
        """
        Check if the release has long term support.

        Returns:
            bool: True if the release has long term support, False otherwise.
        """

        return (
            self.has_extended_support
            and self._phases[str(SupportPhaseType.EXTENDED)].is_ongoing
        )

    @override
    def __str__(self) -> str:
        """
        Convert the current support instance into a string.

        Returns:
            str: a string representing the software support
        """

        return str(self.status)

    def to_dict(self) -> "dict[str, Any]":
        """
        Convert the current support instance into a dict.

        Returns:
            SoftwareReleaseSupportDict: dictionary containing software support key attributes
        """

        phase_dicts = {k: v.to_dict() for k, v in self._phases.items()}

        return {
            "phases": phase_dicts,
            "status": str(self.status),
            "details": self.details,
        }

    # ****************************************************************
    # Class methods

    @classmethod
    def from_dict(cls, support_dict: "SupportDict") -> "SoftwareReleaseSupport":
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

"""A module that describes the notion of software support."""

import logging
from collections.abc import Iterator
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any, TypedDict, override

from oudjat.utils import Context
from oudjat.utils.time import TimeConverter

from .exceptions import (
    EmptySupportPhasesError,
    InvalidSupportPhasesError,
)

type SupportDictProps = dict[str, "SupportPhaseProps"]


class SupportPhaseProps(TypedDict):
    """
    A helper class to properly handle SoftwareReleaseSupport details dictionary types.

    Attributes:
        type  (str): The type of the phase. Must match a SupportPhaseType.
        start (str): Details about the start of the support.
        end   (str): Details about the end of the support.
        name  (str): The name of the phase
    """

    type: "str | SupportPhaseType"
    start: str
    end: str
    label: str


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
        label: str = "",
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
        self._label = label

        self._start: datetime = self._date_fmt(start)
        self._end: datetime = self._date_fmt(end)

    # ****************************************************************
    # Properties

    @property
    def type(self) -> "SupportPhaseType":
        """
        Return the type of the current phase.

        Returns:
            SupportPhaseType: The type of the current phase
        """

        return self._type

    @property
    def label(self) -> "str":
        """
        Return the name of the current support phase.

        Returns:
            str: The name of the current phase
        """

        return self._label

    @property
    def start(self) -> datetime:
        """
        Return the start date of the current phase.

        Returns:
            datetime: A datetime object that corresponds to the phase start date.
        """

        return self._start

    @property
    def end(self) -> datetime:
        """
        Return the end date of the current phase.

        Returns:
            datetime: A datetime object that corresponds to the phase end date.
        """

        return self._end

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

        today = datetime.now(UTC)

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
    def is_retired(self) -> bool:
        """
        Check if the current support phase is retired.

        Returns:
            bool: True if the support phase is retired, False otherwise.
        """

        return self.status is SupportStatus.RETIRED

    @property
    def starts_in(self) -> int:
        """
        Return the number of days between the current date and the start of the support.

        Returns:
            int: The number of days in which the support starts.
        """

        return TimeConverter.days_diff(self._start, reverse=True)

    @property
    def ends_in(self) -> int:
        """
        Return the number of days between the current date and the end of the support.

        Returns:
            int: The number of days in which the support ends.
        """

        return TimeConverter.days_diff(self._end, reverse=True)

    @property
    def description(self) -> str:
        """
        Return a brief description of the phase.

        Returns:
            str: A string that describes the status of the phase.
        """

        today = datetime.now(UTC)

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

    # ****************************************************************
    # Methods

    def __gt__(self, other: "SupportPhase") -> bool:
        """
        Check if the current phase is greater than another.

        The comparison relies on the phase type.

        Args:
            other (SupportPhase): The other phase to compare to the current one.

        Returns:
            bool: True if the current phase is greater than the other one. False otherwise.
        """

        return self.type > other.type

    def __lt__(self, other: "SupportPhase") -> bool:
        """
        Check if the current phase is lower than another.

        The comparison relies on the phase type.

        Args:
            other (SupportPhase): The other phase to compare to the current one.

        Returns:
            bool: True if the current phase is lower than the other one. False otherwise.
        """

        return self.type < other.type

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": str(self._type),
            "label": self._label,
            "start": TimeConverter.date_to_str(self._start),
            "end": TimeConverter.date_to_str(self._end),
            "status": str(self),
            "startsIn": self.starts_in,
            "endsIn": self.ends_in,
            "description": self.description,
        }

    # ****************************************************************
    # Static methods

    @classmethod
    def from_dict(cls, phase_dict: "SupportPhaseProps") -> "SupportPhase":
        """
        Create a new instance of SoftwareReleaseSupport from a dictionary.

        The provided dictionary must follow the SoftwareReleaseSupportDict model

        Args:
            support_dict (SoftwareReleaseSupportDict): The dictionary the new instance will be based on

        Returns:
            SoftwareReleaseSupport: A new instance of SoftwareReleaseSupport based on the provided dictionary
        """

        p_type = phase_dict["type"]
        if isinstance(p_type, str):
            if p_type not in SupportPhaseType._member_names_:
                raise ValueError(
                    f"{Context()}::Invalid phase type provided {phase_dict['type']}"
                )

            p_type = SupportPhaseType[p_type]

        return cls(
            phase_type=p_type,
            start=phase_dict["start"],
            end=phase_dict["end"],
            label=phase_dict["label"],
        )

    # ****************************************************************
    # Static methods

    @staticmethod
    def _date_fmt(date_to_fmt: str | datetime) -> datetime:
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


class Support:
    """A class to handle software release support concept."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self) -> None:
        """
        Create a new instance of SupportPhaseDict.

        Args:
            name (str): The name of the channel
        """

        self.logger: logging.Logger = logging.getLogger(__name__)
        self._phases: dict[str, SupportPhase] = {}

    # ****************************************************************
    # Helper methods

    def _relevent_phases(
        self, include_extended_support: bool = False
    ) -> list["SupportPhase"]:
        """
        Return a list of current phases inluding or not the extended support phase based on parameter.

        Args:
            include_extended_support (bool): Whether or not to include the extended support phase in the list

        Returns:
            list[SupportPhase]: A list of SupportPhase instances based on the current phases and parameter.
        """

        base = self._phases.copy()

        if (
            not include_extended_support
            and f"{SupportPhaseType.EXTENDED_SUPPORT}" in base
        ):
            _ = base.pop(f"{SupportPhaseType.EXTENDED_SUPPORT}")

        relevent = sorted(base.values())

        return relevent

    def _validate_phases(self) -> None:
        """
        Perform some checks on current support phases.

        Ensures that:
            - Phases are not empty.
            - If there is only one phase, that it is not extended support.
        """

        context = Context()

        if len(self._phases) == 0:
            raise EmptySupportPhasesError(f"{context}::No support phases set")

        if (
            str(SupportPhaseType.EXTENDED_SUPPORT) in self._phases
            and len(self._phases) == 1
        ):
            raise InvalidSupportPhasesError(
                f"{context}::Can't have only an extended support phase"
            )

    def _check_phase(self, phase_type: SupportPhaseType) -> bool:
        """
        Return whether support includes a phase of the provided type.

        Args:
            phase_type (SupportPhaseType): SupportPhaseType to check in current support phases.

        Returns:
            bool: True if the support has a phase of the provided type. False otherwise.
        """

        return str(phase_type) in self._phases

    # ****************************************************************
    # Properties

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

        return self._check_phase(SupportPhaseType.EXTENDED_SUPPORT)

    @property
    def is_lts(self) -> bool:
        """
        Check if the support is currently in a phase of extended support.

        Returns:
            bool: True if support is in extended support. False otherwise.
        """

        return (
            self.has_extended_support
            and self._phases[str(SupportPhaseType.EXTENDED_SUPPORT)].is_ongoing
        )

    @property
    def is_eoas(self) -> bool:
        """
        Checks if the support has ended its active support phase.

        Returns:
            bool: True if the active support phase is over. False otherwise.
        """

        return (
            self._check_phase(SupportPhaseType.ACTIVE_SUPPORT)
            and self._phases[str(SupportPhaseType.ACTIVE_SUPPORT)].is_retired
        )

    @property
    def is_eol(self) -> bool:
        """
        Checks if the support has ended its security support phase.

        Returns:
            bool: True if the security support phase is over. False otherwise.
        """

        return (
            self._check_phase(SupportPhaseType.SECURITY_SUPPORT)
            and self._phases[str(SupportPhaseType.SECURITY_SUPPORT)].is_retired
        )

    @property
    def is_eoes(self) -> bool:
        """
        Checks if the support has ended its extended support phase.

        Returns:
            bool: True if the extended support phase is over. False otherwise.
        """

        return (
            self._check_phase(SupportPhaseType.EXTENDED_SUPPORT)
            and self._phases[str(SupportPhaseType.EXTENDED_SUPPORT)].is_retired
        )

    # ****************************************************************
    # Methods

    def __getitem__(self, key: str) -> "SupportPhase":
        """
        Return a SupportPhase based on its key.

        Args:
            key (str): A phase type name

        Returns:
            SupportPhase: The support phase based on the provided phase type name
        """

        return self._phases[key]

    def __setitem__(self, key: str, value: "SupportPhase") -> None:
        """
        Set a new support phase based on a key

        Args:
            key (str)          : The support phase type
            value (ReleaseType): Value of the new element
        """

        if key in SupportPhaseType._member_names_:
            self._phases[key] = value

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator to go through the SoftwareRelEditionDict instances.

        Returns:
            Iterator[str]: iterator object
        """

        return iter(self._phases)

    def add(self, phase: "SupportPhase", force: bool = False) -> None:
        """
        Add a new release for the provided version key.

        The method checks if a similar release (based on ID) already exists for the provided version key.
        If force argument is set to True, the new release will be added regardless.

        Args:
            key (str)            : The key of the new release
            release (ReleaseType): The new release to add
            force (bool)         : Whether to force the addition of the new release
        """

        key = str(phase.type)

        if force or key not in self._phases:
            self._phases[key] = phase

        else:
            self.logger.warning(
                f"A support phase with type ({phase.type}) already exists"
            )

    def get(self, key: str, default_value: Any = None) -> "SupportPhase | Any":
        """
        Return a SoftwareRelEditionDict element based on its key.

        If the element cannot be found, return the default value.

        Args:
            key (str)          : Key of the element to return
            default_value (Any): Default value in case the element cannot be found

        Returns:
            list[ReleaseType] | None: Element associated with provided key or default value

        """

        return self._phases.get(key, default_value)

    def current_phase(self, include_extended_support: bool = False) -> "SupportPhase":
        """
        Return the current support phase based on today's date.

        If no support phase has started yet, the function will return the first phase available.
        If all phases have ended, the function will return the last phase available.

        Args:
            include_extended_support (bool): Whether to include extended support phase.

        Returns:
            SupportPhase: The support phase instance that is currently ongoing.
        """

        self._validate_phases()

        phases = self._relevent_phases(include_extended_support)

        for i, p in enumerate(phases):
            if (
                (i == 0 and p.status is SupportStatus.UPCOMING)
                or p.status is SupportStatus.ONGOING
                or (i == (len(phases) - 1) and p.status is SupportStatus.RETIRED)
            ):
                return p

        return phases[-1]

    def status(self, include_extended_support: bool = False) -> "SupportStatus":
        """
        Return the current support status.

        - UPCOMING: the support has not started yet
        - ONGOING : the support is still ongoing
        - RETIRED : the support has ended

        Returns:
            SoftwareReleaseSupportStatus: The current status of the support as a SoftwareReleaseSupportStatus enum element
        """

        self._validate_phases()

        phases = self._relevent_phases(include_extended_support)

        today = datetime.now(UTC)
        start = phases[0].start
        end = phases[-1].end

        return (
            SupportStatus.UPCOMING
            if today < start
            else SupportStatus.RETIRED
            if today > end
            else SupportStatus.ONGOING
        )

    def duration(self, include_extended_support: bool = False) -> int:
        """
        Return for how long the support is ongoing.

        Returns:
            int: The number of support days
        """

        self._validate_phases()

        return sum(
            [p.duration for p in self._relevent_phases(include_extended_support)]
        )

    def is_ongoing(self, include_extended_support: bool = False) -> bool:
        """
        Check if the current support period is ongoing.

        Returns:
            bool: True if the support period is ongoing, False otherwise.
        """

        return self.status(include_extended_support) is SupportStatus.ONGOING

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
            dict[str, Any]: Dictionary containing software support key attributes
        """

        return {
            "status": str(self.status()),
            "hasLTS": self.has_extended_support,
            "isEoas": self.is_eoas,
            "isEol": self.is_eol,
            "isEoes": self.is_eoes,
            "duration": self.duration(),
            "durationExtended": self.duration(True),
            "currentPhase": str(self.current_phase(True).type),
            "phases": [ p.to_dict() for p in self._phases.values() ],
        }

    # ****************************************************************
    # Class methods

    @classmethod
    def from_dict(cls, support_dict: dict[str, "SupportPhaseProps"]) -> "Support":
        sd = cls()

        for phase_d in support_dict.values():
            sd.add(SupportPhase.from_dict(phase_d))

        return sd

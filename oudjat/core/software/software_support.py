"""A module that describes the notion of software support."""

from datetime import datetime
from enum import IntEnum
from typing import Any, override

from oudjat.utils.time_utils import TimeConverter


class SoftwareReleaseSupportStatus(IntEnum):
    """
    A simple enumeration to handle software release support status.

    Attributes:
        RETIRED: The release support is retired
        ONGOING: The release support is still ongoing
    """

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
        active_support: str | datetime,
        security_support: str | datetime | None = None,
        extended_security_support: str | datetime | None = None,
        long_term_support: bool = False,
    ) -> None:
        """
        Create a new instance SoftwareReleaseSupport.

        Args:
            active_support (str | datetime | None)           : The date when regular support ends. Can be a string with 'YYYY-MM-DD' format.
            security_support (str | datetime | None)         : The date when security support ends. Can be a string with 'YYYY-MM-DD' format.
            extended_security_support (str | datetime | None): The date when extended security support ends. Can be a string with 'YYYY-MM-DD' format.
            edition (list[str] | None)                       : A list of software editions supported by the release.
            long_term_support (bool | None)                  : Whether the release has long term support.
        """

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

        return SoftwareReleaseSupportStatus(int(self.is_ongoing))

    @property
    def is_ongoing(self) -> bool:
        """
        Check if the current support period is ongoing.

        Returns:
            bool: True if the support period is ongoing, False otherwise.
        """

        return TimeConverter.days_diff(self._security_support, reverse=True) > 0

    @property
    def support_details(self) -> str:
        """
        Return a detailed string about the supported status.

        Returns:
            str: A string indicating how many days are left in support or whether support has ended already.
        """

        support_days = TimeConverter.days_diff(self._security_support, reverse=True)
        state = f"{abs(support_days)} days"

        if support_days > 0:
            state = f"Ends in {state}"

        else:
            state = f"Ended {state} ago"

        return state

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

    def to_dict(self) -> dict[str, Any]:
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
            "activeSupport": TimeConverter.date_to_str(self._active_support),
            "securitySupport": TimeConverter.date_to_str(self._security_support),
            "extendedSecuritySupport": esu,
            "status": str(self.status),
            "lts": self._lts,
            "details": self.support_details,
        }

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


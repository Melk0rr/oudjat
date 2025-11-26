"""A module that describes the notion of software support."""

from datetime import datetime
from typing import Any, override

from oudjat.core.software.exceptions import SoftwareReleaseSupportInvalidEndDate
from oudjat.utils import Context
from oudjat.utils.time_utils import TimeConverter

from .software_edition import SoftwareEdition, SoftwareEditionDict


class SoftwareReleaseSupport:
    """A class to handle software release support concept."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        edition: dict[str, SoftwareEdition],
        active_support: str | datetime | None = None,
        end_of_life: str | datetime | None = None,
        long_term_support: bool = False,
    ) -> None:
        """
        Create a new instance SoftwareReleaseSupport.

        Args:
            active_support (str | datetime)    : The date when support starts or a string in 'YYYY-MM-DD' format.
            end_of_life (str | datetime | None): The date when support ends or a string in 'YYYY-MM-DD' format.
            edition (list[str] | None)         : A list of software editions supported by the release.
            long_term_support (bool | None)    : Whether the release has long term support.
        """

        self._edition: SoftwareEditionDict = SoftwareEditionDict(**edition)

        if active_support is None and end_of_life is None:
            raise SoftwareReleaseSupportInvalidEndDate(
                f"{Context()}::Please provide either an active support or end of life date."
            )

        # Handling none support values
        self._active_support: datetime
        self._end_of_life: datetime
        if active_support is not None and end_of_life is None:
            self._end_of_life = (
                TimeConverter.str_to_date(active_support)
                if not isinstance(active_support, datetime)
                else active_support
            )

            self._active_support = self._end_of_life

        if active_support is None and end_of_life is not None:
            self._active_support = (
                TimeConverter.str_to_date(end_of_life)
                if not isinstance(end_of_life, datetime)
                else end_of_life
            )

            self._end_of_life = self._active_support

        self._lts: bool = long_term_support

    # ****************************************************************
    # Methods

    @property
    def edition(self) -> SoftwareEditionDict:
        """
        Getter for the release edition.

        Returns:
            list[str]: The list of software editions supported by this release.
        """

        return self._edition

    @property
    def status(self) -> str:
        """
        Return a string representing the current support status.

        Returns:
            str: "Ongoing" if support is ongoing, otherwise "Retired".
        """

        return "Ongoing" if self.is_ongoing else "Retired"

    @property
    def is_ongoing(self) -> bool:
        """
        Check if the current support period is ongoing.

        Returns:
            bool: True if the support period is ongoing, False otherwise.
        """

        return TimeConverter.days_diff(self._end_of_life, reverse=True) > 0

    @property
    def support_details(self) -> str:
        """
        Return a detailed string about the supported status.

        Returns:
            str: A string indicating how many days are left in support or whether support has ended already.
        """

        support_days = TimeConverter.days_diff(self._end_of_life, reverse=True)
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

    def supports_edition(self, edition: str | list[str], lts: bool = False) -> bool:
        """
        Check if current support concerns the provided edition.

        Args:
            edition (str | list[str]): edition to check support for
            lts (bool)               : whether to look for lts support

        Returns:
            bool: whether the edition is supported or not
        """

        if not isinstance(edition, list):
            edition = [edition]

        return any([((e in self.edition) and (lts == self._lts)) for e in edition])

    @override
    def __str__(self) -> str:
        """
        Convert the current support instance into a string.

        Returns:
            str: a string representing the software support
        """

        return f"({';'.join(self._edition)}) : {self.status}{' - LTS' if self._lts else ''}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current support instance into a dict.

        Returns:
            dict : dictionary containing software support key attributes
        """

        return {
            "edition": self.edition,
            "activeSupport": TimeConverter.date_to_str(self._active_support),
            "endOfLife": TimeConverter.date_to_str(self._end_of_life),
            "status": self.status,
            "lts": self._lts,
            "details": self.support_details,
        }

    # ****************************************************************
    # Static methods


class SoftwareReleaseSupportList(list[SoftwareReleaseSupport]):
    """A class to manage lists of software releases."""

    # ****************************************************************
    # Methods

    def contains(
        self,
        edition: str | list[str],
        lts: bool = False,
    ) -> bool:
        """
        Check if list contains element matching provided attributes.

        This method checks whether any of the software releases in the list support the specified edition and/or are LTS (Long Term Support) based on the given criteria. It returns True if at least one release supports the given conditions, otherwise it returns False.

        Args:
            edition (str | list[str]): The edition or a list of editions to check for support.
            lts (bool)               : Whether to look for LTS releases.

        Returns:
            bool: True if there's a match, otherwise False.
        """

        return any([support.supports_edition(edition, lts) for support in self])

    def get(
        self,
        edition: str | list[str],
        lts: bool = False,
    ) -> list["SoftwareReleaseSupport"]:
        """
        Return releases matching arguments.

        This method filters and returns a list of `SoftwareReleaseSupport` objects that match the specified criteria for edition and LTS status. It uses the `supports_edition` method to filter the releases based on the provided parameters.

        Args:
            edition (str | list[str]): The edition or a list of editions to look for in the software releases.
            lts (bool)               : Whether to include only LTS releases in the result. Defaults to False.

        Returns:
            list[SoftwareReleaseSupport]: A list of `SoftwareReleaseSupport` objects that meet the specified conditions.
        """

        def support_edition(sup: "SoftwareReleaseSupport") -> bool:
            return sup.supports_edition(edition, lts)

        return list(filter(support_edition, self))

    @override
    def append(self, support: "SoftwareReleaseSupport") -> None:
        """
        Append a new support to the list.

        This method allows you to add a `SoftwareReleaseSupport` object to the end of the list. It ensures that only instances of `SoftwareReleaseSupport` can be appended by checking the type of the provided argument.

        Args:
            support (SoftwareReleaseSupport): The `SoftwareReleaseSupport` object to append to the list.

        Raises:
            TypeError: If the provided argument is not an instance of `SoftwareReleaseSupport`.
        """

        super().append(support)

    @override
    def __str__(self) -> str:
        """
        Convert the current support list into a string.

        This method returns a string representation of the list where each element is converted to its string form and joined with commas. It provides a readable format when printing or converting the list to a string.

        Returns:
            str: A string representing the list of software releases, formatted as "[release1, release2, ...]".
        """

        return f"[{', '.join(list(map(str, self)))}]"

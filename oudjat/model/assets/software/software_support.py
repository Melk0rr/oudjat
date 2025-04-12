from datetime import datetime
from typing import Dict, List, Union

from oudjat.utils import DATE_FLAGS, date_format_from_flag, days_diff

from .software_edition import SoftwareEditionDict


def soft_date_str(date: datetime) -> str:
    """
    Converts a software date into a string

    Args:
        date (datetime) : date to convert

    Returns:
        str : date string
    """

    if date is not None:
        return date.strftime(date_format_from_flag(DATE_FLAGS))


class SoftwareReleaseSupport:
    """A class to handle software release support concept"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        active_support: Union[str, datetime] = None,
        end_of_life: Union[str, datetime] = None,
        edition: List[str] = None,
        long_term_support: bool = False,
    ):
        """
        Constructor for the SoftwareReleaseSupport class.

        Args:
            active_support (Union[str, datetime], optional) : The date when support starts or a string in 'YYYY-MM-DD' format.
            end_of_life (Union[str, datetime], optional)    : The date when support ends or a string in 'YYYY-MM-DD' format.
            edition (List[str], optional)                   : A list of software editions supported by the release.
            long_term_support (bool, optional)              : Whether the release has long term support.
        """

        if not isinstance(edition, list):
            edition = [edition]

        self.edition = edition

        # Handling none support values
        if active_support is not None and end_of_life is None:
            end_of_life = active_support

        if active_support is None and end_of_life is not None:
            active_support = end_of_life

        # Datetime conversion
        try:
            if end_of_life is not None and not isinstance(end_of_life, datetime):
                end_of_life = datetime.strptime(end_of_life, date_format_from_flag(DATE_FLAGS))

            if active_support is not None and not isinstance(active_support, datetime):
                active_support = datetime.strptime(
                    active_support, date_format_from_flag(DATE_FLAGS)
                )

        except ValueError as e:
            raise ValueError(f"Please provide dates with %Y-%m-%d format\n{e}")

        self.active_support = active_support
        self.end_of_life = end_of_life

        self.lts = long_term_support

    # ****************************************************************
    # Methods

    def get_edition(self) -> SoftwareEditionDict:
        """
        Getter for the release edition.

        Returns:
            List[str]: The list of software editions supported by this release.
        """

        return self.edition

    def is_ongoing(self) -> bool:
        """
        Checks if the current support period is ongoing.

        Returns:
            bool: True if the support period is ongoing, False otherwise.
        """

        if self.end_of_life is None:
            return True

        return days_diff(self.end_of_life, reverse=True) > 0

    def status(self) -> str:
        """
        Returns a string representing the current support status.

        Returns:
            str: "Ongoing" if support is ongoing, otherwise "Retired".
        """

        return "Ongoing" if self.is_ongoing() else "Retired"

    def support_details(self) -> str:
        """
        Returns a detailed string about the supported status.

        Returns:
            str: A string indicating how many days are left in support or whether support has ended already.
        """

        support_days = days_diff(self.end_of_life, reverse=True)
        state = f"{abs(support_days)} days"

        if support_days > 0:
            state = f"Ends in {state}"

        else:
            state = f"Ended {state} ago"

        return state

    def has_long_term_support(self) -> bool:
        """
        Checks if the release has long term support.

        Returns:
            bool: True if the release has long term support, False otherwise.
        """

        return self.lts

    def supports_edition(self, edition: Union[str, List[str]], lts: bool = False) -> bool:
        """
        Checks if current support concerns the provided edition

        Args:
            edition (Union[str, List[str]]): edition to check support for
            lts (bool) : whether to look for lts support

        Returns:
            bool: whether the edition is supported or not
        """

        if edition is None:
            return False

        if not isinstance(edition, list):
            edition = [edition]

        if self.edition is None:
            return True

        return any([((e in self.edition) and (lts == self.lts)) for e in edition])

    def __str__(self) -> str:
        """
        Converts the current support instance into a string

        Returns:
            str: a string representing the software support
        """

        return f"({';'.join(self.edition)}) : {self.status()}{' - LTS' if self.lts else ''}"

    def to_dict(self) -> Dict:
        """
        Converts the current support instance into a dict

        Returns:
            Dict : dictionary containing software support key attributes
        """
        return {
            "edition": self.edition,
            "active_support": soft_date_str(self.active_support),
            "end_of_life": soft_date_str(self.end_of_life),
            "status": self.status(),
            "lts": self.lts,
            "details": self.support_details(),
        }


class SoftwareReleaseSupportList(list):
    """A class to manage lists of software releases"""

    # ****************************************************************
    # Methods

    def contains(
        self,
        edition: Union[str, List[str]] = None,
        lts: bool = False,
    ) -> bool:
        """
        Check if list contains element matching provided attributes.

        This method checks whether any of the software releases in the list support the specified edition and/or are LTS (Long Term Support) based on the given criteria. It returns True if at least one release supports the given conditions, otherwise it returns False.

        Args:
            edition (Union[str, List[str]]) : The edition or a list of editions to check for support.
            lts (bool)                      : Whether to look for LTS releases.

        Returns:
            bool: True if there's a match, otherwise False.
        """
        return any([support.supports_edition(edition, lts) for support in self])

    def get(
        self,
        edition: Union[str, List[str]] = None,
        lts: bool = False,
    ) -> List[SoftwareReleaseSupport]:
        """
        Returns releases matching arguments.

        This method filters and returns a list of `SoftwareReleaseSupport` objects that match the specified criteria for edition and LTS status. It uses the `supports_edition` method to filter the releases based on the provided parameters.

        Args:
            edition (Union[str, List[str]]) : The edition or a list of editions to look for in the software releases.
            lts (bool)                      : Whether to include only LTS releases in the result. Defaults to False.

        Returns:
            List[SoftwareReleaseSupport]: A list of `SoftwareReleaseSupport` objects that meet the specified conditions.
        """
        return [support for support in self if support.supports_edition(edition, lts)]

    def append(self, support: SoftwareReleaseSupport) -> None:
        """
        Appends a new support to the list.

        This method allows you to add a `SoftwareReleaseSupport` object to the end of the list. It ensures that only instances of `SoftwareReleaseSupport` can be appended by checking the type of the provided argument.

        Args:
            support (SoftwareReleaseSupport): The `SoftwareReleaseSupport` object to append to the list.

        Raises:
            TypeError: If the provided argument is not an instance of `SoftwareReleaseSupport`.
        """
        if isinstance(support, SoftwareReleaseSupport):
            super().append(support)

    def __str__(self) -> str:
        """
        Converts the current support list into a string.

        This method returns a string representation of the list where each element is converted to its string form and joined with commas. It provides a readable format when printing or converting the list to a string.

        Returns:
            str: A string representing the list of software releases, formatted as "[release1, release2, ...]".
        """
        return f"[{', '.join(list(map(str, self)))}]"

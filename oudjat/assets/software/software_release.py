"""A module that defines the notion of software release."""

from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Union

from oudjat.utils.time_utils import TimeConverter

from .software_support import SoftwareReleaseSupport, SoftwareReleaseSupportList

if TYPE_CHECKING:
    from .software import Software


class SoftwareRelease:
    """A class to describe software releases."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        software: "Software",
        version: Union[int, str],
        release_date: Union[str, datetime],
        release_label: str,
    ) -> None:
        """
        Create a new instance of SoftwareRelease.

        Args:
            software (Software)                 : The software instance to which this release belongs.
            version (Union[int, str])           : The version of the software, can be either an integer or a string representation of a number.
            release_date (Union[str, datetime]) : The date when the software was released. Can be provided as a string formatted according to `%Y-%m-%d`
                                                or as a datetime object. If provided as a string, it will be parsed using the format specified by DateStrFlag.YMD.
            release_label (str)                 : A label describing the nature of this release, such as "stable" or "beta".

        Raises:
            ValueError: If `release_date` is provided as a string and does not match the expected date format.
        """

        self.software = software
        self.version = version
        self.label = release_label

        try:
            if not isinstance(release_date, datetime):
                release_date = TimeConverter.str_to_date(release_date)

        except ValueError as e:
            raise ValueError(
                f"{__class__.__name__}::Please provide dates with %Y-%m-%d format\n{e}"
            )

        self.release_date = release_date
        self.support = SoftwareReleaseSupportList()

        # NOTE: maybe convert vulnerabilities into a dictionary (CVE instances ?) if needed
        self.vulnerabilities = set()

    # ****************************************************************
    # Methods
    def get_software(self) -> "Software":
        """
        Return the release software.

        Returns:
            Software: The software associated with the release.
        """

        return self.software

    def get_label(self) -> str:
        """
        Return the release label.

        Returns:
            str: The label of the software release.
        """

        return self.label

    def get_version(self) -> Union[int, str]:
        """
        Return the release version.

        Returns:
            Union[int, str]: The version number or identifier of the software release.
        """

        return self.version

    def is_supported(self, edition: Union[str, List[str]] = None) -> bool:
        """
        Check if the current release has an ongoing support.

        Args:
            edition (Union[str, List[str]], optional): The specific edition to check for support. Defaults to None.

        Returns:
            bool: True if the release is supported, otherwise False.
        """

        return any(
            [
                s.is_ongoing() and (edition is None or s.supports_edition(edition))
                for s in self.support
            ]
        )

    def get_support(self) -> "SoftwareReleaseSupportList":
        """
        Return support list.

        Returns:
            SoftwareReleaseSupportList: The list of support details for the software release.
        """

        return self.support

    def get_support_for_edition(
        self, edition: Union[str, List[str]], lts: bool = False
    ) -> "SoftwareReleaseSupportList":
        """
        Return support for given edition.

        Args:
            edition (Union[str, List[str]]) : The specific edition to retrieve support for.
            lts (bool, optional)            : Whether to filter for LTS (Long Term Support) editions. Defaults to False.

        Returns:
            SoftwareReleaseSupportList : The list of support details filtered by the specified edition or LTS status.
        """

        return self.support.get(edition, lts=lts) if edition is not None else None

    def get_ongoing_support(self) -> List["SoftwareReleaseSupport"]:
        """
        Return ongoing support instances.

        Returns:
            List[SoftwareReleaseSupport]: A list of support details that are currently ongoing.
        """

        return [s for s in self.support if s.is_ongoing()]

    def get_retired_support(self) -> List["SoftwareReleaseSupport"]:
        """
        Return retired support instances.

        Returns:
            List[SoftwareReleaseSupport]: A list of support details that are no longer ongoing.
        """

        return [s for s in self.support if not s.is_ongoing()]

    def get_name(self) -> None:
        """
        Return the name of the release.

        Raises:
            NotImplementedError: This method must be implemented by the overloading class.
        """

        raise NotImplementedError(
            f"{__class__.__name__}.get_name::Method must be implemented by the overloading class"
        )

    def get_full_name(self) -> None:
        """
        Return the release full name.

        Returns:
            str: The full name of the software release, combining the software name and its label.
        """

        return f"{self.get_software().get_name()} {self.label}"

    def add_support(self, support: SoftwareReleaseSupport) -> None:
        """
        Add a support instance to the current release.

        Args:
            support (SoftwareReleaseSupport): The support instance to be added.

        Returns:
            None
        """

        if not isinstance(support, SoftwareReleaseSupport):
            return

        if not self.support.contains(
            edition=support.get_edition(), lts=support.has_long_term_support()
        ):
            self.support.append(support)

    def has_vulnerability(self, vuln: Union[str, List[str]] = None) -> List[str]:
        """
        Check if the release is concerned by any or specific vulnerability.

        Args:
            vuln (Union[str, List[str], optional): The vulnerability to check. Can be a single string or a list of strings. Defaults to None.

        Returns:
            List[str]: A list of vulnerabilities that the release is concerned by. If `vuln` is provided, returns only those in `vuln`.
        """

        if vuln is None:
            return list(self.vulnerabilities)

        if not isinstance(vuln, list):
            vuln = [vuln]

        return [v in self.vulnerabilities for v in vuln]

    def add_vuln(self, vuln: str) -> None:
        """
        Add a vulnerability to the current release.

        Args:
            vuln (str): The vulnerability string to be added.
        """

        self.vulnerabilities.add(vuln)

    def __str__(self, show_version: bool = False) -> str:
        """
        Convert current release to a string.

        Args:
            show_version (bool, optional): Whether to include the version in the string representation. Defaults to False.

        Returns:
            str: A string representation of the software release, optionally including the version.
        """

        name = self.get_full_name()

        if show_version:
            name = f"{name.strip()}({self.version})"

        return name.strip()

    def os_info_dict(self) -> Dict:
        """
        Return a dictionary with OS infos.

        Returns:
            Dict: A dictionary containing information about the operating system, including software name, release name, version, full name, and support status.
        """

        return {
            "software": self.get_software().get_name(),
            "name": self.get_name(),
            "version": self.version,
            "full_name": self.get_full_name(),
            "is_supported": self.is_supported(),
        }

    def to_dict(self) -> Dict:
        """
        Convert current release into a dict.

        Returns:
            Dict: A dictionary representation of the software release, including its label, release date, and OS information.
        """

        return {
            "label": self.label,
            "release_date": SoftwareReleaseSupport.soft_date_str(self.release_date),
            **self.os_info_dict(),
            "support": ", ".join([str(s) for s in self.support]),
        }


class SoftwareReleaseDict(dict):
    """Software release dictionary."""

    # ****************************************************************
    # Methods

    def find_rel_matching_label(self, val: str) -> "SoftwareReleaseDict":
        """
        Try to find release with a label matching the given string.

        This method searches through the dictionary and returns a new dictionary containing only those key-value pairs where the keys match the provided string `val`.
        The resulting dictionary is of type SoftwareReleaseDict, preserving the structure of the original dictionary for potential further processing.

        Args:
            val (str): The string to search for in the dictionary keys.

        Returns:
            SoftwareReleaseDict: A new dictionary containing only the key-value pairs where the keys match `val`.
        """

        return {k: v for k, v in self.items() if k in val}

    def find_rel(self, rel_ver: str, rel_label: str = None) -> "SoftwareReleaseDict":
        """
        Find the given release.

        This method searches through the dictionary to locate a specific software release by version and optionally by label.
        It returns either the entire release information if only the version is specified, or it narrows down the search to a specific label within that version if both are provided.

        Args:
            rel_ver (str)            : The version of the software release to find.
            rel_label (str, optional): The label associated with the release. Defaults to None.

        Returns:
            SoftwareReleaseDict: A dictionary containing either the entire release information or a specific label's information based on the provided criteria.
        """

        if rel_ver not in self.keys():
            return None

        search: SoftwareReleaseDict = self.get(rel_ver)

        if rel_label is not None and rel_label not in search.keys():
            return search

        search = search.get(rel_label)
        return {search.get_label(): search}

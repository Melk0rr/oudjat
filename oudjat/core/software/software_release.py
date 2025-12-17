"""A module that describe the concept of software release."""

from collections.abc import Iterator
from datetime import datetime
from typing import Any, Generic, TypeVar, override

from oudjat.core.generic_identifiable import GenericIdentifiable
from oudjat.core.software.software_edition import SoftwareEdition
from oudjat.utils import Context
from oudjat.utils.time_utils import TimeConverter

from .software_release_version import SoftwareReleaseVersion
from .software_support import SoftwareReleaseSupport

ReleaseType = TypeVar("ReleaseType", bound="SoftwareRelease")


class SoftwareRelease(GenericIdentifiable):
    """A class to describe software releases."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        release_id: str,
        name: str,
        software_name: str,
        version: int | str,
        release_date: str | datetime,
        release_label: str | None = None,
    ) -> None:
        """
        Create a new instance of SoftwareRelease.

        Args:
            release_id (str)             : The ID of the release
            name (str)                   : The name of the release
            software_name (str)          : The software name which this release belongs to.
            version (int | str)          : The version of the software, can be either an integer or a string representation of a number.
            release_date (str | datetime): The date when the software was released. Can be provided as a string formatted like: `%Y-%m-%d`
                                                or as a datetime object. If provided as a string, it will be parsed using the format specified by DateStrFlag.YMD.
            release_label (str)          : A label describing the nature of this release, such as "stable" or "beta".

        Raises:
            ValueError: If `release_date` is provided as a string and does not match the expected date format.
        """

        self._software: str = software_name

        # Version attributes
        self._version: "SoftwareReleaseVersion" = SoftwareReleaseVersion(version)
        self._latest_version: "SoftwareReleaseVersion" = self._version

        super().__init__(gid=release_id, name=name, label=release_label)

        try:
            if not isinstance(release_date, datetime):
                release_date = TimeConverter.str_to_date(release_date)

        except ValueError as e:
            raise ValueError(f"{Context()}::Please provide dates with %Y-%m-%d format\n{e}")

        self._release_date: datetime = release_date
        self._support_channels: dict[str, "SoftwareReleaseSupport"] = {}

        # NOTE: maybe convert vulnerabilities into a dictionary (CVE instances ?) if needed
        self._vulnerabilities: set[str] = set()

    # ****************************************************************
    # Methods

    @property
    def software(self) -> str:
        """
        Return the release software.

        Returns:
            Software: The software associated with the release.
        """

        return self._software

    @property
    def version(self) -> "SoftwareReleaseVersion":
        """
        Return the release version.

        Returns:
            int | str: The version number or identifier of the software release.
        """

        return self._version

    @property
    def latest_version(self) -> "SoftwareReleaseVersion":
        """
        Return the latest version of the current release.

        Returns:
            int | str: The version number or identifier of the software release.
        """

        return self._latest_version

    @latest_version.setter
    def latest_version(self, new_latest_version: "SoftwareReleaseVersion") -> None:
        """
        Return the release version.

        Returns:
            int | str: The version number or identifier of the software release.
        """

        self._latest_version = new_latest_version

    @property
    def support_channels(self) -> dict[str, "SoftwareReleaseSupport"]:
        """
        Return support list.

        Returns:
            SoftwareReleaseSupportList: The list of support details for the software release.
        """

        return self._support_channels

    @property
    def release_date(self) -> datetime:
        """
        Return the release date of this release.

        Returns:
            datetime: a datetime object that corresponds to this release
        """

        return self._release_date

    @property
    def fullname(self) -> str:
        """
        Return the release full name.

        Returns:name
            str: The full name of the software release, combining the software name and its label.
        """

        return f"{self._software} {self._label}"

    @property
    def vulnerabilities(self) -> set[str]:
        """
        Return the vulnerabilies this software is concerned with.

        Returns:
            set[str]: a set of unique vulnerabilities
        """

        return self._vulnerabilities

    @property
    def ongoing_support(self) -> dict[str, "SoftwareReleaseSupport"]:
        """
        Return ongoing support instances.

        Returns:
            list[SoftwareReleaseSupport]: A list of support details that are currently ongoing.
        """

        return {ch_k: s for ch_k, s in self._support_channels.items() if s.is_ongoing}

    @property
    def retired_support(self) -> dict[str, "SoftwareReleaseSupport"]:
        """
        Return retired support instances.

        Returns:
            list[SoftwareReleaseSupport]: A list of support details that are no longer ongoing.
        """

        return {ch_k: s for ch_k, s in self._support_channels.items() if not s.is_ongoing}

    def is_supported(self, edition: "SoftwareEdition | None" = None) -> bool:
        """
        Check if the current release has an ongoing support for the provided edition.

        If no edition is provided, it will simply check if there is any ongoing support.

        Args:
            edition (str | list[str] | None): The specific edition to check for support. Defaults to None.

        Returns:
            bool: True if the release is supported, otherwise False.
        """

        return any(
            [
                s.is_ongoing and (edition is None or channel == edition.channel)
                for channel, s in self._support_channels.items()
            ]
        )

    def add_support(self, channel: str, support: "SoftwareReleaseSupport") -> None:
        """
        Add a support instance to the current release.

        Args:
            channel (str)                   : The support channel
            support (SoftwareReleaseSupport): The support instance to be added.
        """

        if channel not in self._support_channels.keys():
            self._support_channels[channel] = support

    def has_vulnerability(self, vuln: str | list[str] | None = None) -> list[str]:
        """
        Check if the release is concerned by any or specific vulnerability.

        Args:
            vuln (str | list[str] | None): The vulnerability to check. Can be a single string or a list of strings. Defaults to None.

        Returns:
            list[str]: A list of vulnerabilities that the release is concerned with. If `vuln` is provided, returns only those in `vuln`.
        """

        if vuln is None:
            return list(self.vulnerabilities)

        if not isinstance(vuln, list):
            vuln = [vuln]

        return [v for v in vuln if v in self.vulnerabilities]

    def add_vuln(self, vuln: str) -> None:
        """
        Add a vulnerability to the current release.

        Args:
            vuln (str): The vulnerability string to be added.
        """

        self._vulnerabilities.add(vuln)

    @override
    def __str__(self, show_version: bool = False) -> str:
        """
        Convert current release to a string.

        Args:
            show_version (bool | None): Whether to include the version in the string representation. Defaults to False.

        Returns:
            str: A string representation of the software release, optionally including the version.
        """

        name = self.fullname

        if show_version:
            name = f"{name.strip()}({self._version})"

        return name.strip()

    def _software_dict(self) -> dict[str, Any]:
        """
        Return a dictionary with OS infos.

        Returns:
            dict: A dictionary containing innamen about the operating system, including software name, release name, version, full name, and support status.
        """

        return {
            "software": self.software,
            "name": self.name,
            "version": {
                "initial": str(self._version),
                "latest": str(self._latest_version)
            },
            "fullname": self.fullname,
            "isSupported": self.is_supported(),
        }

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert current release into a dict.

        Returns:
            dict: A dictionary representation of the software release, including its label, release date, and OS information.
        """

        base = super().to_dict()

        return {
            **base,
            "releaseDate": TimeConverter.date_to_str(self._release_date),
            **self._software_dict(),
            "supportChannels": {ch_k: s.to_dict() for ch_k, s in self._support_channels.items()},
        }


class SoftwareRelVersionDict(Generic[ReleaseType]):
    """Software release version dictionary."""

    # ****************************************************************
    # Constructor & Attributes

    def __init__(self) -> None:
        """
        Create a new instance of SoftwareReleaseDict.
        """

        self._versions: dict[str, "ReleaseType"] = {}

    # ****************************************************************
    # Methods

    def __getitem__(self, key: str) -> "ReleaseType":
        """
        Return a Software release element based on its key.

        Args:
            key (str): The version of the release to retrieve

        Returns:
            ReleaseType: covariant element of SoftwareRelease
        """

        return self._versions[key]

    def __setitem__(self, version: str, value: "ReleaseType") -> None:
        """
        Set the Software release in the dictionary for the provided key.

        Args:
            version (str)      : The version of the release to retrieve
            value (ReleaseType): Value of the new element
        """

        self._versions[version] = value

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator to go through the SoftwareRelEditionDict instances.

        Returns:
            Iterator[str]: iterator object
        """

        return iter(self._versions)

    def get(
        self, key: str, default_value: Any = None
    ) -> "ReleaseType | None":
        """
        Return a SoftwareRelEditionDict element based on its key.

        If the element cannot be found, return the default value.

        Args:
            key (str)          : Key of the element to return
            default_value (Any): Default value in case the element cannot be found

        Returns:
            ReleaseType | None: Element associated with provided key or default value

        """

        return self._versions.get(key, default_value)

    def keys(self):
        """
        Return the keys of the data dict.

        Returns:
            dict_keys[str, ReleaseType]: The keys of the current dictionary
        """

        return self._versions.keys()

    def values(self):
        """
        Return the values of the data dict.

        Returns:
            dict_values[str, ReleaseType]: The values of the current dictionary
        """

        return self._versions.values()

    def items(self):
        """
        Return the items of the data dict.

        Returns:
            dict_items[str, ReleaseType]: The items of the current dictionary
        """

        return self._versions.items()

    def filter_by_str(self, search_str: str) -> "SoftwareRelVersionDict[ReleaseType]":
        """
        Search for elements with a key matching the provided search string.

        Args:
            search_str (str): search string to compare to the keys in the current dictionary

        Returns:
            SoftwareRelVersionDict[ReleaseType]: A filtered SoftwareRelVersionDict
        """

        return SoftwareRelVersionDict[ReleaseType](
            **{
                version: version_dict
                for version, version_dict in self.items()
                if search_str in version
            }
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the SoftwareRelVersionDict into a regular dictionary.

        Returns:
            dict[str, SoftwareRelEditionDict]: A regular dictionary representation of the current instance
        """

        return {version: version_dict.to_dict() for version, version_dict in self._versions.items()}

"""A module that describe the concept of software release."""

import logging
import re
from collections.abc import Iterator
from datetime import datetime
from typing import Any, Callable, Generic, TypeVar, override

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

        _ = self._support_channels.setdefault(channel, support)

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

    def __gt__(self, other: "SoftwareRelease") -> bool:
        """
        Check if current release is greater (version wise) than the other.

        Args:
            other (SoftwareRelease): The other release

        Returns:
            bool: True if the current release version is greater than the other release version
        """

        return self.version > other.version

    def __ge__(self, other: "SoftwareRelease") -> bool:
        """
        Check if current release is greater or equal (version wise) than the other.

        Args:
            other (SoftwareRelease): The other release

        Returns:
            bool: True if the current release version is greater or equal than the other release version
        """

        return self.version >= other.version

    def __lt__(self, other: "SoftwareRelease") -> bool:
        """
        Check if current release is lower (version wise) than the other.

        Args:
            other (SoftwareRelease): The other release

        Returns:
            bool: True if the current release version is lower than the other release version
        """

        return self.version < other.version

    def __le__(self, other: "SoftwareRelease") -> bool:
        """
        Check if current release is lower or equal (version wise) than the other.

        Args:
            other (SoftwareRelease): The other release

        Returns:
            bool: True if the current release version is lower or equal than the other release version
        """

        return self.version <= other.version

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
            "version": {"initial": str(self._version), "latest": str(self._latest_version)},
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


class SoftwareReleaseList(list, Generic[ReleaseType]):
    """
    A class to provide useful methods to narrow down / filter a list of SoftwareRelease.
    """

    # ****************************************************************
    # Methods

    def is_empty(self) -> bool:
        """
        Check if the list is empty.

        Returns:
            bool: True if the list is empty. False otherwise
        """

        return len(self) == 0

    def unique(
        self,
        *filters: Callable[
            ["SoftwareReleaseList[ReleaseType]"], "SoftwareReleaseList[ReleaseType]"
        ],
    ) -> "ReleaseType | None":
        """
        Filter the list of SoftwareRelease with the provided filters until there is only a unique release left if possible.

        The method chains the provided filters one after the other to narrow down the result.

        Args:
            filters (Callable[[SoftwareReleaseList], SoftwareReleaseList]): The list of filters to resolve the list of releases

        Returns:
            ReleaseType | None: The resolved release if any
        """

        candidates = self
        for f in filters:
            candidates = f(candidates)
            if candidates.is_empty():
                return None

            if len(candidates) == 1:
                return candidates[0]

        return None

    def filter_by_label(
        self,
        label_str: str,
        filter_cb: Callable[[str, str], bool] | None = None,
        fallback: bool = False,
    ) -> "SoftwareReleaseList[ReleaseType]":
        """
        Filter the list of SoftwareRelease by comparing the releases label with the provided string.

        By default, the method searches for each release label in the provided string.
        You can also provide a custom callback.

        Args:
            label_str (str)                                      : The string to compare to the release labels
            filter_cb (Callable[[ReleaseType, str], bool] | None): Custom label comparison callback
            fallback (bool)                                      : If True, falls back to the default list. Else, returns the filtered list

        Returns:
            SoftwareReleaseList: Filtered SoftwareRelease list
        """

        cb: Callable[["ReleaseType"], bool]
        if filter_cb is not None:

            def arg_filter_cb(rel: "ReleaseType") -> bool:
                return filter_cb(f"{rel.label}", label_str)

            cb = arg_filter_cb

        else:

            def label_filter_cb(rel: "ReleaseType") -> bool:
                return re.search(f"{rel.label}", label_str) is not None

            cb = label_filter_cb

        filtered_rels: "SoftwareReleaseList[ReleaseType]" = SoftwareReleaseList(filter(cb, self))
        if fallback and len(filtered_rels) == 0:
            filtered_rels = self

        return filtered_rels

    def filter_by_status(
        self, supported: bool = True, fallback: bool = False
    ) -> "SoftwareReleaseList[ReleaseType]":
        """
        Filter the list of SoftwareRelease by comparing the releases supported status with the provided value.

        Args:
            supported (bool): Whether to filter releases if they are supported or out of support
            fallback (bool) : If True, falls back to the default list. Else, returns the filtered list

        Returns:
            SoftwareReleaseList: Filtered SoftwareRelease list
        """

        def status_filter_cb(rel: "ReleaseType") -> bool:
            return rel.is_supported() == supported

        filtered_rels: "SoftwareReleaseList[ReleaseType]" = SoftwareReleaseList(
            filter(status_filter_cb, self)
        )

        if fallback and len(filtered_rels) == 0:
            filtered_rels = self

        return filtered_rels

    def filter_by_id(
        self, id_str: str, fallback: bool = False
    ) -> "SoftwareReleaseList[ReleaseType]":
        """
        Filter the list of SoftwareRelease by comparing the releases id with the provided string.

        Args:
            id_str (str)   : The string to compare to the release id
            fallback (bool): If True, falls back to the default list. Else, returns the filtered list

        Returns:
            SoftwareReleaseList: Filtered SoftwareRelease list
        """

        def id_filter_cb(rel: "ReleaseType") -> bool:
            return rel.id == id_str

        filtered_rels: "SoftwareReleaseList[ReleaseType]" = SoftwareReleaseList(
            filter(id_filter_cb, self)
        )
        if fallback and len(filtered_rels) == 0:
            filtered_rels = self

        return filtered_rels

    def filter_max_version(self) -> "SoftwareReleaseList[ReleaseType]":
        """
        Filter the list of SoftwareRelease by keeping only the ones with the highest version.

        Returns:
            SoftwareReleaseList: Filtered SoftwareRelease list
        """

        max_version = max([rel.version for rel in self])

        def filter_version_cb(rel: "ReleaseType") -> bool:
            return rel.version == max_version

        return SoftwareReleaseList(filter(filter_version_cb, self))

    def to_dict(self) -> list[dict[str, Any]]:
        """
        Convert the releases of the list into dictionaries.

        Returns:
            list[dict[str, Any]]: A list of releases dictionaries
        """

        return [rel.to_dict() for rel in self]


class SoftwareRelVersionDict(Generic[ReleaseType]):
    """Software release version dictionary."""

    # ****************************************************************
    # Constructor & Attributes

    def __init__(self) -> None:
        """
        Create a new instance of SoftwareReleaseDict.
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)
        self._releases: dict[str, "SoftwareReleaseList[ReleaseType]"] = {}

    # ****************************************************************
    # Methods

    def __getitem__(self, key: str) -> "SoftwareReleaseList[ReleaseType]":
        """
        Return a Software release element based on its key.

        Args:
            key (str): The version of the release to retrieve

        Returns:
            ReleaseType: covariant element of SoftwareRelease
        """

        return self._releases[key]

    def __setitem__(self, key: str, value: "ReleaseType") -> None:
        """
        Set the Software release in the dictionary for the provided key.

        Args:
            key (str)          : The version of the release to retrieve
            value (ReleaseType): Value of the new element
        """

        self._releases[key] = SoftwareReleaseList([value])

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator to go through the SoftwareRelEditionDict instances.

        Returns:
            Iterator[str]: iterator object
        """

        return iter(self._releases)

    def add(self, key: str, release: "ReleaseType", force: bool = False) -> None:
        """
        Add a new release for the provided version key.

        The method checks if a similar release (based on ID) already exists for the provided version key.
        If force argument is set to True, the new release will be added regardless.

        Args:
            key (str)            : The key of the new release
            release (ReleaseType): The new release to add
            force (bool)         : Whether to force the addition of the new release
        """

        _ = self._releases.setdefault(key, SoftwareReleaseList())

        if force or not any(rel.id == release.id for rel in self._releases[key]):
            self._releases[key].append(release)

        else:
            self.logger.warning(
                f"{Context()}::A release with same id ({release.id}) already exists for version {key}"
            )

    def get(self, key: str, default_value: Any = None) -> "SoftwareReleaseList[ReleaseType] | None":
        """
        Return a SoftwareRelEditionDict element based on its key.

        If the element cannot be found, return the default value.

        Args:
            key (str)          : Key of the element to return
            default_value (Any): Default value in case the element cannot be found

        Returns:
            list[ReleaseType] | None: Element associated with provided key or default value

        """

        return self._releases.get(key, default_value)

    def keys(self):
        """
        Return the keys of the data dict.

        Returns:
            dict_keys[str, ReleaseType]: The keys of the current dictionary
        """

        return self._releases.keys()

    def values(self):
        """
        Return the values of the data dict.

        Returns:
            dict_values[str, ReleaseType]: The values of the current dictionary
        """

        return self._releases.values()

    def items(self):
        """
        Return the items of the data dict.

        Returns:
            dict_items[str, ReleaseType]: The items of the current dictionary
        """

        return self._releases.items()

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

        return {
            version: [ver.to_dict() for ver in versions]
            for version, versions in self._releases.items()
        }

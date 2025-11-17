"""A module that describe the concept of software release."""

from collections.abc import Iterator
from datetime import datetime
from typing import Any, Generic, TypeVar, override

from oudjat.utils.time_utils import TimeConverter

from .software_release_version import SoftwareReleaseVersion
from .software_support import SoftwareReleaseSupport, SoftwareReleaseSupportList

ReleaseType = TypeVar("ReleaseType", bound="SoftwareRelease")

class SoftwareRelease:
    """A class to describe software releases."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        software_name: str,
        version: int | str,
        release_date: str | datetime,
        release_label: str,
    ) -> None:
        """
        Create a new instance of SoftwareRelease.

        Args:
            software_name (str)          : The software name which this release belongs to.
            version (int | str)          : The version of the software, can be either an integer or a string representation of a number.
            release_date (str | datetime): The date when the software was released. Can be provided as a string formatted like: `%Y-%m-%d`
                                                or as a datetime object. If provided as a string, it will be parsed using the format specified by DateStrFlag.YMD.
            release_label (str)          : A label describing the nature of this release, such as "stable" or "beta".

        Raises:
            ValueError: If `release_date` is provided as a string and does not match the expected date format.
        """

        # TODO: fully implement SoftwareReleaseVersion
        self._software: str = software_name
        self._version: "SoftwareReleaseVersion" = SoftwareReleaseVersion(version)
        self._label: str = release_label

        try:
            if not isinstance(release_date, datetime):
                release_date = TimeConverter.str_to_date(release_date)

        except ValueError as e:
            raise ValueError(
                f"{__class__.__name__}::Please provide dates with %Y-%m-%d format\n{e}"
            )

        self._release_date: datetime = release_date
        self._support: "SoftwareReleaseSupportList" = SoftwareReleaseSupportList()

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
    def label(self) -> str:
        """
        Return the release label.

        Returns:
            str: The label of the software release.
        """

        return self._label

    @property
    def version(self) -> SoftwareReleaseVersion:
        """
        Return the release version.

        Returns:
            int | str: The version number or identifier of the software release.
        """

        return self._version

    @property
    def support(self) -> "SoftwareReleaseSupportList":
        """
        Return support list.

        Returns:
            SoftwareReleaseSupportList: The list of support details for the software release.
        """

        return self._support

    @property
    def name(self) -> str:
        """
        Return the name of the release.

        Raises:
            NotImplementedError: This method must be implemented by the overloading class.
        """

        raise NotImplementedError(
            f"{__class__.__name__}.get_name::Method must be implemented by the overloading class"
        )

    @property
    def release_date(self) -> datetime:
        """
        Return the release date of this release.

        Returns:
            datetime: a datetime object that corresponds to this release
        """

        return self._release_date

    @property
    def key(self) -> str:
        """
        Return a unique release key based on version and label.

        Returns:
            str: Release key
        """

        return f"{self._version} - {self._label}"

    @property
    def full_name(self) -> str:
        """
        Return the release full name.

        Returns:name
            str: The full name of the software release, combining the software name and its label.
        """

        return f"{self.software} {self.label}"

    @property
    def vulnerabilities(self) -> set[str]:
        """
        Return the vulnerabilies this software is concerned with.

        Returns:
            set[str]: a set of unique vulnerabilities
        """

        return self._vulnerabilities


    @property
    def ongoing_support(self) -> list["SoftwareReleaseSupport"]:
        """
        Return ongoing support instances.

        Returns:
            list[SoftwareReleaseSupport]: A list of support details that are currently ongoing.
        """

        return [s for s in self._support if s.is_ongoing]

    @property
    def retired_support(self) -> list["SoftwareReleaseSupport"]:
        """
        Return retired support instances.

        Returns:
            list[SoftwareReleaseSupport]: A list of support details that are no longer ongoing.
        """

        return [s for s in self._support if not s.is_ongoing]

    def is_supported(self, edition: str | list[str] | None = None) -> bool:
        """
        Check if the current release has an ongoing support.

        Args:
            edition (str | list[str] | None): The specific edition to check for support. Defaults to None.

        Returns:
            bool: True if the release is supported, otherwise False.
        """

        return any(
            [
                s.is_ongoing and (edition is None or s.supports_edition(edition))
                for s in self._support
            ]
        )

    def support_for_edition(
        self, edition: str | list[str], lts: bool = False
    ) -> "SoftwareReleaseSupportList":
        """
        Return support for given edition.

        Args:
            edition (str | list[str]): The specific edition to retrieve support for.
            lts (bool | None)     : Whether to filter for LTS (Long Term Support) editions. Defaults to False.

        Returns:
            SoftwareReleaseSupportList : The list of support details filtered by the specified edition or LTS status.
        """

        return SoftwareReleaseSupportList(*self._support.get(edition, lts=lts))

    def add_support(self, support: "SoftwareReleaseSupport") -> None:
        """
        Add a support instance to the current release.

        Args:
            support (SoftwareReleaseSupport): The support instance to be added.

        Returns:
            None
        """

        if not self._support.contains(
            edition=list(support.edition.keys()), lts=support.has_long_term_support
        ):
            self._support.append(support)

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

        self.vulnerabilities.add(vuln)

    @override
    def __str__(self, show_version: bool = False) -> str:
        """
        Convert current release to a string.

        Args:
            show_version (bool | None): Whether to include the version in the string representation. Defaults to False.

        Returns:
            str: A string representation of the software release, optionally including the version.
        """

        name = self.full_name

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
            "version": self.version.to_dict(),
            "full_name": self.full_name,
            "is_supported": self.is_supported(),
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert current release into a dict.

        Returns:
            dict: A dictionary representation of the software release, including its label, release date, and OS information.
        """

        return {
            "label": self.label,
            "release_date": TimeConverter.date_to_str(self._release_date),
            **self._software_dict(),
            "support": ", ".join(list(map(str, self.support))),
        }


class SoftwareReleaseDict(Generic[ReleaseType]):
    """Software release dictionary."""

    # ****************************************************************
    # Constructor & Attributes

    def __init__(self, **kwargs: "ReleaseType") -> None:
        """
        Create a new instance of SoftwareReleaseDict.
        """

        self._data: dict[str, "ReleaseType"] = {}

        if len(kwargs) > 0:
            self._data.update({ k: v for k, v in kwargs.items() })

    # ****************************************************************
    # Methods

    def __getitem__(self, key: str) -> "ReleaseType":
        """
        Return a SoftwareReleaseBound element based on its key.

        Args:
            key (str): the key of the item to return

        Returns:
            ReleaseType: covariant element of SoftwareRelease
        """

        return self._data[key]

    def __setitem__(self, key: str, value: "ReleaseType") -> None:
        """
        Set the SoftwareRelease in the dictionary for the provided key.

        Args:
            key (str)          : New element key
            value (ReleaseType): Value of the new element
        """

        self._data[key] = value

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator to go through the SoftwareReleases.

        Returns:
            Iterator[str]: iterator object
        """

        return iter(self._data)

    def get(self, key: str, default_value: Any = None) -> "ReleaseType | None":
        """
        Return a SoftwareReleaseBound element based on its key.

        If the element cannot be found, return the default value.

        Args:
            key (str)          : key of the element to return
            default_value (Any): default value in case the element cannot be found

        Returns:
            SoftwareReleaseBound | None: element associated with provided key or default value

        """

        return self._data.get(key, default_value)

    def keys(self):
        """
        Return the keys of the data dict.

        Returns:
            dict_keys[str, SoftwareReleaseBound_co]: the keys of the current dictionary
        """

        return self._data.keys()

    def values(self):
        """
        Return the values of the data dict.

        Returns:
            dict_values[str, SoftwareReleaseBound_co]: the values of the current dictionary
        """

        return self._data.values()

    def items(self):
        """
        Return the items of the data dict.

        Returns:
            dict_items[str, SoftwareReleaseBound_co]: the items of the current dictionary
        """

        return self._data.items()

    def find(self, rel_ver: str, rel_label: str | None = None) -> "ReleaseType | None":
        """
        Find the given release.

        This method searches through the dictionary to locate a specific software release by version and optionally by label.
        It returns either the entire release information if only the version is specified, or it narrows down the search to a specific label within that version if both are provided.

        Args:
            rel_ver (str)         : The version of the software release to find.
            rel_label (str | None): The label associated with the release. Defaults to None.

        Returns:
            SoftwareReleaseDict: A dictionary containing either the entire release information or a specific label's information based on the provided criteria.
        """

        label_key = f" - {rel_label}"
        key = f"{rel_ver}{label_key if rel_label else ''}"

        return self.get(key, None)

    def filter_by_str(self, search_str: str) -> "SoftwareReleaseDict[ReleaseType]":
        """
        Search for elements with a key matching the provided search string.

        Args:
            search_str (str): search string to compare to the keys in the current dictionary

        Returns:
            list[SoftwareReleaseBound]: list of elements found
        """

        return SoftwareReleaseDict[ReleaseType](
            **{rel_k: rel for rel_k, rel in self.items() if search_str in rel_k}
        )

    def filter_by_version(self, version: str) -> "SoftwareReleaseDict[ReleaseType]":
        """
        Filter the content of the current release dictionary by release version.

        Args:
            version (str): String representation of a release version to filter

        Returns:
            SoftwareReleaseDict: a filtered version of the current dictionary
        """

        return SoftwareReleaseDict[ReleaseType](
            **{rel_k: rel for rel_k, rel in self.items() if str(rel.version) == version}
        )


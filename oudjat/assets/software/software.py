"""Main module of the software package that defines the notion of software."""

from datetime import datetime
from enum import IntEnum
from typing import Any, override

from oudjat.assets.software.software_release_version import SoftwareReleaseVersion
from oudjat.utils.time_utils import TimeConverter

from ..asset import Asset
from ..asset_type import AssetType
from .software_edition import SoftwareEdition, SoftwareEditionDict
from .software_support import SoftwareReleaseSupport, SoftwareReleaseSupportList


class SoftwareRelease:
    """A class to describe software releases."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        software: "Software",
        version: int | str,
        release_date: str | datetime,
        release_label: str,
    ) -> None:
        """
        Create a new instance of SoftwareRelease.

        Args:
            software (Software)          : The software instance to which this release belongs.
            version (int | str)          : The version of the software, can be either an integer or a string representation of a number.
            release_date (str | datetime): The date when the software was released. Can be provided as a string formatted according to `%Y-%m-%d`
                                                or as a datetime object. If provided as a string, it will be parsed using the format specified by DateStrFlag.YMD.
            release_label (str)          : A label describing the nature of this release, such as "stable" or "beta".

        Raises:
            ValueError: If `release_date` is provided as a string and does not match the expected date format.
        """

        # TODO: fully implement SoftwareReleaseVersion
        self._software: "Software" = software
        self._version: SoftwareReleaseVersion = SoftwareReleaseVersion(version)
        self._label: str = release_label

        try:
            if not isinstance(release_date, datetime):
                release_date = TimeConverter.str_to_date(release_date)

        except ValueError as e:
            raise ValueError(
                f"{__class__.__name__}::Please provide dates with %Y-%m-%d format\n{e}"
            )

        self._release_date: datetime = release_date
        self._support: SoftwareReleaseSupportList = SoftwareReleaseSupportList()

        # NOTE: maybe convert vulnerabilities into a dictionary (CVE instances ?) if needed
        self._vulnerabilities: set[str] = set()

    # ****************************************************************
    # Methods

    @property
    def software(self) -> "Software":
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
    def name(self) -> None:
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
    def full_name(self) -> str:
        """
        Return the release full name.

        Returns:name
            str: The full name of the software release, combining the software name and its label.
        """

        return f"{self.software.name} {self.label}"

    @property
    def vulnerabilities(self) -> set[str]:
        """
        Return the vulnerabilies this software is concerned with.

        Returns:
            set[str]: a set of unique vulnerabilities
        """

        return self._vulnerabilities

    def is_supported(self, edition: str | list[str] | None = None) -> bool:
        """
        Check if the current release has an ongoing support.

        Args:
            edition (str | list[str], optional): The specific edition to check for support. Defaults to None.

        Returns:
            bool: True if the release is supported, otherwise False.
        """

        return any(
            [
                s.is_ongoing() and (edition is None or s.supports_edition(edition))
                for s in self._support
            ]
        )

    def get_support_for_edition(
        self, edition: str | list[str], lts: bool = False
    ) -> "SoftwareReleaseSupportList":
        """
        Return support for given edition.

        Args:
            edition (str | list[str]): The specific edition to retrieve support for.
            lts (bool, optional)     : Whether to filter for LTS (Long Term Support) editions. Defaults to False.

        Returns:
            SoftwareReleaseSupportList : The list of support details filtered by the specified edition or LTS status.
        """

        return SoftwareReleaseSupportList(*self._support.get(edition, lts=lts))

    def get_ongoing_support(self) -> list[SoftwareReleaseSupport]:
        """
        Return ongoing support instances.

        Returns:
            list[SoftwareReleaseSupport]: A list of support details that are currently ongoing.
        """

        return [s for s in self._support if s.is_ongoing()]

    def get_retired_support(self) -> list[SoftwareReleaseSupport]:
        """
        Return retired support instances.

        Returns:
            list[SoftwareReleaseSupport]: A list of support details that are no longer ongoing.
        """

        return [s for s in self._support if not s.is_ongoing()]


    def add_support(self, support: SoftwareReleaseSupport) -> None:
        """
        Add a support instance to the current release.

        Args:
            support (SoftwareReleaseSupport): The support instance to be added.

        Returns:
            None
        """

        if not self._support.contains(
            edition=list(support.get_edition().keys()), lts=support.has_long_term_support()
        ):
            self._support.append(support)

    def has_vulnerability(self, vuln: str | list[str] | None = None) -> list[str]:
        """
        Check if the release is concerned by any or specific vulnerability.

        Args:
            vuln (str | list[str], optional): The vulnerability to check. Can be a single string or a list of strings. Defaults to None.

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
            show_version (bool, optional): Whether to include the version in the string representation. Defaults to False.

        Returns:
            str: A string representation of the software release, optionally including the version.
        """

        name = self.full_name

        if show_version:
            name = f"{name.strip()}({self._version})"

        return name.strip()

    def software_dict(self) -> dict[str, Any]:
        """
        Return a dictionary with OS infos.

        Returns:
            dict: A dictionary containing innamen about the operating system, including software name, release name, version, full name, and support status.
        """

        return {
            "software": self.software.name,
            "name": self.name,
            "version": self.version,
            "full_name": self.full_name,
            "is_supported": self.is_supported(),
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert current release into a dict.

        Returns:
            dict: A dictionary representation of the software release, including its label, release date, and OS information.
        """

        # TODO: add version dictionary and rename keys
        # version_dict = self.version.to_dict()

        return {
            "label": self.label,
            "release_date": TimeConverter.date_to_str(self._release_date),
            **self.software_dict(),
            "support": ", ".join(list(map(str, self.support))),
        }


class SoftwareReleaseDict(dict[str, Any]):
    """Software release dictionary."""

    # ****************************************************************
    # Methods

    def find_release_per_label(self, release_label: str) -> "SoftwareReleaseDict":
        """
        Try to find release with a label matching the given string.

        This method searches through the dictionary and returns a new dictionary containing only those key-value pairs where the keys match the provided string `val`.
        The resulting dictionary is of type SoftwareReleaseDict, preserving the structure of the original dictionary for potential further processing.

        Args:
            release_label (str): The string to search for in the dictionary keys.

        Returns:
            SoftwareReleaseDict: A new dictionary containing only the key-value pairs where the keys match `val`.
        """

        return SoftwareReleaseDict(**{k: v for k, v in self.items() if k in release_label})

    def find_release(self, rel_ver: str, rel_label: str | None = None) -> SoftwareRelease | None:
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

        res = None
        if rel_ver in self.keys():
            search: SoftwareReleaseDict = self.get(rel_ver, SoftwareReleaseDict())

            res = (
                search.get(rel_label, None)
                if rel_label is not None
                else search.get(list(search.keys())[0], None)
            )

        return res


class SoftwareType(IntEnum):
    """An enumeration to list software types."""

    OS = 0
    APPLICATION = 1


class Software(Asset):
    """A class to describe softwares."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        software_id: int | str,
        name: str,
        label: str,
        software_type: SoftwareType = SoftwareType.APPLICATION,
        editor: str | list[str] | None = None,
        description: str | None = None,
    ) -> None:
        """
        Initialize a new instance of the Software class.

        This constructor sets up the basic attributes for a software asset, including its identifier, name, label, type,
        editor(s), and optional description. The software type defaults to an application unless specified otherwise.

        Args:
            software_id (int | str)               : A unique identifier for the software, which can be either an integer or a string.
            name (str)                            : The name of the software.
            label (str)                           : A brief label that describes the software.
            software_type (SoftwareType, optional): Specifies the type of the software. Defaults to SoftwareType.APPLICATION.
            editor (str | list[str], optional)    : The editor(s) responsible for the development or maintenance of the software
            description (str, optional)           : A detailed description of the software. Defaults to None.
        """

        super().__init__(
            asset_id=software_id,
            name=name,
            label=label,
            asset_type=AssetType.SOFTWARE,
            description=description,
        )

        if editor is not None and not isinstance(editor, list):
            editor = [editor]

        self._editor: list[str] | None = editor
        self._type: SoftwareType = software_type
        self._releases: "SoftwareReleaseDict" = SoftwareReleaseDict()
        self._editions: SoftwareEditionDict = SoftwareEditionDict()

    # ****************************************************************
    # Methods

    @property
    def editor(self) -> list[str] | None:
        """
        Return software editor.

        Returns:
            str: software editor's name
        """

        return self._editor

    @editor.setter
    def set_editor(self, editor: list[str]) -> None:
        """
        Setter for software editor.

        Args:
            editor (str | list[str]): The new editor to be assigned to the software instance. Can be a single string or a list of strings.
        """

        self._editor = editor

    @property
    def releases(self) -> SoftwareReleaseDict:
        """
        Return the releases of this software.

        Returns:
            SoftwareReleaseDict: A dictionary containing all the software releases associated with this instance.
        """

        return self._releases

    @property
    def type(self) -> SoftwareType:
        """
        Getter for software type.

        Returns:
            SoftwareType: The type of the software as specified during initialization or defaulted to Application.
        """

        return self._type

    @property
    def editions(self) -> SoftwareEditionDict:
        """
        Return the editions this software can have.

        Returns:
            SoftwareEditionDict: A dictionary containing all the software editions associated with this instance.
        """

        return self._editions


    def has_release(self, rel_ver: str, rel_label: str) -> bool:
        """
        Check if the current software has a release with the given version and label.

        Args:
            rel_ver (str)   : The version of the release to check for.
            rel_label (str) : The label of the release to check for.

        Returns:
            bool: True if a matching release is found, otherwise False.
        """

        return self.releases.find_release(rel_ver, rel_label) is not None

    def add_release(self, new_release: "SoftwareRelease") -> None:
        """
        Add a release to the list of software releases.

        Args:
            new_release (SoftwareRelease): The release object to be added.

        Note:
            This method does not allow adding non-SoftwareRelease objects and returns silently if so.
        """

        new_rel_ver: SoftwareReleaseVersion = new_release.version
        if str(new_rel_ver) not in self.releases.keys():
            self.releases[str(new_rel_ver)] = SoftwareReleaseDict()

        new_rel_label: str = new_release.label
        if new_rel_label not in self.releases[str(new_rel_ver)].keys():
            self.releases[str(new_rel_ver)][new_rel_label] = new_release

    def find_release(self, rel_ver: str, rel_label: str | None = None) -> "SoftwareRelease | None":
        """
        Find a release by its version and optionally label.

        Args:
            rel_ver (str): The version of the release to search for.
            rel_label (str, optional): The label of the release to search for. Defaults to None.

        Returns:
            SoftwareRelease: The found release object or None if not found.
        """

        return self.releases.find_release(rel_ver, rel_label)

    def retired_releases(self) -> list["SoftwareRelease"]:
        """
        Get a list of retired releases.

        Returns:
            list[SoftwareRelease]: A list of SoftwareRelease objects that are not supported.
        """

        return [r for r in self.releases.values() if not r.is_supported()]

    def supported_releases(self) -> list["SoftwareRelease"]:
        """
        Get a list of released that are currently supported.

        Returns:
            list[SoftwareRelease]: A list of SoftwareRelease objects that are supported.
        """

        return [r for r in self.releases.values() if r.is_supported()]

    def get_matching_editions(self, test_str: str) -> list[SoftwareEdition]:
        """
        Return the editions which pattern matches the given string.

        Args:
            test_str (str): The string to match against edition names or other patterns.

        Returns:
            SoftwareEditionDict: A dictionary containing matching editions.
        """

        return self.editions.get_matching_editions(test_str)

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: current software instance represented as a string

        Example:
            soft: Software = Software(...)
            print(soft)
        """

        return self._name

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary representation.

        Returns:
            dict: A dictionary containing basic class information and lists of releases.
        """

        base_dict = super().to_dict()
        return {
            **base_dict,
            "editor": self.editor,
            "releases": ",".join(map(str, self.releases)),
            "supported_releases": ",".join(list(map(str, self.supported_releases()))),
            "retired_releases": ",".join(list(map(str, self.retired_releases()))),
        }

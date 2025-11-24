"""Main module of the software package that defines the notion of software."""

from enum import IntEnum
from typing import Any, Generic, override

from ..asset import Asset
from ..asset_type import AssetType
from .software_edition import SoftwareEdition, SoftwareEditionDict
from .software_release import ReleaseType, SoftwareReleaseDict


class SoftwareType(IntEnum):
    """An enumeration to list software types."""

    OS = 0
    APPLICATION = 1


class Software(Asset, Generic[ReleaseType]):
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
            software_id (int | str)            : A unique identifier for the software, which can be either an integer or a string.
            name (str)                         : The name of the software.
            label (str)                        : A brief label that describes the software.
            software_type (SoftwareType | None): Specifies the type of the software. Defaults to SoftwareType.APPLICATION.
            editor (str | list[str] | None)    : The editor(s) responsible for the development or maintenance of the software
            description (str | None)           : A detailed description of the software. Defaults to None.
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
        self._type: "SoftwareType" = software_type
        self._releases: "SoftwareReleaseDict[ReleaseType]" = SoftwareReleaseDict[ReleaseType]()
        self._editions: "SoftwareEditionDict" = SoftwareEditionDict()

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
    def releases(self) -> SoftwareReleaseDict[ReleaseType]:
        """
        Return the releases of this software.

        Returns:
            SoftwareReleaseDict: A dictionary containing all the software releases associated with this instance.
        """

        return self._releases

    @property
    def type(self) -> "SoftwareType":
        """
        Getter for software type.

        Returns:
            SoftwareType: The type of the software as specified during initialization or defaulted to Application.
        """

        return self._type

    @property
    def editions(self) -> "SoftwareEditionDict":
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

        return self.releases.find(rel_ver, rel_label) is not None

    def add_release(self, new_release: "ReleaseType") -> None:
        """
        Add a release to the list of software releases.

        Args:
            new_release (SoftwareRelease): The release object to be added.

        Note:
            This method does not allow adding non-SoftwareRelease objects and returns silently if so.
        """

        if new_release.key not in self.releases.keys():
            self.releases[new_release.key] = new_release

    def find_release(self, rel_ver: str, rel_label: str | None = None) -> "ReleaseType | None":
        """
        Find a release by its version and optionally label.

        Args:
            rel_ver (str): The version of the release to search for.
            rel_label (str | None): The label of the release to search for. Defaults to None.

        Returns:
            ReleaseType: The found release object or None if not found.
        """

        return self.releases.find(rel_ver, rel_label)

    def retired_releases(self) -> list["ReleaseType"]:
        """
        Get a list of retired releases.

        Returns:
            list[SoftwareRelease]: A list of SoftwareRelease objects that are not supported.
        """

        return [r for r in self.releases.values() if not r.is_supported()]

    def supported_releases(self) -> list["ReleaseType"]:
        """
        Get a list of released that are currently supported.

        Returns:
            list[SoftwareRelease]: A list of SoftwareRelease objects that are supported.
        """

        return [r for r in self.releases.values() if r.is_supported()]

    def matching_editions(self, test_str: str) -> list["SoftwareEdition"]:
        """
        Return the editions which pattern matches the given string.

        Args:
            test_str (str): The string to match against edition names or other patterns.

        Returns:
            SoftwareEditionDict: A dictionary containing matching editions.
        """

        return self.editions.find_by_label(test_str)

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

        base_dict: dict[str, Any] = super().to_dict()
        return {
            **base_dict,
            "editor": self.editor,
            "releases": {r.key: r.to_dict() for r in self._releases.values()},
        }

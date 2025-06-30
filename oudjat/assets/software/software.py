"""Main module of the software package that defines the notion of software."""

from enum import IntEnum
from typing import Any, Dict, List, Union

from ..asset import Asset
from ..asset_type import AssetType
from .software_edition import SoftwareEditionDict
from .software_release import SoftwareRelease, SoftwareReleaseDict


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
        software_id: Union[int, str],
        name: str,
        label: str,
        software_type: SoftwareType = SoftwareType.APPLICATION,
        editor: Union[str, List[str]] = None,
        description: str = None,
    ) -> None:
        """
        Initialize a new instance of the Software class.

        This constructor sets up the basic attributes for a software asset, including its identifier, name, label, type,
        editor(s), and optional description. The software type defaults to an application unless specified otherwise.

        Args:
            software_id (Union[int, str])           : A unique identifier for the software, which can be either an integer or a string.
            name (str)                              : The name of the software.
            label (str)                             : A brief label that describes the software.
            software_type (SoftwareType, optional)  : Specifies the type of the software. Defaults to SoftwareType.APPLICATION.
            editor (Union[str, List[str]], optional): The editor(s) responsible for the development or maintenance of the software
            description (str, optional)             : A detailed description of the software. Defaults to None.
        """

        super().__init__(
            asset_id=software_id,
            name=name,
            label=label,
            asset_type=AssetType.SOFTWARE,
            description=description,
        )

        self.editor = editor
        self.type = software_type
        self.releases = SoftwareReleaseDict()
        self.editions = SoftwareEditionDict()

    # ****************************************************************
    # Methods

    def get_editor(self) -> str:
        """
        Return software editor.

        Returns:
            str: software editor's name
        """

        return self.editor

    def get_releases(self) -> SoftwareReleaseDict:
        """
        Getter for software releases.

        Returns:
            SoftwareReleaseDict: A dictionary containing all the software releases associated with this instance.
        """

        return self.releases

    def get_software_type(self) -> SoftwareType:
        """
        Getter for software type.

        Returns:
            SoftwareType: The type of the software as specified during initialization or defaulted to Application.
        """

        return self.type

    def get_editions(self) -> SoftwareEditionDict:
        """
        Getter for software editions.

        Returns:
            SoftwareEditionDict: A dictionary containing all the software editions associated with this instance.
        """

        return self.editions

    def set_editor(self, editor: Union[str, List[str]]) -> None:
        """
        Setter for software editor.

        Args:
            editor (Union[str, List[str]]): The new editor to be assigned to the software instance. Can be a single string or a list of strings.
        """

        self.editor = editor

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

    def add_release(self, new_release: SoftwareRelease) -> None:
        """
        Add a release to the list of software releases.

        Args:
            new_release (SoftwareRelease): The release object to be added.

        Note:
            This method does not allow adding non-SoftwareRelease objects and returns silently if so.
        """

        if not isinstance(new_release, SoftwareRelease):
            return

        new_rel_ver = new_release.get_version()
        if new_rel_ver not in self.releases.keys():
            self.releases[new_rel_ver] = SoftwareReleaseDict()

        new_rel_label = new_release.get_label()
        if new_rel_label not in self.releases[new_rel_ver].keys():
            self.releases[new_rel_ver][new_release.get_label()] = new_release

    def find_release(self, rel_ver: str, rel_label: str = None) -> SoftwareRelease:
        """
        Find a release by its version and optionally label.

        Args:
            rel_ver (str): The version of the release to search for.
            rel_label (str, optional): The label of the release to search for. Defaults to None.

        Returns:
            SoftwareRelease: The found release object or None if not found.
        """

        return self.releases.find_release(rel_ver, rel_label)

    def retired_releases(self) -> List[SoftwareRelease]:
        """
        Get a list of retired releases.

        Returns:
            List[SoftwareRelease]: A list of SoftwareRelease objects that are not supported.
        """

        return [str(r) for r in self.releases.values() if not r.is_supported()]

    def supported_releases(self) -> List[SoftwareRelease]:
        """
        Get a list of released that are currently supported.

        Returns:
            List[SoftwareRelease]: A list of SoftwareRelease objects that are supported.
        """

        return [str(r) for r in self.releases.values() if r.is_supported()]

    def get_matching_editions(self, test_str: str) -> SoftwareEditionDict:
        """
        Return the editions which pattern matches the given string.

        Args:
            test_str (str): The string to match against edition names or other patterns.

        Returns:
            SoftwareEditionDict: A dictionary containing matching editions.
        """

        return self.editions.get_matching_editions(test_str)

    def __str__(self):
        """
        Convert the current instance into a string.

        Returns:
            str: current software instance represented as a string

        Example:
            soft: Software = Software(...)
            print(soft)
        """

        return self.name

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the current instance into a dictionary representation.

        Returns:
            Dict: A dictionary containing basic class information and lists of releases.
        """

        base_dict = super().to_dict()
        return {
            **base_dict,
            "editor": self.editor,
            "releases": ",".join(map(str, self.releases)),
            "supported_releases": ",".join(self.supported_releases()),
            "retired_releases": ",".join(self.retired_releases()),
        }

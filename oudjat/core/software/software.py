"""Main module of the software package that defines the notion of software."""

import re
from enum import IntEnum
from typing import Any, Generic, override

from oudjat.core.software.definitions import VERSION_REG
from oudjat.core.software.exceptions import UnknownSoftwareReleaseVersionError
from oudjat.utils import Context

from ..asset import Asset
from ..asset_type import AssetType
from .software_edition import SoftwareEdition, SoftwareEditionDict
from .software_release import (
    ReleaseType,
    SoftwareReleaseList,
    SoftwareRelVersionDict,
)


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
        editions: "SoftwareEditionDict | None" = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the Software class.

        This constructor sets up the basic attributes for a software asset, including its identifier, name, label, type,
        editor(s), and optional description. The software type defaults to an application unless specified otherwise.

        Args:
            software_id (int | str)                               : A unique identifier for the software, which can be either an integer or a string.
            name (str)                                            : The name of the software.
            label (str)                                           : A brief label that describes the software.
            software_type (SoftwareType | None)                   : Specifies the type of the software. Defaults to SoftwareType.APPLICATION.
            editor (str | list[str] | None)                       : The editor(s) responsible for the development or maintenance of the software
            description (str | None)                              : A detailed description of the software. Defaults to None.
            releases (dict[str, list[GenericSoftwareReleaseDict]]): A dictionary of software releases dictionaries used to generate the software releases
            editions (SoftwareEditionDict | None)                 : A dictionary of the software editions
            **kwargs (Any)                                        : Any additional arguments that will be passed to parent class
        """

        super().__init__(
            asset_id=software_id,
            name=name,
            label=label,
            asset_type=AssetType.SOFTWARE,
            description=description,
            **kwargs,
        )

        if editor is not None and not isinstance(editor, list):
            editor = [editor]

        self._editor: list[str] | None = editor
        self._type: "SoftwareType" = software_type
        self._releases: "SoftwareRelVersionDict[ReleaseType]" = SoftwareRelVersionDict[
            ReleaseType
        ]()

        self._editions: "SoftwareEditionDict" = SoftwareEditionDict()

        if editions is not None:
            self._editions = editions

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
    def releases(self) -> "SoftwareRelVersionDict[ReleaseType]":
        """
        Return the releases of this software.

        Returns:
            SoftwareReleaseDict: A dictionary containing all the software releases associated with this instance.
        """

        return self._releases

    @releases.setter
    def releases(self, new_releases: "SoftwareRelVersionDict[ReleaseType]") -> None:
        """
        Set the releases for this software.

        Args:
            new_releases (SoftwareReleaseDict): New releases value
        """

        self._releases = new_releases

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

    def release(self, key: str) -> "ReleaseType | SoftwareReleaseList[ReleaseType]":
        """
        Return the releases matching the provided key.

        Args:
            key (str): The key of the sought release

        Returns:
            SoftwareReleaseList: A custom list of SoftwareRelease that can be narrowed down using its custom methods
        """

        candidates = self._releases.get(key)

        if candidates is None:
            raise UnknownSoftwareReleaseVersionError(
                f"{Context()}::{self.name} does not have any release matching the provided key {key}"
            )

        return candidates[0] if len(candidates) == 1 else candidates

    def has_release(self, rel_ver: str) -> bool:
        """
        Check if the current software has a release with the given version and label.

        Args:
            rel_ver (str)  : The version of the release to check for.
            rel_label (str): The label of the release to check for.

        Returns:
            bool: True if a matching release is found, otherwise False.
        """

        return rel_ver in self.releases.keys()

    def add_release(self, new_release: "ReleaseType", force: bool = False) -> None:
        """
        Add a release to the list of software releases.

        Args:
            new_release (SoftwareRelease): The release object to be added
            force (bool)                 : Whether to force the addition of the new release
        """

        self._releases.add(str(new_release.version), new_release, force=force)

    def retired_releases(self) -> "SoftwareReleaseList[ReleaseType]":
        """
        Get a list of retired releases.

        Returns:
            list[SoftwareRelease]: A list of SoftwareRelease objects that are not supported.
        """

        res: "SoftwareReleaseList[ReleaseType]" = SoftwareReleaseList()
        for r in self._releases.values():
            res.extend(r.filter_by_status(False))

        return res

    def supported_releases(self) -> "SoftwareReleaseList[ReleaseType]":
        """
        Get a list of released that are currently supported.

        Returns:
            list[SoftwareRelease]: A list of SoftwareRelease objects that are supported.
        """

        res: "SoftwareReleaseList[ReleaseType]" = SoftwareReleaseList()
        for r in self._releases.values():
            res.extend(r.filter_by_status())

        return res

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
            "releases": self._releases.to_dict(),
        }

    # ****************************************************************
    # Static methods

    @staticmethod
    def find_version_in_str(search_str: str) -> str | None:
        """
        Try to find a version in the provided string based on the class VERSION_REG.

        This static method uses a regular expression to find and return a version number from the input string.

        Args:
            search_str (str): The string to search for a version match.

        Returns:
            str: A string representing the matched version, or None if no match is found.
        """

        search = re.search(VERSION_REG, search_str)
        return search.group(0) if search is not None else None

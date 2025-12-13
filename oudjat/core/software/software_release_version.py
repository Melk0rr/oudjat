"""Module to describe software release versions."""

import re
from enum import Enum
from typing import Any, override

from oudjat.core.software.exceptions import (
    InvalidSoftwareVersionError,
)
from oudjat.utils import Context

from .definitions import STAGE_REG, VERSION_REG


# TODO: Improve stage handling: allow more freedom in stage inicator ?
class SoftwareReleaseStage(Enum):
    """
    An enumeration of software release stages.

    Along with major, minor and build version, a software version comes with a stage of development
    """

    ALPHA = "a"
    BETA = "b"
    SERVICE_PACK = "sp"
    RELEASE_CANDIDATE = "rc"
    RELEASE = ""

    @override
    def __str__(self) -> str:
        """
        Convert the SoftwareReleaseStage into a string.

        Returns:
            str: A string representation of the software release stage
        """

        return self._value_


class SoftwareReleaseVersion:
    """
    A class that describe and handle software release version.

    The class handles version stage and version semantic parts major, minor and build.
    """

    def __init__(
        self,
        version: int | str,
        stage: tuple["SoftwareReleaseStage", int] = (SoftwareReleaseStage.RELEASE, 1),
    ) -> None:
        """
        Create a new instance of SoftwareReleaseVersion.

        Args:
            version (int | str): initial version to set
            stage (tuple[SoftwareReleaseStage, int]): a tuple representing stage and stage version

        Returns:
            type and description of the returned object.

        Example:
            # Description of my example.
            use_it_this_way(arg1, arg2)
        """
        self._major: int = 0
        self._minor: int = 0
        self._build: int = 0

        self._stage: "SoftwareReleaseStage" = stage[0]
        self._stage_version: int = stage[1]
        self._raw: int | str = version

        if isinstance(version, int):
            self._major = version

        else:
            match = re.match(VERSION_REG, version)

            if match is None:
                raise InvalidSoftwareVersionError(
                    f"{Context()}::Invalid version provided {version}"
                )

            self._major = int(match.group(1))
            self._minor = int(match.group(2))
            self._build = int(match.group(3))

            if match.group(4) is not None:
                stage_match = re.match(STAGE_REG, match.group(4))

                if stage_match:
                    self._stage = SoftwareReleaseStage(stage_match.group(1))
                    self._stage_version = int(stage_match.group(2))

    @property
    def major(self) -> int:
        """
        Return the major version number.

        Returns:
            int: major version number (default 0)
        """

        return self._major

    @major.setter
    def major(self, new_major: int) -> None:
        """
        Set the major version number of the current SoftwareReleaseVersion.

        Args:
            new_major (int): new major version value
        """

        self._major = new_major

    @property
    def minor(self) -> int:
        """
        Return the minor version number.

        Returns:
            int: minor version number (default 0)
        """

        return self._minor

    @minor.setter
    def minor(self, new_minor: int) -> None:
        """
        Set the minor version number of the current SoftwareReleaseVersion.

        Args:
            new_minor (int): new minor version value
        """

        self._minor = new_minor

    @property
    def build(self) -> int:
        """
        Return the build version number.

        Returns:
            int: build version number (default 0)
        """

        return self._build

    @build.setter
    def build(self, new_build: int) -> None:
        """
        Set the build version number of the current SoftwareReleaseVersion.

        Args:
            new_build (int): new build version value
        """

        self._build = new_build

    @property
    def raw(self) -> int | str:
        """
        Return the raw version value.

        Returns:
            int | str: raw version value
        """

        return self._raw

    @property
    def stage(self) -> tuple["SoftwareReleaseStage", int]:
        """
        Return the stage version number.

        Returns:
            tuple[SoftwareReleaseStage, int]: stage version number (default 0)
        """

        return (self._stage, self._stage_version)

    @stage.setter
    def stage(self, new_stage: tuple["SoftwareReleaseStage", int]) -> None:
        """
        Set the stage version number of the current SoftwareReleaseVersion.

        Args:
            new_stage (tuple[SoftwareReleaseStage, int]): new stage version value
        """

        self._stage, self._stage_version = new_stage

    def __gt__(self, other: "SoftwareReleaseVersion") -> bool:
        """
        Check if current version is above the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is above the other. False otherwise
        """

        return self.major >= other.major and self.minor >= other.minor and self.build > other.build

    def __ge__(self, other: "SoftwareReleaseVersion") -> bool:
        """
        Check if current version is equal or above the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is above or equal to the other. False otherwise
        """

        return self.major >= other.major and self.minor >= other.minor and self.build >= other.build

    def __lt__(self, other: "SoftwareReleaseVersion") -> bool:
        """
        Check if current version is below the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is below the other. False otherwise
        """

        return self.major <= other.major and self.minor <= other.minor and self.build < other.build

    def __le__(self, other: "SoftwareReleaseVersion") -> bool:
        """
        Check if current version is equal or above the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is lower or equal to the other. False otherwise
        """

        return self.major <= other.major and self.minor <= other.minor and self.build <= other.build

    @override
    def __eq__(self, other: object) -> bool:
        """
        Check if current version is equal or above the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is lower or equal to the other. False otherwise
        """

        if not isinstance(other, SoftwareReleaseVersion):
            raise ValueError(
                f"{Context()}::You are trying to compare a SoftwareReleaseVersion with {type(object)}"
            )

        return self.major == other.major and self.minor == other.minor and self.build == other.build

    @override
    def __hash__(self) -> int:
        """
        Generate a hash for the current version.

        Returns:
            int: Hash based on the version numbers
        """

        return hash((self._major, self._minor, self._build))

    @override
    def __str__(self) -> str:
        """
        Convert the current SoftwareReleaseVersion into a string.

        Returns:
            str: a string representing the current software release version
        """

        return f"{self._major}.{self._minor}.{self._build}{self._stage}{self._stage_version if self._stage is not SoftwareReleaseStage.RELEASE else ''}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current software release version into a dictionary.

        Returns:
            dict[str, int | str]: a dictionary representing the current instance
        """

        return {
            "raw": self._raw,
            "major": self._major,
            "minor": self._minor,
            "build": self._build,
            "stage": {
                "name": self._stage.name,
                "version": self._stage_version,
                "value": f"{self._stage}{self._stage_version}",
            },
        }

"""Module to describe software release versions."""

from enum import Enum
from typing import override


class SoftwareReleaseStage(Enum):
    """
    An enumeration of software release stages.

    Along with major, minor and build version, a software version comes with a stage of development
    """

    ALPHA = "a"
    BETA = "b"
    RELEASE_CANDIDATE = "rc"
    RELEASE = ""


class SoftwareReleaseVersion:
    """
    A class that describe and handle software release version.

    The class handles version stage and version semantic parts major, minor and build.
    """

    def __init__(
        self,
        version: int | str,
        stage: tuple[SoftwareReleaseStage, int] = (SoftwareReleaseStage.RELEASE, 1),
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

        if isinstance(version, int):
            self._major = version

        else:
            self._major, self._minor, self._build = map(int, version.split("."))

        self._stage: SoftwareReleaseStage = stage[0]
        self._stage_version: int = stage[1]

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
    def stage(self) -> tuple[SoftwareReleaseStage, int]:
        """
        Return the stage version number.

        Returns:
            tuple[SoftwareReleaseStage, int]: stage version number (default 0)
        """

        return (self._stage, self._stage_version)

    @stage.setter
    def stage(self, new_stage: tuple[SoftwareReleaseStage, int]) -> None:
        """
        Set the stage version number of the current SoftwareReleaseVersion.

        Args:
            new_stage (tuple[SoftwareReleaseStage, int]): new stage version value
        """

        self._stage, self._stage_version = new_stage

    @override
    def __str__(self) -> str:
        """
        Convert the current SoftwareReleaseVersion into a string.

        Returns:
            str: a string representing the current software release version
        """

        return f"{self._major}.{self._minor}.{self._build}{self._stage}{self._stage_version if self._stage is not SoftwareReleaseStage.RELEASE else ''}"

    def to_dict(self) -> dict[str, int | str]:
        """
        Convert the current software release version into a dictionary.

        Returns:
            dict[str, int | str]: a dictionary representing the current instance
        """

        return {
            "major": self._major,
            "minor": self._minor,
            "build": self._build,
            "stage": f"{self._stage}{self._stage_version}",
        }
